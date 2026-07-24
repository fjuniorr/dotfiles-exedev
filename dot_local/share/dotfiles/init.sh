# Entry point sourced from ~/.bashrc by the chezmoi-managed block
DOTFILES_SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# gh works through the exe.dev GitHub integration; no token on the VM
export GH_HOST=github.int.exe.xyz

. "$DOTFILES_SHELL_DIR/aliases.sh"
. "$DOTFILES_SHELL_DIR/functions.sh"
. "$DOTFILES_SHELL_DIR/prompt.sh"
. "$DOTFILES_SHELL_DIR/forgit.sh"

# atuin (ctrl+r shell history) wires itself into ~/.bashrc via its own installer
