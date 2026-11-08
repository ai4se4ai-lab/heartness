# Results — heartness run am-smoke-20261107-002031 (SMOKE: not for reporting)

Collected 2026-11-07 00:52:13 from `/scratch/mbabaei/heartness-work/runs/am-smoke-20261107-002031/results`.

## Tables

| table | files | rows | csv |
|---|---|---|---|
| cells | 8 | 8 | csv/cells.csv |

## Summaries

## Completeness

9/10 stage cells finished OK.

| stage | cell_id | cell | state | steps_ok | steps_total | node | elapsed | failed_steps | records_done | records_expected |
|---|---|---|---|---|---|---|---|---|---|---|
| setup | 0 | - | OK | 2 | 2 | ng20404 | 125 |  |  |  |
| gen | 0 | seed=0,model=qwen2.5-coder:7b,benchmark=mbpp,policy=curate | OK | 1 | 1 | ng20404 | 408 |  |  |  |
| gen | 1 | seed=0,model=llama3.1:8b,benchmark=mbpp,policy=curate | OK | 1 | 1 | ng30304 | 802 |  |  |  |
| gen | 2 | seed=0,model=deepseek-coder-v2:16b,benchmark=mbpp,policy=curate | OK | 1 | 1 | ng30404 | 946 |  |  |  |
| gen | 3 | seed=0,model=gemma2:9b,benchmark=mbpp,policy=curate | OK | 1 | 1 | ng30504 | 571 |  |  |  |
| oracle | 0 | seed=0,model=qwen2.5-coder:7b,benchmark=mbpp,policy=curate | OK | 1 | 1 | ng20404 | 200 |  |  |  |
| oracle | 1 | seed=0,model=llama3.1:8b,benchmark=mbpp,policy=curate | OK | 1 | 1 | ng20404 | 192 |  |  |  |
| oracle | 2 | seed=0,model=deepseek-coder-v2:16b,benchmark=mbpp,policy=curate | OK | 1 | 1 | ng20503 | 236 |  |  |  |
| oracle | 3 | seed=0,model=gemma2:9b,benchmark=mbpp,policy=curate | OK | 1 | 1 | ng20503 | 212 |  |  |  |
| collect | 0 | - | RUNNING | 1 | 2 | ng20404 | 29 |  |  |  |

