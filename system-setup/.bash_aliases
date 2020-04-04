alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
# docker containers
alias tldr='docker run --rm -it -v ~/.tldr/:/root/.tldr/ nutellinoit/tldr'
alias git-tip='docker run -it --rm djoudix/git-tip git-tip'
#git
alias branch-clear='git branch --merged | grep -v "master" | grep -v "development" | grep -v "\*" | xargs git branch -d'
