# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load
ZSH_THEME="powerlevel10k/powerlevel10k"

# Plugins (zsh-syntax-highlighting must stay last)
plugins=(
  git
  docker
  docker-compose
  node
  npm
  vscode
  gh
  fd
  ripgrep
  zoxide
  command-not-found
  colored-man-pages
  extract
  copyfile
  copypath
  zsh-autosuggestions
  zsh-completions
  zsh-syntax-highlighting
)

source $ZSH/oh-my-zsh.sh

# User configuration

# Preferred editor
export EDITOR='vim'

# History — large, deduplicated; persists across container rebuilds when a
# volume is mounted at /commandhistory (see .devcontainer/devcontainer.json)
HISTSIZE=50000
SAVEHIST=50000
setopt HIST_IGNORE_ALL_DUPS HIST_REDUCE_BLANKS INC_APPEND_HISTORY
[[ -d /commandhistory && -w /commandhistory ]] && export HISTFILE=/commandhistory/.zsh_history

# fzf shell integration (Ctrl-R fuzzy history, Ctrl-T file picker, Alt-C cd)
command -v fzf >/dev/null && source <(fzf --zsh)

# Modern replacements (eza for ls; bat/fd are symlinked from batcat/fdfind)
alias ls='eza'
alias ll='eza -alF --git --group-directories-first'
alias la='eza -a'
alias l='eza -F'
alias lt='eza --tree --level=2'
alias ..='cd ..'
alias ...='cd ../..'

# Salesforce CLI shortcuts — run `sfhelp` to list them
alias sfl='sf org list'
alias sfo='sf org open'
alias sfd='sf project deploy start'
alias sfdp='sf project deploy preview'
alias sfr='sf project retrieve start'
alias sft='sf apex run test --code-coverage --result-format human --wait 10'

# Delta deployment package from git history (sfdx-git-delta plugin)
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

# Custom functions
function mkcd() {
  mkdir -p "$1" && cd "$1"
}

# Display welcome message (static — no subprocesses, keeps shell start fast)
echo ""
echo "🚀 Salesforce Development Environment"
echo "======================================"
echo "sf · node · java 17 · gh · fzf · zoxide · eza · bat · rg · fd · delta · lazygit"
echo "Run 'sfhelp' for Salesforce shortcuts, 'sf version' for tool versions."
echo ""

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

SF_AC_ZSH_SETUP_PATH=/home/vscode/.cache/sf/autocomplete/zsh_setup && test -f $SF_AC_ZSH_SETUP_PATH && source $SF_AC_ZSH_SETUP_PATH; # sf autocomplete setup

# Per-developer overrides — layer your own aliases/theme tweaks without
# rebuilding the image. For full dotfiles, use VS Code's dotfiles.repository
# setting (see sf-devcontainer/README.md).
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
