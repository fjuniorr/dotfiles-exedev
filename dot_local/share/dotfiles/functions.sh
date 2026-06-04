# Shell functions — sourced from ~/.bashrc via dotfiles/init.sh

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
