# Results — heartness run am-smoke-20261106-234213 (SMOKE: not for reporting)

Collected 2026-11-07 01:17:20 from `/scratch/mbabaei/heartness-work/runs/am-smoke-20261106-234213/results`.

## Tables

| table | files | rows | csv |
|---|---|---|---|
| cells | 8 | 8 | csv/cells.csv |

## Summaries

## Completeness

9/10 stage cells finished OK.

| stage | cell_id | cell | state | steps_ok | steps_total | node | elapsed | failed_steps | records_done | records_expected |
|---|---|---|---|---|---|---|---|---|---|---|
| setup | 0 | - | OK | 2 | 2 | rg12603 | 108 |  |  |  |
| gen | 0 | seed=0,model=qwen2.5-coder:7b,benchmark=mbpp,policy=expel | OK | 1 | 1 | rg12603 | 309 |  |  |  |
| gen | 1 | seed=0,model=llama3.1:8b,benchmark=mbpp,policy=expel | OK | 1 | 1 | rg12801 | 740 |  |  |  |
| gen | 2 | seed=0,model=deepseek-coder-v2:16b,benchmark=mbpp,policy=expel | OK | 1 | 1 | rg12703 | 715 |  |  |  |
| gen | 3 | seed=0,model=gemma2:9b,benchmark=mbpp,policy=expel | OK | 1 | 1 | rg13102 | 513 |  |  |  |
| oracle | 0 | seed=0,model=qwen2.5-coder:7b,benchmark=mbpp,policy=expel | OK | 1 | 1 | rg12603 | 254 |  |  |  |
| oracle | 1 | seed=0,model=llama3.1:8b,benchmark=mbpp,policy=expel | OK | 1 | 1 | rg12603 | 108 |  |  |  |
| oracle | 2 | seed=0,model=deepseek-coder-v2:16b,benchmark=mbpp,policy=expel | OK | 1 | 1 | rg12703 | 145 |  |  |  |
| oracle | 3 | seed=0,model=gemma2:9b,benchmark=mbpp,policy=expel | OK | 1 | 1 | rg12801 | 279 |  |  |  |
| collect | 0 | - | RUNNING | 1 | 2 | rg12501 | 29 |  |  |  |

