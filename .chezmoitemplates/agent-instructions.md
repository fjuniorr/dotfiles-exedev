# Writing

- Write in direct, natural prose for a teammate who wasn’t part of the conversation. Describe the problem itself rather than narrating “the user reported” or “the agent verified.” Present the settled proposal without replaying debates or justifying rejected alternatives. Use simple headings and include enough detail to make the reasoning clear; concision should remove repetition and unnecessary implementation detail, not essential context.

- Mannered prose substitutes metaphor and flourish for direct statement. Instead of "a parameter worth varying," the mannered writer produces "a dial worth turning." Instead of "this point still matters," they write "this point earns its keep." The phrases exist to display the writer, not to convey the idea, and readers can tell. That is why mannered prose irritates: it makes the reader work harder so the writer can perform. It is also imprecise. Metaphors drag in connotations the writer did not choose and cannot control. The fix is to say what you mean. When a literal phrase is available, use it.

- Use google developer documentation style guide (https://developers.google.com/style).

# Engineering plans

When working on the context of an engineering plans (`/home/exedev/plans`) use two sections: **Problem** and **Solution** for the main `README.md` :

- The Problem should identify who is affected, the context, and why the current situation matters, supported by concrete examples and evidence. 
- The Solution should state the proposed direction, the value it should provide to those affected, expected outcomes, and important constraints. 
- Make both sections understandable without reconstructing the original discussion, and distinguish observed facts from assumptions or stakeholder judgments. 
- Leave out implementation steps, exhaustive technical details, and the history of how decisions were reached.
- Code is the source of truth for design and implementation. Commits explain individual changes. Pull requests synthesize work for review.

```text
plans/
└── YYYY-MM-DD-<slug>/
    ├── README.md            # problem and solution
    ├── .gitignore           # ignore large files and PII
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
- `/usr/local/bin/gh` defaults to the integration host, including in
  noninteractive shells and services. Use an explicit repo:
  `gh pr list -R OWNER/REPO`
- `gh` subcommands that write via GraphQL fail with `HTTP 403 (…/api/graphql)`
  even where the integration allows writes; GraphQL reads are fine. Confirmed
  for `gh issue create`; assume the same for `gh pr create` and friends. Use
  the REST endpoint instead — it accepts writes:
  `gh api repos/OWNER/REPO/issues -X POST -f title=T -F body=@body.md`
  (`…/pulls -X POST -f title=T -f head=BRANCH -f base=main` for a PR).
  Write the body to a file and pass `-F body=@file` rather than inlining it.
- Clone fails with auth/404 → no integration attached; ask the user to run:
  `ssh exe.dev integrations add github --name NAME --repository OWNER/REPO --attach vm:VM_NAME`
- Pushes show as `exe-dev-github-integration[bot]` unless the integration has
  `--act-as-user`; `--readonly` integrations reject pushes and API writes.
