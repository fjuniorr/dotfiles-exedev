#!/usr/bin/env bash
set -euo pipefail

if command -v sentry-cli >/dev/null 2>&1; then
  exit 0
fi

# sentry-cli creates/finalizes the Sentry release around each EB deploy in the
# ficks deploy.sh. The official installer grabs the prebuilt binary from GitHub
# releases; INSTALL_DIR keeps it user-local like everything else here (no sudo).
export INSTALL_DIR="$HOME/.local/bin"
curl -sL https://sentry.io/get-cli/ | bash
