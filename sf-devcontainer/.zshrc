# Salesforce devcontainer shell.
#
# Deliberately framework-free: Starship + directly-sourced plugins + ONE cached
# compinit, mirroring the host setup that cut startup from 1370ms to 61ms.
# Do not reintroduce Oh My Zsh — it is what this replaced.

# --- completions -----------------------------------------------------------
# Every fpath addition MUST happen before compinit.
#
# The sf autocomplete directory is listed here on purpose. `sf autocomplete zsh`
# generates a ~/.cache/sf/autocomplete/zsh_setup that appends to fpath and then
# runs a SECOND, uncached `compinit` — a full security scan of every fpath
# directory on every interactive shell, which is exactly the cost this file
# exists to avoid. Adding the directory here instead lets the single cached
# compinit below cover sf's completions too. Do not source zsh_setup.
fpath=(
  /usr/share/zsh/vendor-completions
  /home/vscode/.cache/sf/autocomplete/functions/zsh
  $fpath
)

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

# sf completions are wired up via the fpath entry at the top of this file, not
# by sourcing sf's generated zsh_setup — sourcing it would run a second,
# uncached compinit on every shell. See the comment there.

# Per-developer overrides — layer your own aliases/tweaks without rebuilding.
# For full dotfiles, use VS Code's dotfiles.repository setting.
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
