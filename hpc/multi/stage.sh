#!/usr/bin/env bash
# Stage Ollama + models on clusters whose compute nodes are offline (download only, login node).
#   bash hpc/multi/stage.sh [all|names...]       starts staging in the background
#   bash hpc/multi/stage.sh --check [names...]   show staged models
set -uo pipefail
source "$(dirname "$0")/common.sh"
check=0; [[ "${1:-}" == "--check" ]] && { check=1; shift; }
for n in $(targets "$@"); do
  [[ "$(cluster_field "$n" 5)" == 1 ]] || { [[ $check == 1 ]] || echo "  - $n has internet: models are pulled by its setup job"; continue; }
  dest="$(repo_of "$n")"
  if [[ $check == 1 ]]; then
    echo "== $n"; rssh "$n" "tail -c 3000 /scratch/$REMOTE_USER/heartness-work/stage.log 2>/dev/null | tr '\r' '\n' | grep -E 'GB|success|rror' | tail -3; du -sh /scratch/$REMOTE_USER/heartness-work/ollama-models 2>/dev/null"
  else
    rssh "$n" "mkdir -p /scratch/$REMOTE_USER/heartness-work && cd $dest && nohup bash scripts/hpc/stage_offline.sh > /scratch/$REMOTE_USER/heartness-work/stage.log 2>&1 < /dev/null &" && echo "  ✔ $n staging started"
  fi
done
