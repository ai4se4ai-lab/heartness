#!/usr/bin/env bash
# Kept for backward compatibility: use hpc/multi/connect.sh (all clusters, or named ones).
exec bash "$(dirname "$0")/../../hpc/multi/connect.sh" "$@"
