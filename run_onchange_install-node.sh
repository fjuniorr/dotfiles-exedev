#!/usr/bin/env bash
set -euo pipefail

# ccstatusline renders the Claude Code status line (wired up in
# .claude/settings.json) and is a node package invoked through npx, so a VM
# without node silently shows a blank status line instead of failing loudly.
# exe.dev images normally ship node already — this is only the fallback, and the
# guard makes the whole script a no-op whenever npx is on PATH.
if command -v npx >/dev/null 2>&1; then
  exit 0
fi

case "$(uname -m)" in
  x86_64) arch=x64 ;;
  aarch64 | arm64) arch=arm64 ;;
  *)
    echo "install-node: unsupported arch $(uname -m), install node by hand" >&2
    exit 1
    ;;
esac

# Track whatever nodejs.org currently marks LTS rather than pinning a version
# here that goes stale silently.
version="$(curl -fsSL https://nodejs.org/dist/index.json |
  python3 -c 'import json,sys; print(next(r["version"] for r in json.load(sys.stdin) if r["lts"]))')"

# User-local, no sudo, same as every other installer here.
prefix="$HOME/.local/share/node"
mkdir -p "$prefix" "$HOME/.local/bin"
curl -fsSL "https://nodejs.org/dist/${version}/node-${version}-linux-${arch}.tar.xz" |
  tar -xJ -C "$prefix" --strip-components=1

for bin in node npm npx; do
  ln -sf "$prefix/bin/$bin" "$HOME/.local/bin/$bin"
done
