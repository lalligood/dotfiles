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

# Powerline Config
pyver=$(python3 --version | awk -F'.' '{print $2}')
export PATH="$PATH:$HOME/Library/Python/3.${pyver}/bin"
powerline-daemon -q
POWERLINE_BASH_CONTINUATION=1
POWERLINE_BASH_SELECT=1
source /usr/local/lib/python3.${pyver}/site-packages/powerline/bindings/bash/powerline.sh

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# Supercharge <ctrl>-r with fzf (requires `brew install fzf`)
[ -f ~/.fzf.bash ] && source ~/.fzf.bash
