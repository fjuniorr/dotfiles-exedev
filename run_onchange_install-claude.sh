#!/usr/bin/env bash
set -euo pipefail

# Claude Code native installer drops versioned builds under
# ~/.local/share/claude and a `claude` symlink in ~/.local/bin, fetching the
# latest stable build. `claude` self-updates after that, so this only needs to
# bootstrap a fresh VM.
if command -v claude >/dev/null 2>&1; then
  exit 0
fi

curl -fsSL https://claude.ai/install.sh | bash
