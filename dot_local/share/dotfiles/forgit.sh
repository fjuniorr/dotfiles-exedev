# forgit (interactive git via fzf) — sourced from ~/.bashrc via dotfiles/init.sh

# The plugin registers its completion through bash-completion's lazy loader, so
# load that first on a bare shell — otherwise sourcing errors with
# "_completion_loader: command not found".
if ! declare -F _completion_loader >/dev/null 2>&1; then
  for bc in /usr/share/bash-completion/bash_completion /etc/bash_completion; do
    [ -r "$bc" ] && . "$bc" && break
  done
fi

[ -f "$HOME/.local/share/forgit/forgit.plugin.sh" ] && \
  . "$HOME/.local/share/forgit/forgit.plugin.sh"
