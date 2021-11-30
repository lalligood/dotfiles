# PostgreSQL
#export PGVERSION=$(postgres --version | awk '{print $3}')

# bash history settings
HISTCONTROL=ignoreboth
shopt -s histappend
export HISTTIMEFORMAT="%F %T "
HISTFILESIZE=5000
HISTSIZE=2500

# less custom configuration
export LESS="--clear-screen --ignore-case --status-column --long-prompt --quiet"

# Add color to man pages - requires `brew install most`
export PAGER="most"

# Add Pentaho to PATH
export PATH=$PATH:/Applications/data-integration
# Add MySQL to PATH
export PATH="$PATH:/usr/local/opt/mysql@5.7/bin"

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# Supercharge <ctrl>-r with fzf (requires `brew install fzf`)
[ -f ~/.fzf.bash ] && source ~/.fzf.bash

# Starship shell
eval "$(starship init bash)"
export STARSHIP_CONFIG=~/.config/starship.toml

# Following 2 lines updates PATH for the Google Cloud SDK & enables shell command completion
if [ -f $HOME/Projects/google-cloud-sdk/path.bash.inc ]; then . $HOME/Projects/google-cloud-sdk/path.bash.inc; fi
if [ -f $HOME/Projects/google-cloud-sdk/completion.bash.inc ]; then . $HOME/Projects/google-cloud-sdk/completion.bash.inc; fi
