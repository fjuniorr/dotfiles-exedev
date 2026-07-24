When creating engineering plans follow this folder organization structure:

```
YYYY-MM-DD-<slug>/
    ├── README.md         # plan
    ├── datapackage.json  # frictionless data package describing files in data/ including human readable column titles and descriptions
    ├── data/             # datasets
    ├── reports/          # code walkthroughs, incident reports, explanation deep dives, reference materials, etc
    ├── scripts/          # ad-hoc scripts
    ├── tools/            # standalone html tools
    └── .gitignore        # ignore files in data/ and data-raw/ that exceed 10MB
```

Ensure `just serve` is running from the `plans` repo inside a tmux session named `plans`.

# GitHub on exe.dev VMs

GitHub access goes through the exe.dev GitHub integration
(https://exe.dev/docs/all#integrations-github). No credentials live on the
VM — never run `gh auth login` or set up tokens.

- Clone via HTTPS through the integration host, never github.com or SSH:
  `git clone https://github.int.exe.xyz/OWNER/REPO.git`. Rewrite `github.com`
  remotes on existing checkouts with `git remote set-url`.
- List repos available to this VM (each `github` entry has a ready-made
  clone command): `curl -s https://reflection.int.exe.xyz/integrations`
- `gh` needs `GH_HOST=github.int.exe.xyz` (exported in interactive shells;
  set it if missing) and an explicit repo: `gh pr list -R OWNER/REPO`
- Clone fails with auth/404 → no integration attached; ask the user to run:
  `ssh exe.dev integrations add github --name NAME --repository OWNER/REPO --attach vm:VM_NAME`
- Pushes show as `exe-dev-github-integration[bot]` unless the integration has
  `--act-as-user`; `--readonly` integrations reject pushes and API writes.
