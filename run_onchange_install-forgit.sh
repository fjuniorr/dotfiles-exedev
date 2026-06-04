#!/usr/bin/env bash
set -euo pipefail

if command -v git-forgit >/dev/null 2>&1; then
  exit 0
fi

mkdir -p "$HOME/.local/bin" "$HOME/.local/share"
if [ ! -d "$HOME/.local/share/forgit/.git" ]; then
  git clone --quiet --depth 1 https://github.com/wfxr/forgit.git \
    "$HOME/.local/share/forgit"
fi
ln -sf "$HOME/.local/share/forgit/bin/git-forgit" "$HOME/.local/bin/git-forgit"
