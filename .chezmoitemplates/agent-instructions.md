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
- Use `gh issue create`, `gh pr create`, and `gh pr merge --squash` normally.
  These worked through the proxy with gh 2.103.3 on November 4–5, 2026;
  GraphQL writes are not generally blocked. Use `--body-file` for issue
  and PR bodies rather than inlining them.
- Avoid `-d` / `--delete-branch` when merging through the proxy. In the same
  tests, `gh pr merge -sd` merged successfully, then failed with HTTP 400
  deleting the remote branch: the proxy rejects the encoded `heads%2F...`
  path. Check the PR's merge state before retrying. If remote branch deletion
  is requested, confirm it is merged, then use the tested unencoded path:
  `gh api -X DELETE repos/OWNER/REPO/git/refs/heads/BRANCH`.
  This deletes only the remote branch.
- `--attach` fails before uploading because gh treats the proxy hostname as
  GitHub Enterprise Server. Changing credentials will not fix this check.
- `gh api user --jq '.login'` fails: the proxy rejects `/user` because it
  names no repository, and the JSON filter hides the explanation. Identify
  the integration actor with
  `gh api graphql -f query='{viewer{login}}' --jq '.data.viewer.login'`.
  For read-only API diagnostics, use `--include` without `--jq` to see the
  HTTP status and error body.
- Test details: `~/pim/notes/20261104T193900.md`. Do not infer that other
  commands fail from one rejected request.
- For clone auth/404 errors, check whether the repo integration is attached.
  If missing, ask the user to run:
  `ssh exe.dev integrations add github --name NAME --repository OWNER/REPO --attach vm:VM_NAME`
- Pushes show as `exe-dev-github-integration[bot]` unless the integration has
  `--act-as-user`; `--readonly` integrations reject pushes and API writes.

{{ template "artifacts-instructions.md" . }}
