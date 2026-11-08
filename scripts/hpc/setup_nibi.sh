#!/usr/bin/env bash
# Setup stage (runs inside a Slurm job on a GPU node with internet; idempotent).
#   - installs a pinned Ollama release into $OLLAMA_PREFIX
#   - pulls the pinned model tags into $OLLAMA_MODELS and records their digests
#   - verifies the shipped HumanEval+ / MBPP+ JSONL files against their pinned checksums
#   - re-validates canonical solutions (exclusion list) and writes $1/setup/verify.json
set -euo pipefail
OUT="$1"; shift
MODELS_LIST="$*"
mkdir -p "$OUT/setup" "$OLLAMA_PREFIX" "$OLLAMA_MODELS" "$HEARTNESS_DATA"

if [[ "${OFFLINE:-0}" == 1 && ! -x "$OLLAMA_PREFIX/bin/ollama" ]]; then
  echo "OFFLINE cluster: stage Ollama and models first (scripts/hpc/stage_offline.sh)" >&2; exit 3
fi
if [[ ! -x "$OLLAMA_PREFIX/bin/ollama" ]]; then
  url="https://github.com/ollama/ollama/releases/download/${OLLAMA_VERSION}/ollama-linux-amd64.tar.zst"
  curl -fL --retry 5 -o "$SLURM_TMPDIR/ollama.tar.zst" "$url"
  zstd -dc "$SLURM_TMPDIR/ollama.tar.zst" | tar -x -C "$OLLAMA_PREFIX"
fi
"$OLLAMA_PREFIX/bin/ollama" -v

port=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')
export OLLAMA_HOST="127.0.0.1:$port"
"$OLLAMA_PREFIX/bin/ollama" serve > "$OUT/setup/ollama_setup.log" 2>&1 &
pid=$!
trap 'kill $pid 2>/dev/null || true' EXIT
curl -sf --retry 90 --retry-delay 2 --retry-connrefused --retry-all-errors -m 5 \
  "http://$OLLAMA_HOST/api/version" > /dev/null
for m in $MODELS_LIST; do
  if [[ "${OFFLINE:-0}" == 1 ]]; then   # verify the staged model instead of pulling
    "$OLLAMA_PREFIX/bin/ollama" show "$m" > /dev/null || { echo "model $m not staged" >&2; exit 4; }
  else
    "$OLLAMA_PREFIX/bin/ollama" pull "$m"
  fi
done
echo "[setup] all models present; recording digests"
curl -sS --fail "http://$OLLAMA_HOST/api/tags" -o "$OUT/setup/model_digests.json" \
  || { echo "[setup] FAILED to read model digests (ollama server down?)" >&2; exit 5; }

# Datasets are shipped as JSONL conversions of pinned EvalPlus parquet files (no pyarrow on the
# cluster); verify them against the manifest written when they were converted.
echo "[setup] verifying datasets"
python - "$HEARTNESS_DATA" "$OUT/setup/data_sha256.json" <<'PY'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1]); man = json.loads((root / "MANIFEST.json").read_text())
got = {k: hashlib.sha256((root / f"{k}.jsonl").read_bytes()).hexdigest() for k in man}
assert all(got[k] == v["jsonl_sha256"] for k, v in man.items()), got
json.dump({"manifest": man, "verified": got}, open(sys.argv[2], "w"), indent=1)
PY

echo "[setup] validating canonical solutions"
python - "$OUT/setup/verify.json" <<'PY'
import json, sys
from concurrent.futures import ThreadPoolExecutor
from experiments.live.tasks import EXCLUDED, load_tasks, run_tests
import os
workers = max(1, len(os.sched_getaffinity(0)))   # cores actually granted to this job
report = {}
for bench in ("humaneval", "mbpp"):
    tasks = load_tasks(bench)
    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(lambda t: (t.id, *run_tests(t.prompt + t.canonical if not t.direct
                                                       else t.canonical, t)), tasks))
    failed = sorted(i for i, ok, _ in res if not ok)
    report[bench] = {"tasks": len(tasks), "workers": workers, "canonical_failures": failed,
                     "unexpected": sorted(set(failed) - EXCLUDED),
                     "messages": {i: m for i, ok, m in res if not ok}}
json.dump(report, open(sys.argv[1], "w"), indent=1)
print(report)
assert not any(v["unexpected"] for v in report.values()), "unexpected canonical failures"
PY
