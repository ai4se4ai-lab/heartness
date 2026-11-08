# gen stage: generator + embedding model resident; four runs share the server.
export OLLAMA_NUM_PARALLEL=4 OLLAMA_MAX_LOADED_MODELS=2   # 4 slots x 8k ctx fits gemma2:9b in 20 GB
source "$HPC_DIR/slurm/hooks/ollama_common.sh"
