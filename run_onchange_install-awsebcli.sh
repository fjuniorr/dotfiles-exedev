#!/usr/bin/env bash
set -euo pipefail

if command -v eb >/dev/null 2>&1; then
  exit 0
fi

# awsebcli provides `eb`, needed by the ficks `just deploy` recipe: deploy.sh
# runs `eb deploy`, and its first step (`manage.py test_env_vars`) shells out to
# `eb printenv`, so a missing `eb` aborts the deploy before anything happens.
# awsebcli pins tight, old dependency ranges; uv gives it an isolated venv that
# won't collide with anything, and drops the `eb` shim into ~/.local/bin (on PATH).
if ! command -v uv >/dev/null 2>&1; then
  # linuxbrew isn't always on PATH in chezmoi's non-interactive run env
  export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"
fi

uv tool install awsebcli
