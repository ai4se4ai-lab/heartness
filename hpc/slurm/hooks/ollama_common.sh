# Shared by gen.sh / oracle.sh: a private Ollama server bound to this job's GPU slice.
_port=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')
# Flash attention is on for every model except DeepSeek-V2 generators: its attention (192/128 K/V head
# sizes) decoded at 0.26 tok/s per slot with it on, versus 26-29 tok/s for Qwen/Llama/Gemma (Fir smoke
# run am-smoke-20261106-214210). The judges and embeddings keep it on.
_model=$(python3 - "$LOG_ROOT/config/experiments.resolved.json" "$STAGE" "${CELL_ID:-0}" <<'PY'
import json, sys
st = next(x for x in json.load(open(sys.argv[1]))["stages"] if x["name"] == sys.argv[2])
cells = st.get("cells") or [{}]
print(cells[int(sys.argv[3])].get("model", ""))
PY
)
OLLAMA_FLASH_ATTENTION=1
if [[ "$STAGE" == "gen" && "$_model" == deepseek* ]]; then OLLAMA_FLASH_ATTENTION=0; fi
log_info "model=$_model flash_attention=$OLLAMA_FLASH_ATTENTION"
export OLLAMA_HOST="127.0.0.1:$_port" OLLAMA_MODELS OLLAMA_KEEP_ALIVE=24h OLLAMA_FLASH_ATTENTION OLLAMA_NOPRUNE=1
export HEARTNESS_OLLAMA="http://$OLLAMA_HOST" HEARTNESS_DATA
# GPU discovery on a fresh MIG slice can exceed Ollama's 30 s watchdog; Ollama then silently falls
# back to CPU and a single 600-token call takes >10 min (Fir run am-20261107-080855, gen[0]).
# Never run on CPU: restart the server until it reports a CUDA device, else fail the cell.
_ok=0
for _try in 1 2 3; do
    _olog="$LOG_ROOT/env/ollama_${JOB_TAG}_r${SLURM_RESTART_COUNT:-0}_t${_try}.log"
    "$OLLAMA_PREFIX/bin/ollama" serve > "$_olog" 2>&1 &
    _opid=$!
    curl -sf --retry 90 --retry-delay 2 --retry-connrefused --retry-all-errors -m 5 "$HEARTNESS_OLLAMA/api/version" >/dev/null \
        || { log_error "ollama did not become ready"; kill $_opid 2>/dev/null; continue; }
    for _ in $(seq 60); do grep -q 'msg="inference compute"' "$_olog" && break; sleep 2; done
    if grep -q 'msg="inference compute".*library=CUDA' "$_olog"; then SERVICE_PIDS+=($_opid); _ok=1; break; fi
    log_error "ollama started without a GPU (try $_try): restarting"
    kill $_opid 2>/dev/null; wait $_opid 2>/dev/null; sleep 5
done
[[ $_ok == 1 ]] || { log_error "ollama found no GPU after 3 tries"; return 1; }
log_info "ollama ready at $HEARTNESS_OLLAMA (parallel=$OLLAMA_NUM_PARALLEL, loaded=$OLLAMA_MAX_LOADED_MODELS)"
