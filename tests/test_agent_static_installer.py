"""Check the chezmoi installer without changing system services."""

import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("chezmoi"), "chezmoi is needed to render the installer")
class InstallerTests(unittest.TestCase):
    def render(self, source):
        return subprocess.check_output(
            ["chezmoi", "--source", str(ROOT), "execute-template", "--file", str(ROOT / source)],
            text=True,
        )


    def test_occupied_port_is_left_untouched(self):
        script = self.render("run_onchange_install-agent-static.sh.tmpl")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for name, body in {
                "systemctl": "exit 3",
                "ss": "echo LISTEN",
                "sudo": 'echo "unexpected sudo call" >&2; exit 99',
            }.items():
                path = root / name
                path.write_text(f"#!/bin/sh\n{body}\n")
                path.chmod(0o755)
            result = subprocess.run(
                ["bash"], input=script, text=True, capture_output=True,
                env={**os.environ, "PATH": f"{root}:{os.environ['PATH']}"},
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("port 8765 is occupied", result.stderr)
            self.assertNotIn("unexpected sudo call", result.stderr)
