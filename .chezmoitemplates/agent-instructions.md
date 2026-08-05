When working on the context of an engineering plans (`/home/exedev/plans`) follow this structure:

- `README.md`: Captures the background context for the project, including problem and objectives
- `DECISIONS.md`: Records decisions whose rationale should be preserved, especially alternatives that were considered but rejected (append-only)
- `TODO.md`: Tracks remaining work
- `artifacts/`: Stores supporting evidence and working material

Code is the source of truth for design and implementation. Commits explain individual changes. Pull requests synthesize work for review.

`DECISIONS.md` is a Markdown list. Each top-level item is one decision, with optional indented Markdown for supporting context.

`TODO.md` is a Markdown checklist. Each top-level item is one remaining task, with optional indented Markdown for supporting context.

```text
plans/
└── YYYY-MM-DD-<slug>/
    ├── README.md                # project context
    ├── DECISIONS.md             # durable reasoning
    ├── TODO.md                  # remaining work
    ├── .gitignore               # ignore large files and PII
    └── artifacts/
        ├── prototypes/          # UI and UX prototypes
        ├── transcripts/         # meetings, interviews, conversations
        ├── data/                # datasets
        ├── reports/             # code walkthroughs, incident reports, deep dives, reference materials
        ├── scripts/             # ad-hoc scripts
        └── tools/               # standalone utilities
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
