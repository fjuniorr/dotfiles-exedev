# dotfiles

Minimal dotfiles for bootstrapping fresh exe.dev VMs via
[chezmoi](https://chezmoi.io). Not intended for use on my main machine.

## Install (on a fresh VM)

```sh
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply https://github.int.exe.xyz/fjuniorr/dotfiles-exedev.git
```

Then open a new shell (or `exec bash -l`) — picks up the updated
`~/.bashrc` and puts `chezmoi` on `PATH`.

Init prompts for two work values (the ficks AWS SSO start URL and account
ID — kept out of this public repo) and writes `~/.aws/config` from them.
Answers persist in the VM-local chezmoi config, so only a fresh `init`
asks. After that, AWS login is browserless via the device-code flow:

```sh
aws sso login --profile ficks --use-device-code
```

It prints a URL + code; approve it from a browser on any other device.
(`--no-browser` alone is not enough — the default flow redirects to
localhost on the VM.)

## GitHub CLI

Chezmoi installs the latest stable `gh` release from GitHub, verifies its
published SHA-256 checksum, and upgrades it on `chezmoi apply` or
`chezmoi update` when a newer release is available. This installer uses
`sudo` to install the binary at `/usr/local/libexec/gh` and a launcher at
`/usr/local/bin/gh`, so all VM users and services can use it.

On Ubuntu and Debian, `/usr/bin/gh` also points to the launcher. The
installer uses `dpkg-divert` to preserve the distro binary at
`/usr/bin/gh.distrib` and keep package upgrades from replacing the link.
This matters on exe.dev, where SSH sessions put `/bin` and `/usr/bin`
before `/usr/local/bin` in `PATH`.

The launcher defaults `GH_HOST` to `github.int.exe.xyz`, as described in
the [exe.dev GitHub integration guide](https://exe.dev/docs/integrations-github#using-the-gh-cli).
It supplies the variable each time `gh` runs, including from noninteractive
shells, cron, and services. No shell export or `gh auth login` is needed:

```sh
gh pr list -R OWNER/REPO
```

This sets the environment for `gh` and its children, not for unrelated
programs. An explicit `GH_HOST` takes precedence. Calling
`/usr/local/libexec/gh` or the preserved distro binary directly bypasses
the default. The installer prints the managed version when it finishes.

## Shared static artifacts

Use file-based publishing instead of Claude Artifacts, chat-embedded
HTML/iframe previews, or similar artifact/canvas tools. These deliverables
turn generated output into something the user can view, interact with, or
download: reports, visualizations, diagrams, UI mockups, and small demos.
Ordinary files and direct browser URLs keep that output editable and usable
outside the originating chat.

**If the work has a corresponding engineering plan, use its existing
folder first.** For Ficks, follow `ficks/AGENTS.md` and
`ficks/docs/working-with-claude.md`. The sibling plans repo stores each plan
at `plans/YYYY-MM-DD-<slug>/README.md`. Put related artifacts alongside that
file or in an appendix subfolder, link them from the plan, and serve them
through the existing plans viewer (`just serve` in the `plans` tmux session).
Follow that repo's privacy, metadata, and commit/publish conventions.
Do not create a plan merely to host an artifact or substitute a same-named
temporary folder for an existing plan.

**Without a corresponding plan, use the shared temporary server.**
On Linux, chezmoi installs and enables `artifacts.service`, a Python
static server on **port 8765**. It starts at boot and restarts after failure.
The installer requires Python 3, systemd, `ss`, and sudo access. It refuses
to take over an occupied port and leaves **8000 available for Django**.

Publish previews, reports, and downloads under
`/tmp/artifacts/<feature-branch-slug>/`. Usually the slug comes from
the current feature branch: lowercase the name, replace runs of punctuation
with `-`, and trim leading/trailing hyphens. For example,
`feature/order-preview` becomes `feature-order-preview`. Reuse the folder
for that feature; choose a descriptive feature slug when not on a feature
branch. Avoid collisions with other features.

Visit `https://<vm-name>.exe.xyz:8765/` to browse all folders. Feature
folders serve their `index.html` when present, or a directory listing.
Tools on the VM use `http://localhost:8765/`. The exe.dev proxy controls
access; this server does not add its own authentication.

The same publishing instructions are installed for Claude Code, Codex,
and Shelley. Publish only intended artifacts, never secrets or private
source trees. Previews on each server share an origin, so this is not a sandbox for
untrusted HTML/JavaScript. Files under `/tmp` may disappear on reboot
or through OS cleanup; no custom retention/deletion job is installed.

```sh
systemctl status artifacts.service
journalctl -u artifacts.service
```

Server and unit sources live in `.chezmoitemplates/artifacts/`.
Changes rerun the installer on the next `chezmoi apply`; the installed
server is `/usr/local/lib/artifacts/server.py`.

## Dashlane CLI first use

`dcli` is installed by chezmoi, but Dashlane requires an interactive
device registration before the first sync on each VM:

```sh
dcli sync
```

It prompts for the account email, an OTP (sent by email or from 2FA),
and the master password. Subsequent `dcli` calls reuse the registered
device.

## Notebook search (`ss`) first use

`zt`, `fzf` and `glow` are installed by chezmoi, and `ZETTEL_DIR` is
exported from `dotfiles/init.sh`. The notebook itself is not managed
here — clone it to the path that variable points at:

```sh
git clone https://github.int.exe.xyz/fjuniorr/pim.git ~/pim
```

HTTPS through the integration host, not SSH — no credentials live on the
VM. An auth error or 404 means the integration isn't attached to `pim`
yet; `curl -s https://reflection.int.exe.xyz/integrations` lists what
this VM can reach.

Until it exists, `ss` shows an empty list rather than an error, since
`zt search` just finds no `Actions/` or `Reference/` to read.

`ss` copies the picked note through OSC 52 rather than a local clipboard
tool, so the result lands on the clipboard of the machine you're SSH'd in
from. Some keybinds are mac-only and do nothing here: `enter` on an
existing note (Obsidian), `ctrl-t` (iTerm), `f2` (VS Code). Creating a
note by typing a query and pressing `enter` does work, as do search,
preview, `ctrl-x` (wikilink) and `ctrl-s` (gist).

## Update a VM

```sh
chezmoi update
```

If a managed file changed on the VM since chezmoi last wrote it (e.g. a
tool edited its own config), chezmoi prompts per file with
overwrite/skip/quit. Pass `--force` to skip the prompts and always
overwrite with the repo's version:

```sh
chezmoi update --force
```

If chezmoi warns that the config file template has changed (new prompts
were added to `.chezmoi.toml.tmpl`), re-run init to answer them:

```sh
chezmoi init --apply
```

If the update touched shell config (aliases, prompt, `~/.bashrc`),
reload to see it in the current shell:

```sh
exec bash -l        # or `source ~/.bashrc`, or open a new shell
```
