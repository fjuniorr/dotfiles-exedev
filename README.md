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
