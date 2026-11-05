# Writing

- Write in direct, natural prose for a teammate who wasn’t part of the conversation. Describe the problem itself rather than narrating “the user reported” or “the agent verified.” Present the settled proposal without replaying debates or justifying rejected alternatives. Use simple headings and include enough detail to make the reasoning clear; concision should remove repetition and unnecessary implementation detail, not essential context.

- Mannered prose substitutes metaphor and flourish for direct statement. Instead of "a parameter worth varying," the mannered writer produces "a dial worth turning." Instead of "this point still matters," they write "this point earns its keep." The phrases exist to display the writer, not to convey the idea, and readers can tell. That is why mannered prose irritates: it makes the reader work harder so the writer can perform. It is also imprecise. Metaphors drag in connotations the writer did not choose and cannot control. The fix is to say what you mean. When a literal phrase is available, use it.

- Use google developer documentation style guide (https://developers.google.com/style).

# Personal knowledge base (Notebook)

Identifiers like `20261029T083335` (`YYYYMMDDTHHMMSS`) refer to notes in my
personal knowledge base: `~/Notebook` on the Mac mini, `~/pim` on exe.dev VMs.
Read its `AGENTS.md` first, then open `notes/<id>.md` or
`notes/<id>/index.md`. Resolve bare IDs and `[[<id>|<title>]]` links this way
without asking what they refer to.

# Ficks

- Ensure `just serve` is running from the `plans` repo inside a tmux session named `plans`

- Always run the test suite as `just test -n 0` on the VMs to prevent out-of-memory errors

{{ template "aws-sso-instructions.md" . }}

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
- Use `--body-file` for issue and PR bodies rather than inlining them.
- Merge with `gh pr merge --squash`, without `-d` / `--delete-branch`.
  If remote branch deletion is requested, confirm the PR is merged, then use:
  `gh api -X DELETE repos/OWNER/REPO/git/refs/heads/BRANCH`.
  Keep the literal `/` after `heads`; the proxy rejects `%2F`.
- Do not use `--attach` through the proxy.
- Identify the integration actor with
  `gh api graphql -f query='{viewer{login}}' --jq '.data.viewer.login'`.
- For read-only API diagnostics, use `--include` without `--jq` to see the
  HTTP status and error body.
- For clone auth/404 errors, check whether the repo integration is attached.
  If missing, ask the user to run:
  `ssh exe.dev integrations add github --name NAME --repository OWNER/REPO --attach vm:VM_NAME`
- Pushes show as `exe-dev-github-integration[bot]` unless the integration has
  `--act-as-user`; `--readonly` integrations reject pushes and API writes.

{{ template "artifacts-instructions.md" . }}
