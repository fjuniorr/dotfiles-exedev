# Shell functions — sourced from ~/.bashrc via dotfiles/init.sh

# osc52 — copy stdin to the clipboard of the terminal we're being viewed in.
# pbcopy is macOS-only and xclip/wl-copy need a display server these headless
# VMs don't run, so neither can reach the clipboard you actually paste from.
# OSC 52 sidesteps that: the escape travels back over SSH and the terminal
# emulator does the copying. GNU base64 wraps at 76 columns, hence the tr.
# Writing to /dev/tty keeps it working when stdout is piped or captured.
# Under tmux this needs `set -g set-clipboard on` (see .tmux.conf) — the
# default `external` lets tmux set the outer clipboard but drops sequences
# coming from programs running inside it.
osc52() {
  printf '\033]52;c;%s\a' "$(base64 | tr -d '\n')" > /dev/tty
}

# pp — fuzzy-pick a directory under $HOME (/home/exedev on these VMs) and cd
# into it. A README.md, when present, is previewed with glow. (Shadows NSS's
# ASN.1 pretty-printer pp from libnss3-tools, which goes unused on these VMs.)
pp() {
  local base="$HOME" dir
  dir=$(find "$base" -mindepth 1 -maxdepth 1 -type d -not -name '.*' -printf '%f\n' \
    | fzf --height=60% --preview-window "down:60%" \
        --preview "test -f \"$base/{}/README.md\" && glow --style dark \"$base/{}/README.md\"") \
    && cd "$base/$dir"
}
