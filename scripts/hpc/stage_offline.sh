#!/usr/bin/env bash
# Stage the pinned Ollama release and model tags on a cluster whose compute nodes have no
# internet (Narval). Run on the LOGIN node (download only; no inference):
#   bash scripts/hpc/stage_offline.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
set -a; source hpc/config/cluster.env; set +a
MODELS=$(python3 -c 'import json;print(json.load(open("hpc/config/experiments.json"))["vars"]["PULL_MODELS"])')
mkdir -p "$OLLAMA_PREFIX" "$OLLAMA_MODELS"
if [[ ! -x "$OLLAMA_PREFIX/bin/ollama" ]]; then
  tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
  curl -fL --retry 5 -o "$tmp/ollama.tar.zst" \
    "https://github.com/ollama/ollama/releases/download/${OLLAMA_VERSION}/ollama-linux-amd64.tar.zst"
  zstd -dc "$tmp/ollama.tar.zst" | tar -x -C "$OLLAMA_PREFIX"
fi
port=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')
export OLLAMA_HOST="127.0.0.1:$port" OLLAMA_MODELS OLLAMA_NOPRUNE=1 CUDA_VISIBLE_DEVICES=""
nice -n 10 "$OLLAMA_PREFIX/bin/ollama" serve > "$WORK/ollama_stage.log" 2>&1 &
pid=$!; trap 'kill $pid 2>/dev/null || true' EXIT
curl -sf --retry 60 --retry-delay 2 --retry-connrefused -m 5 "http://$OLLAMA_HOST/api/version" >/dev/null
for m in $MODELS; do nice -n 10 "$OLLAMA_PREFIX/bin/ollama" pull "$m"; done
"$OLLAMA_PREFIX/bin/ollama" list
