#!/usr/bin/env bash
# Push code (never results) to clusters and install each cluster's experiment-graph variant
# (hpc/config/experiments.<cluster>.json -> experiments.json), then run the selftest there.
#   bash hpc/multi/sync.sh [all|names...]
set -uo pipefail
source "$(dirname "$0")/common.sh"
cd "$REPO_LOCAL"
for n in $(targets "$@"); do
  alive "$n" || { echo "  ✘ $n not connected (bash hpc/multi/connect.sh $n)"; continue; }
  dest="$(repo_of "$n")"
  rssh "$n" "mkdir -p $dest"
  rsync -az --delete -e "ssh -o ControlPath=$(sock_of "$n")" \
    --include='build/' --include='build/data/' --include='build/data/*.jsonl' \
    --include='build/data/MANIFEST.json' --exclude='build/**' \
    --exclude='.venv/' --exclude='results/' --exclude='.git/' --exclude='__pycache__/' \
    --exclude='.mypy_cache/' --exclude='.ruff_cache/' --exclude='.pytest_cache/' \
    --exclude='.hypothesis/' --exclude='.coverage' --exclude='hpc/logs/' --exclude='docs/' \
    --exclude='reviews/' --exclude='hpc/multi/runs.tsv' --exclude='hpc/multi/status.*' \
    ./ "${REMOTE_USER}@$(host_of "$n"):$dest/" || { echo "  ✘ $n rsync failed"; continue; }
  echo "  ✔ $n synced: $(rssh "$n" "cd $dest && cp hpc/config/experiments.$n.json hpc/config/experiments.json && bash hpc/scripts/selftest.sh 2>&1 | tail -1")"
done
