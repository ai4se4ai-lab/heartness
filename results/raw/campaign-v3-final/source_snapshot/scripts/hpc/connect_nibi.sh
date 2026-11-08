#!/usr/bin/env bash
# Open one MFA-authenticated SSH master connection to Nibi that later commands reuse.
# Run this yourself in a terminal (it will prompt for MFA). Close it with:
#   bash scripts/hpc/connect_nibi.sh --close
set -euo pipefail
USER_REMOTE="${NIBI_USER:-mbabaei}"
HOST="nibi.alliancecan.ca"
SOCK_DIR="$HOME/.ssh/controlmasters"
SOCK="$SOCK_DIR/${USER_REMOTE}@${HOST}:22"
mkdir -p "$SOCK_DIR" && chmod 700 "$SOCK_DIR"

if [[ "${1:-}" == "--close" ]]; then
  ssh -o ControlPath="$SOCK" -O exit "${USER_REMOTE}@${HOST}" && echo "closed"
  exit 0
fi

if ssh -o ControlPath="$SOCK" -O check "${USER_REMOTE}@${HOST}" 2>/dev/null; then
  echo "A master connection is already open: $SOCK"
  exit 0
fi

# A socket left over from a reboot or a dead master blocks a new master from listening:
# stop any master for this path that is not answering, and remove the stale socket.
if [[ -S "$SOCK" ]]; then
  echo "Removing stale control socket $SOCK"
  pkill -f "ControlPath=$SOCK" 2>/dev/null || true
  rm -f -- "$SOCK"
fi

echo "Opening master connection to ${USER_REMOTE}@${HOST} (approve the MFA prompt)..."
ssh -o ControlMaster=yes -o ControlPath="$SOCK" -o ControlPersist=12h \
    -o ServerAliveInterval=60 -fN "${USER_REMOTE}@${HOST}"
ssh -o ControlPath="$SOCK" -O check "${USER_REMOTE}@${HOST}"
echo "Ready. Socket: $SOCK (valid up to 12 h of inactivity; re-run to reopen)."
