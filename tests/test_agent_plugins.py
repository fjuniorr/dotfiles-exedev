"""Check native plugin configuration and installer commands without installing plugins."""

import json
import os
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render(path: str) -> str:
    """Render a managed file using the repository's actual chezmoi data."""
    return subprocess.check_output(
        ["chezmoi", "--source", str(ROOT), "execute-template", "-f", str(ROOT / path)],
        text=True,
    )


class AgentPluginTests(unittest.TestCase):
    """Keep plugin declarations, pinned archives, and native CLI calls consistent."""

    @classmethod
    def setUpClass(cls):
        """Render configuration once without applying it."""
        cls.sources = json.loads((ROOT / ".chezmoidata/agent-plugins.json").read_text())[
            "agentPlugins"
        ]
        cls.claude = json.loads(render("dot_claude/settings.json.tmpl"))
        cls.codex = tomllib.loads(render("dot_codex/config.toml.tmpl"))
        cls.externals = tomllib.loads(render(".chezmoiexternal.toml"))
        cls.script = render("run_onchange_after_install-agent-plugins.sh.tmpl")

    def run_installer(self, fail_on=""):
        """Replace both native CLIs with recorders in a disposable home."""
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            binaries = home / ".local/bin"
            binaries.mkdir(parents=True)
            for name in ("claude", "codex"):
                executable = binaries / name
                executable.write_text(
                    "#!/usr/bin/env python3\n"
                    "import json, os, sys\n"
                    "from pathlib import Path\n"
                    "command = [Path(sys.argv[0]).name, *sys.argv[1:]]\n"
                    "with open(os.environ['COMMAND_LOG'], 'a') as log:\n"
                    "    log.write(json.dumps(command) + '\\n')\n"
                    "failure = os.environ.get('FAIL_ON')\n"
                    "sys.exit(19 if failure and ' '.join(command).startswith(failure) else 0)\n"
                )
                executable.chmod(0o755)
            log = home / "commands.jsonl"
            result = subprocess.run(
                ["bash"], input=self.script, text=True, capture_output=True,
                env={**os.environ, "HOME": str(home), "COMMAND_LOG": str(log), "FAIL_ON": fail_on},
            )
            return result, [json.loads(line) for line in log.read_text().splitlines()]

    def test_installation_sources_and_host_configuration(self):
        """Archives supply the marketplaces and both hosts enable their plugins."""
        self.assertEqual(
            set(self.externals),
            {f".local/share/agent-plugin-sources/{s['directory']}" for s in self.sources},
        )
        for source in self.sources:
            archive = self.externals[f".local/share/agent-plugin-sources/{source['directory']}"]
            self.assertEqual(archive["stripComponents"], 1)
            self.assertEqual(
                archive["url"],
                f"https://github.com/{source['repository']}/archive/{source['revision']}.tar.gz",
            )
            marketplace = source["marketplace"]
            claude_source = self.claude["extraKnownMarketplaces"][marketplace]["source"]
            codex_source = self.codex["marketplaces"][marketplace]
            self.assertEqual(claude_source["source"], "directory")
            self.assertEqual(codex_source["source_type"], "local")
            self.assertEqual(claude_source["path"], codex_source["source"])
            self.assertTrue(claude_source["path"].endswith(
                f"/.local/share/agent-plugin-sources/{source['directory']}"
            ))
            for plugin in source["plugins"]:
                identifier = f"{plugin}@{marketplace}"
                self.assertTrue(self.claude["enabledPlugins"][identifier])
                self.assertTrue(self.codex["plugins"][identifier]["enabled"])

    def test_installer_uses_native_commands_for_every_plugin(self):
        """Installation and refresh use host CLIs rather than rewriting skill files."""
        syntax = subprocess.run(["bash", "-n"], input=self.script, text=True)
        self.assertEqual(syntax.returncode, 0)
        result, commands = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = []
        for source in self.sources:
            marketplace = source["marketplace"]
            root = self.codex["marketplaces"][marketplace]["source"]
            expected.extend([
                ["claude", "plugin", "marketplace", "add", root],
                ["claude", "plugin", "marketplace", "update", marketplace],
                ["codex", "plugin", "marketplace", "add", root],
            ])
            for plugin in source["plugins"]:
                identifier = f"{plugin}@{marketplace}"
                expected.extend([
                    ["claude", "plugin", "install", identifier, "--scope", "user"],
                    ["claude", "plugin", "update", identifier, "--scope", "user"],
                    ["codex", "plugin", "add", identifier],
                ])
        self.assertEqual(commands, expected)
        self.assertNotIn("SKILL.md", self.script)
        self.assertNotIn(".agents/skills", self.script)

    def test_native_command_failure_stops_installation(self):
        """A failed marketplace registration cannot be reported as a successful install."""
        result, commands = self.run_installer("codex plugin marketplace add")
        self.assertEqual(result.returncode, 19)
        self.assertEqual(len(commands), 3)


if __name__ == "__main__":
    unittest.main()
