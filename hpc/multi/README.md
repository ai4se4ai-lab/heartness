# hpc/multi — one pipeline, four Alliance clusters

The use-hpc pipeline in `hpc/` runs unchanged on every cluster; this layer splits the
experiment matrix across clusters, reconnects to all of them at once, and federates the
use-hpc audit into one dashboard. Clusters and their matrix slices are in `clusters.tsv`:

| cluster | GPUs (requested slice) | slice of the matrix | compute-node internet |
|---|---|---|---|
| nibi    | H100 (`h100_2g.20gb`) | HumanEval+ x curate | yes |
| narval  | A100 (`a100_3g.20gb`) | MBPP+ x curate      | no: models staged from login node |
| fir     | H100 (`h100_2g.20gb`) | HumanEval+ x ExpeL  | yes |
| rorqual | H100 (`h100_2g.20gb`) | MBPP+ x ExpeL       | no: models staged from login node |

Every remedy comparison happens inside one cell (one cluster, one GPU type); records store
host, cluster and GPU name. Per-cluster graphs: `hpc/config/experiments.<cluster>.json`;
per-cluster storage and offline mode: `hpc/config/cluster.env` (branches on `$CC_CLUSTER`).

## Daily use

```bash
bash hpc/multi/connect.sh                 # reconnect all (one MFA prompt per dead connection)
bash hpc/multi/connect.sh --check         # which connections are alive
python3 hpc/multi/status.py               # federated audit: one summary per cluster and stage
python3 hpc/multi/status.py --full        # + every cluster's complete use-hpc audit table
python3 hpc/multi/status.py --only failed # only failed rows, with reasons and log tails
python3 hpc/multi/status.py --watch 300   # live (minimum 120 s)
```

## Lifecycle

```bash
bash hpc/multi/sync.sh all                # push code + install each cluster's graph + selftest
bash hpc/multi/stage.sh all               # offline clusters: download Ollama + models (login node)
bash hpc/multi/stage.sh --check           # staging progress
bash hpc/multi/submit.sh --dry-run all
bash hpc/multi/submit.sh --smoke all      # records RUN_IDs in hpc/multi/runs.tsv
bash hpc/multi/submit.sh --full all       # the real run (only after the smoke runs pass)
bash hpc/multi/submit.sh --full nibi -- --run-id <ID> --only oracle   # repair one stage
bash hpc/multi/fetch.sh all               # results -> results/raw/hpc/<cluster>/<RUN_ID>/
```

`status.py` only reads (one `squeue` + one `sacct` per cluster per refresh, via each
cluster's own `hpc/scripts/audit.py`); it writes `hpc/multi/status.txt` / `status.json`.
