#!/usr/bin/env bash
# (Re)open MFA-authenticated SSH master connections that every other hpc/multi command reuses.
#   bash hpc/multi/connect.sh                 all clusters (one MFA prompt per cluster not yet connected)
#   bash hpc/multi/connect.sh fir rorqual     selected clusters
#   bash hpc/multi/connect.sh --check         show which connections are alive (no prompts)
#   bash hpc/multi/connect.sh --close [names] close connections
set -uo pipefail
source "$(dirname "$0")/common.sh"
mkdir -p "$SOCK_DIR" && chmod 700 "$SOCK_DIR"
mode=open
case "${1:-}" in --check) mode=check; shift ;; --close) mode=close; shift ;; esac
for n in $(targets "$@"); do
  host="$(host_of "$n")"; sock="$(sock_of "$n")"
  case $mode in
    check) if alive "$n"; then echo "  ✔ $n  connected"; else echo "  ✘ $n  not connected"; fi ;;
    close) ssh -o ControlPath="$sock" -O exit "${REMOTE_USER}@$host" 2>/dev/null && echo "  closed $n" ;;
    open)
      if alive "$n"; then echo "  ✔ $n  already connected"; continue; fi
      # a socket left by a reboot or a dead master blocks a new master from listening
      if [[ -S "$sock" ]]; then pkill -f "ControlPath=$sock" 2>/dev/null; rm -f -- "$sock"; fi
      echo "  → $n ($host): approve the MFA prompt"
      if ssh -o ControlMaster=yes -o ControlPath="$sock" -o ControlPersist=12h \
             -o ServerAliveInterval=60 -fN "${REMOTE_USER}@$host" && alive "$n"; then
        echo "  ✔ $n  connected (reused for up to 12 h of inactivity)"
      else
        echo "  ✘ $n  failed; re-run: bash hpc/multi/connect.sh $n"
      fi ;;
  esac
done
