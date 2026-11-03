"""Exercise the Shelley catalog bridge without changing agent configuration."""

import importlib.machinery
import importlib.util
import io
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "dot_local/bin/executable_plugin-skills"
LOADER = importlib.machinery.SourceFileLoader("plugin_skills", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
bridge = importlib.util.module_from_spec(SPEC)
with patch.object(sys, "dont_write_bytecode", True):
    LOADER.exec_module(bridge)


class PluginSkillTests(unittest.TestCase):
    """Keep the bridge namespaced, source-preserving, and safe for system prompts."""

    def setUp(self):
        """Give every test an isolated home and two same-named upstream skills."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.cache = self.home / ".cache/shelley/plugin-skills.json"
        self.skills = []
        for plugin in ("alpha", "beta"):
            path = self.home / "sources" / plugin / "skills/tdd/SKILL.md"
            path.parent.mkdir(parents=True)
            flag = "disable-model-invocation: true\n" if plugin == "beta" else ""
            path.write_text(
                f"---\nname: tdd\ndescription: Original.\n{flag}---\n\n"
                "Read references.md.\n"
            )
            self.skills.append({
                "name": f"{plugin}:tdd", "description": 'Tests <interfaces> & "behavior".',
                "path": str(path), "enabled": True, "pluginId": f"{plugin}@test",
            })
        self.plugins = {"alpha@test", "beta@test"}
        config = self.home / ".config/shelley/plugin-sources.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"plugins": sorted(self.plugins)}))

    def cache_skills(self):
        """Build an index from fixture metadata rather than launching Codex."""
        with patch.object(bridge, "discover", return_value=self.skills):
            bridge.refresh(self.home)

    def test_native_names_and_original_files_are_preserved(self):
        """Two tdd skills stay distinct without editing either upstream document."""
        original = [Path(s["path"]).read_bytes() for s in self.skills]
        entries = bridge.catalog_entries(self.skills, self.plugins)
        self.assertEqual([s["name"] for s in entries], ["alpha:tdd", "beta:tdd"])
        self.assertEqual([s["explicit"] for s in entries], [False, True])
        self.assertEqual([Path(s["path"]).read_bytes() for s in self.skills], original)

    def test_only_enabled_selected_plugins_are_indexed(self):
        """Standalone skills, disabled skills, and unselected plugins are excluded."""
        candidates = [
            *self.skills,
            {**self.skills[0], "pluginId": None, "name": "standalone"},
            {**self.skills[0], "pluginId": "other@test", "name": "other:tdd"},
            {**self.skills[0], "enabled": False, "name": "alpha:disabled"},
        ]
        self.assertEqual(len(bridge.catalog_entries(candidates, self.plugins)), 2)

    def test_invocation_flag_is_read_only_from_frontmatter(self):
        """Mentioning the flag in the skill body does not disable automatic selection."""
        path = Path(self.skills[0]["path"])
        path.write_text(path.read_text() + "\ndisable-model-invocation: true\n")
        self.assertFalse(bridge.catalog_entries(self.skills, self.plugins)[0]["explicit"])

    def test_refresh_is_stable_and_failure_preserves_previous_catalog(self):
        """A repeat refresh avoids rewrites and a failed refresh keeps the working index."""
        self.cache_skills()
        before = self.cache.read_bytes(), self.cache.stat().st_mtime_ns
        self.cache_skills()
        self.assertEqual((self.cache.read_bytes(), self.cache.stat().st_mtime_ns), before)
        with patch.object(bridge, "discover", side_effect=RuntimeError("unavailable")):
            with self.assertRaisesRegex(RuntimeError, "unavailable"):
                bridge.refresh(self.home)
        self.assertEqual(self.cache.read_bytes(), before[0])

    def test_duplicate_native_names_are_rejected(self):
        """A collision cannot silently select one plugin's skill over another."""
        with self.assertRaisesRegex(ValueError, "Duplicate plugin skill"):
            bridge.catalog_entries([*self.skills, self.skills[0]], self.plugins)

    def test_prompt_keeps_existing_instructions_and_escapes_metadata(self):
        """Existing system instructions survive alongside safely encoded plugin metadata."""
        self.cache_skills()
        original = "System instructions.\n<available_skills>existing</available_skills>\n"
        prompt = bridge.transform_prompt(original, self.home)
        self.assertTrue(prompt.startswith(original))
        root = ET.fromstring(prompt[prompt.index("<plugin_skills>"):])
        self.assertEqual(len(root), 2)
        self.assertEqual(root[0].findtext("description"), self.skills[0]["description"])
        self.assertEqual(root[1].findtext("invocation"), "explicit")
        self.assertEqual(
            shlex.split(root[0].findtext("activate")),
            [str(self.home / ".local/bin/plugin-skills"), "cat", "alpha:tdd"],
        )
        self.assertEqual(root[0].findtext("location"), self.skills[0]["path"])

    def test_missing_or_corrupt_catalog_cannot_break_shelley(self):
        """An unavailable optional index returns the original system prompt unchanged."""
        original = "System prompt, including all existing skills.\n"
        self.assertEqual(bridge.transform_prompt(original, self.home), original)
        self.cache.parent.mkdir(parents=True)
        for content in ("not json", '{"version": 99}', '{"version": 1, "skills": [null]}'):
            with self.subTest(content=content), patch("sys.stderr", new_callable=io.StringIO):
                self.cache.write_text(content)
                self.assertEqual(bridge.transform_prompt(original, self.home), original)

    def test_removed_skill_files_disappear_from_discovery(self):
        """A stale cache never advertises a skill file that no longer exists."""
        self.cache_skills()
        Path(self.skills[0]["path"]).unlink()
        entries = bridge.load_catalog(self.home)
        self.assertEqual([e["name"] for e in entries], ["beta:tdd"])

    def test_cat_returns_exact_upstream_bytes_and_reports_unknown_names(self):
        """Activation reads the original file, with no added wrapper instructions."""
        self.cache_skills()
        command = [sys.executable, str(SCRIPT), "cat"]
        environment = {**os.environ, "HOME": str(self.home)}
        result = subprocess.run(command + ["beta:tdd"], capture_output=True, env=environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, Path(self.skills[1]["path"]).read_bytes())
        result = subprocess.run(command + ["missing:tdd"], capture_output=True, env=environment)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"not found", result.stderr)

    def test_hook_keeps_prompt_when_helper_is_not_installed(self):
        """A fresh apply cannot break Shelley before the helper has been written."""
        result = subprocess.run(
            ["sh", str(ROOT / "dot_config/shelley/hooks/executable_system-prompt")],
            input="Original prompt.\n", text=True, capture_output=True,
            env={**os.environ, "HOME": str(self.home)},
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "Original prompt.\n")

    def test_discovery_uses_only_metadata_rpc_and_handles_protocol_errors(self):
        """Discovery tolerates notifications and never starts a model turn."""
        executable = self.home / "bin/codex"
        executable.parent.mkdir()
        executable.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "for line in sys.stdin:\n"
            "    request = json.loads(line)\n"
            "    with open(os.environ['PROTOCOL_LOG'], 'a') as log:\n"
            "        log.write(request['method'] + '\\n')\n"
            "    if 'id' not in request: continue\n"
            "    result = {} if request['method'] == 'initialize' else {\n"
            "        'data': [{'errors': [], 'skills': json.loads(os.environ['SKILLS'])}]}\n"
            "    response = {'id': request['id'], 'result': result}\n"
            "    if os.environ.get('PROTOCOL_ERROR') and request['method'] == 'skills/list':\n"
            "        response = {'id': request['id'], 'error': {'message': 'broken'}}\n"
            "    print(json.dumps({'method': 'notification'}) + '\\n' + json.dumps(response), flush=True)\n"
        )
        executable.chmod(0o755)
        log = self.home / "protocol.log"
        environment = {
            "HOME": str(self.home), "PATH": f"{executable.parent}:{os.environ['PATH']}",
            "PROTOCOL_LOG": str(log), "SKILLS": json.dumps(self.skills),
        }
        with patch.dict(os.environ, environment):
            self.assertEqual(bridge.discover(), self.skills)
            self.assertEqual(
                log.read_text().splitlines(), ["initialize", "initialized", "skills/list"]
            )
            with patch.dict(os.environ, {"PROTOCOL_ERROR": "1"}):
                with self.assertRaisesRegex(RuntimeError, "broken"):
                    bridge.discover()


if __name__ == "__main__":
    unittest.main()
