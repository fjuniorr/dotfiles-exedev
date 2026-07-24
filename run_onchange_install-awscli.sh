#!/usr/bin/env bash
set -euo pipefail

if command -v aws >/dev/null 2>&1; then
  exit 0
fi

# AWS CLI v2 ships a self-contained bundle; --install-dir/--bin-dir keep it
# user-local. It doesn't self-update, but version drift doesn't matter for
# the sso/ec2/ssm subcommands the VMs use.
if ! command -v unzip >/dev/null 2>&1; then
  # python3 -m zipfile would lose the exec bits the installer needs
  sudo apt-get install -y -q unzip
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" \
  -o "$tmp/awscliv2.zip"
unzip -q "$tmp/awscliv2.zip" -d "$tmp"
"$tmp/aws/install" --install-dir "$HOME/.local/aws-cli" --bin-dir "$HOME/.local/bin"
