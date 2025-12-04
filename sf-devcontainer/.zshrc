# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load
ZSH_THEME="powerlevel10k/powerlevel10k"

# Plugins
plugins=(
  git
  docker
  docker-compose
  node
  npm
  vscode
  zsh-autosuggestions
  zsh-syntax-highlighting
  zsh-completions
  command-not-found
  colored-man-pages
  extract
  copyfile
  copypath
)

source $ZSH/oh-my-zsh.sh

# User configuration

# Preferred editor
export EDITOR='vim'


# General aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'

# Custom functions
function mkcd() {
  mkdir -p "$1" && cd "$1"
}


# Display welcome message
echo ""
echo "🚀 Salesforce Development Environment"
echo "======================================"
echo "Node version: $(node --version)"
echo "Java version: $(java -version 2>&1 | head -n 1)"
echo "SF CLI: $(sf version --json | jq -r '.cliVersion')"
echo ""
echo ""

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

SF_AC_ZSH_SETUP_PATH=/home/vscode/.cache/sf/autocomplete/zsh_setup && test -f $SF_AC_ZSH_SETUP_PATH && source $SF_AC_ZSH_SETUP_PATH; # sf autocomplete setup