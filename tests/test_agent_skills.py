"""Test skill installation without touching the user's agent configuration."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / ".chezmoitemplates/agent-skills.py"
SPEC = importlib.util.spec_from_file_location("agent_skills", MODULE)
skills = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(skills)


class AgentSkillsTests(unittest.TestCase):
    """Pin namespace, resource lookup, and ownership behavior."""

    def setUp(self):
        """Give each test a disposable home directory."""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.sources = [{"namespace": "mattpocock", "skillRoot": "skills"}]

    def source(self, slug="tdd", namespace="mattpocock", metadata=""):
        """Create a source document with a sibling resource."""
        path = (
            self.home / ".local/share/agent-skill-sources"
            / namespace / "skills" / slug / "SKILL.md"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nname: {slug}\ndescription: Test first.\n{metadata}---\n\nUse tests.md.\n"
        )
        (path.parent / "tests.md").write_text("Supporting reference.\n")
        return path

    def test_namespaces_preserve_both_versions_and_original_resources(self):
        """Identical upstream names remain independently usable with intact resources."""
        source = self.source(metadata="disable-model-invocation: true\n")
        original = source.read_bytes()
        self.source(namespace="pstack")
        self.sources.append({"namespace": "pstack", "skillRoot": "skills"})
        self.assertEqual(
            skills.install(self.home, self.sources), {"mattpocock": 1, "pstack": 1}
        )
        for name in ("mattpocock-tdd", "pstack-tdd"):
            target = self.home / ".agents/skills" / name
            text = (target / "SKILL.md").read_text()
            self.assertIn(f"name: {name}\n", text)
            self.assertEqual((self.home / ".claude/skills" / name).resolve(), target)
        wrapper = (self.home / ".agents/skills/mattpocock-tdd/SKILL.md").read_text()
        self.assertIn(str(source), wrapper)
        self.assertIn(str(source.parent), wrapper)
        self.assertIn("disable-model-invocation: true", wrapper)
        self.assertIn("Use only when explicitly requested", wrapper)
        self.assertEqual(source.read_bytes(), original)
        self.assertTrue((source.parent / "tests.md").exists())

    def test_description_formats(self):
        """Quoted, folded, and upstream's malformed plain colon descriptions are retained."""
        for raw, expected in [
            ('"Say \\"hello\\"."', 'Say "hello".'),
            ("'A user''s skill.'", "A user's skill."),
            (">-\n  Build a UI.\n  Show the result.", "Build a UI. Show the result."),
            ("Design a factory: tasks and services.", "Design a factory: tasks and services."),
        ]:
            with self.subTest(raw=raw):
                frontmatter = f"name: example\ndescription: {raw}\ndisable-model-invocation: true"
                self.assertEqual(skills.description_from(frontmatter), expected)

    def test_reapply_does_not_rewrite_unchanged_entries(self):
        """A second installation leaves unchanged files and symlinks untouched."""
        self.source()
        skills.install(self.home, self.sources)
        paths = [
            self.home / ".agents/skills/mattpocock-tdd/SKILL.md",
            self.home / ".claude/skills/mattpocock-tdd",
        ]
        before = [p.lstat().st_mtime_ns for p in paths]
        skills.install(self.home, self.sources)
        self.assertEqual([p.lstat().st_mtime_ns for p in paths], before)

    def test_collision_stops_before_any_writes(self):
        """A conflicting user-owned Claude skill prevents even earlier entries being installed."""
        self.source("aaa")
        self.source("tdd")
        existing = self.home / ".claude/skills/mattpocock-tdd"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("User-owned skill.")
        with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
            skills.install(self.home, self.sources)
        self.assertFalse((self.home / ".agents/skills").exists())
        self.assertEqual((existing / "SKILL.md").read_text(), "User-owned skill.")

    def test_existing_source_symlink_is_not_replaced(self):
        """Even a dangling link in the canonical directory is treated as user-owned."""
        self.source()
        existing = self.home / ".agents/skills/mattpocock-tdd"
        existing.parent.mkdir(parents=True)
        existing.symlink_to(self.home / "missing")
        with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
            skills.install(self.home, self.sources)
        self.assertTrue(existing.is_symlink())

    def test_stale_entries_removed_without_touching_unrelated_skills(self):
        """An upstream removal cleans only owned entries and their aliases."""
        old = self.source("old")
        self.source("keep")
        skills.install(self.home, self.sources)
        unrelated = self.home / ".agents/skills/hello"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_text("Existing skill.")
        old.unlink()
        skills.install(self.home, self.sources)
        self.assertFalse((self.home / ".agents/skills/mattpocock-old").exists())
        self.assertFalse((self.home / ".claude/skills/mattpocock-old").is_symlink())
        self.assertEqual((unrelated / "SKILL.md").read_text(), "Existing skill.")
        self.assertTrue((self.home / ".agents/skills/mattpocock-keep/SKILL.md").exists())

    def test_duplicate_names_and_empty_sources_fail(self):
        """Invalid discovery cannot overwrite entries or masquerade as an empty update."""
        with self.assertRaisesRegex(ValueError, "No skills"):
            skills.install(self.home, self.sources)
        source = self.source()
        duplicate = source.parent.parent / "nested/tdd/SKILL.md"
        duplicate.parent.mkdir(parents=True)
        duplicate.write_bytes(source.read_bytes())
        with self.assertRaisesRegex(ValueError, "Duplicate skill"):
            skills.install(self.home, self.sources)
        self.assertFalse((self.home / ".agents/skills").exists())


if __name__ == "__main__":
    unittest.main()
