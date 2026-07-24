#!/usr/bin/env bash
set -euo pipefail

if command -v session-manager-plugin >/dev/null 2>&1; then
  exit 0
fi

# Needed by `aws ssm start-session` — the ficks `just db-tunnel` and
# production-settings recipes. AWS only ships it as a deb, but dpkg -x
# extracts without root so it stays user-local like everything else.
case "$(uname -m)" in
  x86_64|amd64) arch="ubuntu_64bit" ;;
  aarch64|arm64) arch="ubuntu_arm64" ;;
  *) echo "install-session-manager-plugin: unsupported arch $(uname -m); skipping" >&2; exit 0 ;;
esac

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

curl -fsSL "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/${arch}/session-manager-plugin.deb" \
  -o "$tmp/plugin.deb"
dpkg -x "$tmp/plugin.deb" "$tmp/extract"
mkdir -p "$HOME/.local/sessionmanagerplugin" "$HOME/.local/bin"
cp -r "$tmp/extract/usr/local/sessionmanagerplugin/." "$HOME/.local/sessionmanagerplugin/"
ln -sf "$HOME/.local/sessionmanagerplugin/bin/session-manager-plugin" "$HOME/.local/bin/session-manager-plugin"
