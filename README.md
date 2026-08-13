# dotfiles

Minimal dotfiles for bootstrapping fresh exe.dev VMs via
[chezmoi](https://chezmoi.io). Not intended for use on my main machine.

## Install (on a fresh VM)

```sh
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply fjuniorr
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
