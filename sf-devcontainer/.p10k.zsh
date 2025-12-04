# Powerlevel10k configuration
# This is a minimal configuration - users can customize by running `p10k configure`

# Instant prompt mode
typeset -g POWERLEVEL9K_INSTANT_PROMPT=quiet

# Simple two-line prompt
typeset -g POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(
  dir
  vcs
  prompt_char
)

typeset -g POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(
  status
  command_execution_time
  background_jobs
  time
)

# Colors
typeset -g POWERLEVEL9K_DIR_FOREGROUND=31
typeset -g POWERLEVEL9K_VCS_CLEAN_FOREGROUND=76
typeset -g POWERLEVEL9K_VCS_MODIFIED_FOREGROUND=178
typeset -g POWERLEVEL9K_VCS_UNTRACKED_FOREGROUND=178

# Time format
typeset -g POWERLEVEL9K_TIME_FORMAT='%D{%H:%M:%S}'
