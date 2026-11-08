#!/usr/bin/env bash
# Submit the pipeline on clusters and record each RUN_ID in hpc/multi/runs.tsv (local ledger).
#   bash hpc/multi/submit.sh --smoke [all|names...]     end-to-end smoke test
#   bash hpc/multi/submit.sh --full  [all|names...]     the real run (ask before using it)
#   bash hpc/multi/submit.sh --dry-run [all|names...]
#   extra submit.py options after "--", e.g.  -- --run-id <ID> --only collect
set -uo pipefail
source "$(dirname "$0")/common.sh"
kind="${1:-}"; shift || true
case "$kind" in --smoke) flag="--smoke" ;; --full) flag="" ;; --dry-run) flag="--dry-run" ;;
  *) echo "usage: submit.sh --smoke|--full|--dry-run [clusters] [-- submit.py options]"; exit 2 ;; esac
names=(); extra=()
while [[ $# -gt 0 ]]; do [[ "$1" == "--" ]] && { shift; extra=("$@"); break; }; names+=("$1"); shift; done
ledger="$MULTI_DIR/runs.tsv"
[[ -f "$ledger" ]] || printf "submitted\tcluster\trun_id\tkind\n" > "$ledger"
for n in $(targets "${names[@]}"); do
  alive "$n" || { echo "  ✘ $n not connected (bash hpc/multi/connect.sh $n)"; continue; }
  out=$(rssh "$n" "cd $(repo_of "$n") && python3 hpc/slurm/submit.py $flag ${extra[*]:-} 2>&1")
  run=$(grep -oE 'RUN_ID [^ ]+' <<<"$out" | head -1 | cut -d' ' -f2)
  echo "== $n"; grep -E 'RUN_ID|job |rror|refus' <<<"$out" | sed 's/^/   /'
  if [[ -n "$run" && "$kind" != "--dry-run" ]]; then
    printf "%s\t%s\t%s\t%s\n" "$(date '+%F %T')" "$n" "$run" "${kind#--}" >> "$ledger"
  fi
done
