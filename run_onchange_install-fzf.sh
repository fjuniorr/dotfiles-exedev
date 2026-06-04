#!/usr/bin/env bash
set -euo pipefail

if command -v fzf >/dev/null 2>&1; then
  exit 0
fi

mkdir -p "$HOME/.local/bin" "$HOME/.local/share"
if [ ! -d "$HOME/.local/share/fzf/.git" ]; then
  git clone --quiet --depth 1 https://github.com/junegunn/fzf.git \
    "$HOME/.local/share/fzf"
fi
# --bin only fetches the prebuilt binary into fzf/bin; it leaves shell rc files
# alone (our init.sh does the wiring), unlike the interactive ./install.
"$HOME/.local/share/fzf/install" --bin >/dev/null
ln -sf "$HOME/.local/share/fzf/bin/fzf" "$HOME/.local/bin/fzf"
