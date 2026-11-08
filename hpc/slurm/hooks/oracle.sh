# oracle stage: one judge model resident at a time (jobs are grouped by judge).
export OLLAMA_NUM_PARALLEL=2 OLLAMA_MAX_LOADED_MODELS=1   # mistral-small:24b (14 GB) + KV in 20 GB
source "$HPC_DIR/slurm/hooks/ollama_common.sh"
