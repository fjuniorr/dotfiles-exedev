# dotfiles

Minimal dotfiles for bootstrapping fresh exe.dev VMs via
[chezmoi](https://chezmoi.io). Not intended for use on my main machine.

## Install (on a fresh VM)

```sh
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply fjuniorr
```

Then open a new shell (or `exec bash -l`) — picks up the updated
`~/.bashrc` and puts `chezmoi` on `PATH`.

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

If the update touched shell config (aliases, prompt, `~/.bashrc`),
reload to see it in the current shell:

```sh
exec bash -l        # or `source ~/.bashrc`, or open a new shell
```
