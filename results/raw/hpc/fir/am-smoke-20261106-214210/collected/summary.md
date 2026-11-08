# Results — heartness run am-smoke-20261106-214210 (SMOKE: not for reporting)

Collected 2026-11-06 22:45:37 from `/scratch/mbabaei/heartness-work/runs/am-smoke-20261106-214210/results`.

## Tables

| table | files | rows | csv |
|---|---|---|---|
| cells | 8 | 8 | csv/cells.csv |

## Summaries

## Completeness

9/10 stage cells finished OK.

| stage | cell_id | cell | state | steps_ok | steps_total | node | elapsed | failed_steps | records_done | records_expected |
|---|---|---|---|---|---|---|---|---|---|---|
| setup | 0 | - | OK | 2 | 2 | fc11008 | 129 |  |  |  |
| gen | 0 | seed=0,model=qwen2.5-coder:7b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11004 | 84 |  |  |  |
| gen | 1 | seed=0,model=llama3.1:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11004 | 19 |  |  |  |
| gen | 2 | seed=0,model=deepseek-coder-v2:16b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11004 | 602 |  |  |  |
| gen | 3 | seed=0,model=gemma2:9b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11004 | 26 |  |  |  |
| oracle | 0 | seed=0,model=qwen2.5-coder:7b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc10910 | 22 |  |  |  |
| oracle | 1 | seed=0,model=llama3.1:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc10910 | 18 |  |  |  |
| oracle | 2 | seed=0,model=deepseek-coder-v2:16b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11004 | 128 |  |  |  |
| oracle | 3 | seed=0,model=gemma2:9b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11004 | 18 |  |  |  |
| collect | 0 | - | RUNNING | 1 | 2 | fc11004 | 20 |  |  |  |

