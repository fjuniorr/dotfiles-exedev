#!/usr/bin/env bash
set -euo pipefail

if command -v hunk >/dev/null 2>&1; then
  exit 0
fi

# hunk (terminal diff viewer) ships as a Node package; it needs Node 18+. The
# VMs don't manage node, so skip rather than fail when npm is absent.
if ! command -v npm >/dev/null 2>&1; then
  echo "install-hunk: npm (Node.js 18+) not found; skipping" >&2
  exit 0
fi

npm install -g hunkdiff
