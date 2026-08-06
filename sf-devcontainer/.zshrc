# Salesforce devcontainer shell.
#
# Deliberately framework-free: Starship + directly-sourced plugins + ONE cached
# compinit, mirroring the host setup that cut startup from 1370ms to 61ms.
# Do not reintroduce Oh My Zsh — it is what this replaced.

# --- completions -----------------------------------------------------------
# Every fpath addition MUST happen before compinit.
fpath=(/usr/share/zsh/vendor-completions $fpath)

autoload -Uz compinit
_zcompdump="${HOME}/.cache/zsh/zcompdump"
mkdir -p "${_zcompdump:h}"
# Cached fast path when the dump is less than 24h old; full scan otherwise.
if [[ -n ${_zcompdump}(#qN.mh-24) ]]; then
  compinit -C -d "$_zcompdump"
else
  compinit -d "$_zcompdump"
fi
unset _zcompdump

# --- history ---------------------------------------------------------------
# Persists across container rebuilds when a volume is mounted at
# /commandhistory (see .devcontainer/devcontainer.json).
HISTSIZE=50000
SAVEHIST=50000
setopt HIST_IGNORE_ALL_DUPS HIST_REDUCE_BLANKS INC_APPEND_HISTORY
[[ -d /commandhistory && -w /commandhistory ]] && export HISTFILE=/commandhistory/.zsh_history

export EDITOR='vim'

# --- integrations ----------------------------------------------------------
command -v fzf >/dev/null && source <(fzf --zsh)      # ^R history, ^T files, alt-C dirs
command -v zoxide >/dev/null && eval "$(zoxide init zsh)"

# --- aliases ---------------------------------------------------------------
alias ls='eza'
alias ll='eza -alF --git --group-directories-first'
alias la='eza -a'
alias l='eza -F'
alias lt='eza --tree --level=2'
alias ..='cd ..'
alias ...='cd ../..'

# Salesforce shortcuts — run `sfhelp` to list them
alias sfl='sf org list'
alias sfo='sf org open'
alias sfd='sf project deploy start'
alias sfdp='sf project deploy preview'
alias sfr='sf project retrieve start'
alias sft='sf apex run test --code-coverage --result-format human --wait 10'

function sfdelta() {
  sf sgd source delta --from "${1:-origin/main}" --to HEAD --output-dir delta-output
}

function sfhelp() {
  cat <<'EOF'
Salesforce shortcuts:
  sfl        sf org list
  sfo        sf org open
  sfd        sf project deploy start
  sfdp       sf project deploy preview
  sfr        sf project retrieve start
  sft        sf apex run test --code-coverage --result-format human --wait 10
  sfdelta    sf sgd source delta --from <ref, default origin/main> --to HEAD
EOF
}

function devhelp() {
  bat --style=plain --language=md /usr/local/share/sf-devcontainer/cheatsheet.md
}

function mkcd() {
  mkdir -p "$1" && cd "$1"
}

# --- welcome ---------------------------------------------------------------
# Static: no subprocesses, so it costs nothing at shell start.
echo ""
echo "🚀 Salesforce Development Environment"
echo "======================================"
echo "sf · node · java 17 · gh · fzf · zoxide · eza · bat · rg · fd · delta · lazygit"
echo "Run 'sfhelp' for Salesforce shortcuts, 'devhelp' for the CLI tools cheatsheet."
echo ""

# --- zsh plugins -----------------------------------------------------------
# ORDER MATTERS: zsh-syntax-highlighting must be sourced LAST, or it silently
# stops highlighting.
source /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh
source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# --- prompt ----------------------------------------------------------------
eval "$(starship init zsh)"

SF_AC_ZSH_SETUP_PATH=/home/vscode/.cache/sf/autocomplete/zsh_setup && test -f $SF_AC_ZSH_SETUP_PATH && source $SF_AC_ZSH_SETUP_PATH; # sf autocomplete setup

# Per-developer overrides — layer your own aliases/tweaks without rebuilding.
# For full dotfiles, use VS Code's dotfiles.repository setting.
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
