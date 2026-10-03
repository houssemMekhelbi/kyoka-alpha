# ~/.config/zsh/kyoka-alpha.zsh-theme
# Kyoka alpha prompt: agnoster's segment chain, recoloured
# cold, standalone (no oh-my-zsh). Separators are the powerline arrow.
#   status  Blood + Bone, only on failure / root / background jobs
#   context Raised Violet + Pale Violet, only over SSH or as another user
#   dir     Violet + Bone
#   git     Bone block with Void text when clean, Ice with ± when dirty
# Hex colours need zsh 5.7+ and a true-colour terminal; the arrow needs a Nerd Font.

setopt prompt_subst

KYOKA_DEFAULT_USER=${KYOKA_DEFAULT_USER:-$USER}   # hide context on your own box

K_RAISED='#171225' K_VIOLET='#7B4FD6' K_PALE='#A98BFF'
K_BONE='#EDE8DF'   K_ICE='#8FD3F4'    K_BLOOD='#C24B6B'
K_VOID='#07060B'   K_HAIR='#2A2140'

KYOKA_SEP=$'\ue0b0'
typeset -g KYOKA_BG=NONE

kyoka_segment() {
  local bg="%K{$1}" fg="%F{$2}"
  if [[ $KYOKA_BG != NONE && $1 != $KYOKA_BG ]]; then
    print -n "%{$bg%F{$KYOKA_BG}%}$KYOKA_SEP%{$fg%} "
  else
    print -n "%{$bg%}%{$fg%} "
  fi
  KYOKA_BG=$1
  [[ -n $3 ]] && print -n -- "$3 "
}

kyoka_end() {
  if [[ $KYOKA_BG != NONE ]]; then
    print -n "%{%k%F{$KYOKA_BG}%}$KYOKA_SEP"
  else
    print -n "%{%k%}"
  fi
  print -n "%{%f%}"
  KYOKA_BG=NONE
}

# ~/dotfiles/hypr -> ~/d/hypr
kyoka_short_pwd() {
  local p=${(%):-%~}
  local -a parts=("${(@s:/:)p}")
  local i
  for (( i = 1; i < ${#parts}; i++ )); do
    [[ -z ${parts[i]} || ${parts[i]} == '~' ]] && continue
    if [[ ${parts[i]} == .* ]]; then
      parts[i]=${parts[i][1,2]}
    else
      parts[i]=${parts[i][1]}
    fi
  done
  print -rn -- "${(j:/:)parts//\%/%%}"
}

kyoka_status() {
  local -a s
  (( KYOKA_RETVAL != 0 )) && s+="✘ $KYOKA_RETVAL"
  (( UID == 0 )) && s+="⚡"
  [[ -n ${jobstates} ]] && s+="⚙"
  (( ${#s} )) && kyoka_segment $K_BLOOD $K_BONE "${(j: :)s}"
}

kyoka_context() {
  [[ $USER != $KYOKA_DEFAULT_USER || -n $SSH_CONNECTION ]] &&
    kyoka_segment $K_RAISED $K_PALE '%n@%m'
}

kyoka_dir() {
  kyoka_segment $K_VIOLET $K_BONE "$(kyoka_short_pwd)"
}

kyoka_git() {
  command git rev-parse --is-inside-work-tree &>/dev/null || return
  local ref
  ref=$(command git symbolic-ref --short HEAD 2>/dev/null) ||
    ref="➦ $(command git rev-parse --short HEAD 2>/dev/null)"
  ref=${ref//\%/%%}
  if [[ -n $(command git status --porcelain --ignore-submodules=dirty 2>/dev/null | head -n1) ]]; then
    kyoka_segment $K_ICE $K_VOID "$ref ±"
  else
    kyoka_segment $K_BONE $K_VOID "$ref"
  fi
}

kyoka_build_prompt() {
  kyoka_status
  kyoka_context
  kyoka_dir
  kyoka_git
  kyoka_end
}

kyoka_precmd() { KYOKA_RETVAL=$? }
autoload -Uz add-zsh-hook
add-zsh-hook precmd kyoka_precmd

PROMPT='%{%f%b%k%}$(kyoka_build_prompt) '
RPROMPT="%F{$K_HAIR}%*%f"

# ---- completion ------------------------------------------------------
autoload -Uz compinit && compinit
zstyle ':completion:*' menu select
zstyle ':completion:*' list-colors 'ma=48;2;23;18;37;38;2;237;232;223'

# ---- plugins ---------------------------------------------------------
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=$K_HAIR"
[[ -r /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh ]] &&
  source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh

# zsh-syntax-highlighting must be sourced last, then styled.
if [[ -r /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]]; then
  source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
  ZSH_HIGHLIGHT_STYLES[command]='fg=#EDE8DF'
  ZSH_HIGHLIGHT_STYLES[builtin]='fg=#EDE8DF'
  ZSH_HIGHLIGHT_STYLES[alias]='fg=#EDE8DF'
  ZSH_HIGHLIGHT_STYLES[function]='fg=#EDE8DF'
  ZSH_HIGHLIGHT_STYLES[precommand]='fg=#EDE8DF,underline'
  ZSH_HIGHLIGHT_STYLES[path]='fg=#EDE8DF'
  ZSH_HIGHLIGHT_STYLES[single-hyphen-option]='fg=#8FD3F4'
  ZSH_HIGHLIGHT_STYLES[double-hyphen-option]='fg=#8FD3F4'
  ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg=#A98BFF'
  ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg=#A98BFF'
  ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=#C24B6B,underline'
fi

export FZF_DEFAULT_OPTS="--color=bg+:#171225,fg:#9C9489,fg+:#EDE8DF,hl:#7B4FD6,hl+:#A98BFF,pointer:#A98BFF,prompt:#A98BFF,info:#9C9489,border:#7B4FD6 --pointer='›' --border=sharp"
