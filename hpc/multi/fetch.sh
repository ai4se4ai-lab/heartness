#!/usr/bin/env bash
# Copy a run's results (raw records, oracle labels, LLM caches, collected outputs) and logs
# back to this machine: results/raw/hpc/<cluster>/<RUN_ID>/ and hpc/logs/<cluster>/<RUN_ID>/.
#   bash hpc/multi/fetch.sh [all|names...]      latest recorded full run per cluster
#   RUN_KIND=smoke bash hpc/multi/fetch.sh ...  latest smoke run instead
set -uo pipefail
source "$(dirname "$0")/common.sh"
kind="${RUN_KIND:-full}"
for n in $(targets "$@"); do
  run=$(awk -F'\t' -v n="$n" -v k="$kind" '$2==n && $4==k {r=$3} END {print r}' "$MULTI_DIR/runs.tsv" 2>/dev/null)
  [[ -n "$run" ]] || { echo "  - $n: no $kind run recorded"; continue; }
  alive "$n" || { echo "  ✘ $n not connected"; continue; }
  work=$(rssh "$n" "cd $(repo_of "$n") && set -a && CC_CLUSTER=$n source hpc/config/cluster.env && echo \$WORK")
  mkdir -p "$REPO_LOCAL/results/raw/hpc/$n/$run" "$REPO_LOCAL/hpc/logs/$n/$run"
  rsync -az -e "ssh -o ControlPath=$(sock_of "$n")" "${REMOTE_USER}@$(host_of "$n"):$work/runs/$run/results/" "$REPO_LOCAL/results/raw/hpc/$n/$run/" \
    && rsync -az -e "ssh -o ControlPath=$(sock_of "$n")" "${REMOTE_USER}@$(host_of "$n"):$(repo_of "$n")/hpc/logs/$run/" "$REPO_LOCAL/hpc/logs/$n/$run/" \
    && echo "  ✔ $n $run -> results/raw/hpc/$n/$run"
done
