"""Expose pinned upstream skills under distinct names without modifying their sources."""

import json
import re
import sys
from pathlib import Path

MARKER = "<!-- Managed by dotfiles-exedev agent-skills. -->"


def description_from(frontmatter: str) -> str:
    """Read the upstream description, including its known unquoted colon typo."""
    match = re.search(r"^description: *(.*(?:\n[ \t]+[^\n]+)*)", frontmatter, re.M)
    if not match:
        raise ValueError("Missing skill description")
    value = match[1].strip()
    if value.startswith('"'):
        return json.loads(value)
    if value.startswith("'"):
        return value[1:-1].replace("''", "'")
    if value.splitlines()[0] in ("|", "|-", ">", ">-"):
        return " ".join(line.strip() for line in value.splitlines()[1:])
    return value


def entry_point(source: Path, root: Path, namespace: str) -> tuple[str, str]:
    """Build a namespaced entry point that resolves resources at their original paths."""
    text = source.read_text()
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError(f"Missing frontmatter: {source}")
    frontmatter = text[4:].split("\n---\n", 1)[0]
    slug = source.parent.name
    name = f"{namespace}-{slug}"
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise ValueError(f"Invalid skill name: {name}")
    description = description_from(frontmatter)
    explicit_only = bool(
        re.search(r"^disable-model-invocation: true\s*$", frontmatter, re.M)
    )
    # Shelley ignores this YAML flag, so carry the restriction in its discovery text too.
    if explicit_only:
        description = f"Use only when explicitly requested by the user. {description}"
    header = f"---\nname: {name}\ndescription: {json.dumps(description)}\n"
    if explicit_only:
        header += "disable-model-invocation: true\n"
    body = f"""---

{MARKER}

Read `{source}` and follow that skill's instructions.
Resolve its relative files and `$SKILLBASE` from `{source.parent}`, not this entry point.
The complete upstream source is at `{root}`.
Other skills from this source use the `{namespace}-` prefix in this installation.

Use the host's available tools and models. Report unsupported host-specific steps
rather than claiming they ran. This installation provides skill documents, not
plugin agents, hooks, MCP servers, or Cursor services. Keep user approval
requirements and repository instructions in force.
"""
    return name, header + body


def owned_entry(path: Path) -> bool:
    """Recognize generated entries without taking ownership of user files."""
    return (
        path.is_dir()
        and not path.is_symlink()
        and {p.name for p in path.iterdir()} == {"SKILL.md"}
        and MARKER in (path / "SKILL.md").read_text()
    )


def install(home: Path, sources: list[dict[str, str]]) -> dict[str, int]:
    """Install entries and Claude aliases, preserving unrelated skills."""
    skill_dir = home / ".agents/skills"
    claude_dir = home / ".claude/skills"
    entries: dict[str, str] = {}
    counts: dict[str, int] = {}
    for source in sources:
        namespace = source["namespace"]
        root = home / ".local/share/agent-skill-sources" / namespace
        paths = sorted((root / source["skillRoot"]).rglob("SKILL.md"))
        if not paths:
            raise ValueError(f"No skills found in {root}")
        counts[namespace] = len(paths)
        for path in paths:
            name, content = entry_point(path, root, namespace)
            if name in entries:
                raise ValueError(f"Duplicate skill: {name}")
            entries[name] = content

    stale = [
        path for path in skill_dir.glob("*")
        if path.name not in entries
        and any(path.name.startswith(f"{ns}-") for ns in counts)
        and owned_entry(path)
    ]
    # Check every destination before writing, so a collision cannot leave a partial install.
    for name in [*entries, *(path.name for path in stale)]:
        target = skill_dir / name
        alias = claude_dir / name
        if (target.exists() or target.is_symlink()) and not owned_entry(target):
            raise ValueError(f"Refusing to overwrite existing skill: {target}")
        if alias.is_symlink():
            if alias.readlink() != target:
                raise ValueError(f"Refusing to replace existing link: {alias}")
        elif alias.exists():
            raise ValueError(f"Refusing to overwrite existing skill: {alias}")

    skill_dir.mkdir(parents=True, exist_ok=True)
    claude_dir.mkdir(parents=True, exist_ok=True)
    for name, content in entries.items():
        target = skill_dir / name
        target.mkdir(exist_ok=True)
        document = target / "SKILL.md"
        if not document.exists() or document.read_text() != content:
            document.write_text(content)
        alias = claude_dir / name
        if not alias.is_symlink():
            alias.symlink_to(target, target_is_directory=True)
    for target in stale:
        alias = claude_dir / target.name
        if alias.is_symlink():
            alias.unlink()
        (target / "SKILL.md").unlink()
        target.rmdir()
    return counts


if __name__ == "__main__":
    result = install(Path(sys.argv[1]), json.loads(sys.argv[2]))
    print("Installed shared skills: " + ", ".join(f"{key}={n}" for key, n in result.items()))
