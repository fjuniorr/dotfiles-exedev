# Shell aliases — sourced from ~/.bashrc via dotfiles/init.sh
alias claude='claude --dangerously-skip-permissions'
alias codex='codex --dangerously-bypass-approvals-and-sandbox'
alias ls='ls -GFhal'

# ss — fuzzy search the notebook and copy what was picked. On the mac this
# ends in pbcopy; here the copy has to cross the SSH boundary, so it goes out
# as an OSC 52 escape and lands on the clipboard of whatever machine the
# terminal is running on. See osc52() in functions.sh.
alias ss="zt search | tr -d '\n' | osc52"
