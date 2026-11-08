# Results — heartness run am-20261107-060101

Collected 2026-11-07 06:52:23 from `/scratch/mbabaei/heartness-work/runs/am-20261107-060101/results`.

## Tables

| table | files | rows | csv |
|---|---|---|---|
| cells | 50 | 50 | csv/cells.csv |

## Summaries

## Completeness

51/52 stage cells finished OK.

| stage | cell_id | cell | state | steps_ok | steps_total | node | elapsed | failed_steps | records_done | records_expected |
|---|---|---|---|---|---|---|---|---|---|---|
| setup | 0 | - | OK | 2 | 2 | fc11008 | 150 |  |  |  |
| gen | 0 | seed=0,model=qwen2.5-coder:7b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11017 | 649 |  |  |  |
| gen | 1 | seed=0,model=llama3.1:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11015 | 1017 |  |  |  |
| gen | 2 | seed=0,model=deepseek-coder-v2:16b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11019 | 946 |  |  |  |
| gen | 3 | seed=0,model=gemma2:9b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11008 | 1212 |  |  |  |
| gen | 4 | seed=0,model=granite3.3:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11002 | 1112 |  |  |  |
| gen | 5 | seed=1,model=qwen2.5-coder:7b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc10714 | 697 |  |  |  |
| gen | 6 | seed=1,model=llama3.1:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11004 | 943 |  |  |  |
| gen | 7 | seed=1,model=deepseek-coder-v2:16b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11011 | 1069 |  |  |  |
| gen | 8 | seed=1,model=gemma2:9b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11013 | 1167 |  |  |  |
| gen | 9 | seed=1,model=granite3.3:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11017 | 965 |  |  |  |
| gen | 10 | seed=2,model=qwen2.5-coder:7b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11019 | 602 |  |  |  |
| gen | 11 | seed=2,model=llama3.1:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11011 | 780 |  |  |  |
| gen | 12 | seed=2,model=deepseek-coder-v2:16b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11016 | 904 |  |  |  |
| gen | 13 | seed=2,model=gemma2:9b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc10714 | 1212 |  |  |  |
| gen | 14 | seed=2,model=granite3.3:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11013 | 1040 |  |  |  |
| gen | 15 | seed=3,model=qwen2.5-coder:7b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11003 | 568 |  |  |  |
| gen | 16 | seed=3,model=llama3.1:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11019 | 1082 |  |  |  |
| gen | 17 | seed=3,model=deepseek-coder-v2:16b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11008 | 1011 |  |  |  |
| gen | 18 | seed=3,model=gemma2:9b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11015 | 1211 |  |  |  |
| gen | 19 | seed=3,model=granite3.3:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11012 | 1218 |  |  |  |
| gen | 20 | seed=4,model=qwen2.5-coder:7b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11008 | 647 |  |  |  |
| gen | 21 | seed=4,model=llama3.1:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11002 | 931 |  |  |  |
| gen | 22 | seed=4,model=deepseek-coder-v2:16b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11014 | 1166 |  |  |  |
| gen | 23 | seed=4,model=gemma2:9b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11019 | 940 |  |  |  |
| gen | 24 | seed=4,model=granite3.3:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11004 | 1149 |  |  |  |
| oracle | 0 | seed=0,model=qwen2.5-coder:7b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11017 | 108 |  |  |  |
| oracle | 1 | seed=0,model=llama3.1:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11017 | 129 |  |  |  |
| oracle | 2 | seed=0,model=deepseek-coder-v2:16b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11017 | 107 |  |  |  |
| oracle | 3 | seed=0,model=gemma2:9b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11017 | 115 |  |  |  |
| oracle | 4 | seed=0,model=granite3.3:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11012 | 121 |  |  |  |
| oracle | 5 | seed=1,model=qwen2.5-coder:7b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11013 | 108 |  |  |  |
| oracle | 6 | seed=1,model=llama3.1:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11016 | 143 |  |  |  |
| oracle | 7 | seed=1,model=deepseek-coder-v2:16b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11011 | 171 |  |  |  |
| oracle | 8 | seed=1,model=gemma2:9b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11013 | 137 |  |  |  |
| oracle | 9 | seed=1,model=granite3.3:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11017 | 137 |  |  |  |
| oracle | 10 | seed=2,model=qwen2.5-coder:7b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11002 | 116 |  |  |  |
| oracle | 11 | seed=2,model=llama3.1:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11017 | 115 |  |  |  |
| oracle | 12 | seed=2,model=deepseek-coder-v2:16b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11017 | 95 |  |  |  |
| oracle | 13 | seed=2,model=gemma2:9b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11019 | 125 |  |  |  |
| oracle | 14 | seed=2,model=granite3.3:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11008 | 112 |  |  |  |
| oracle | 15 | seed=3,model=qwen2.5-coder:7b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11003 | 87 |  |  |  |
| oracle | 16 | seed=3,model=llama3.1:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11017 | 115 |  |  |  |
| oracle | 17 | seed=3,model=deepseek-coder-v2:16b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11008 | 121 |  |  |  |
| oracle | 18 | seed=3,model=gemma2:9b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11015 | 124 |  |  |  |
| oracle | 19 | seed=3,model=granite3.3:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11012 | 143 |  |  |  |
| oracle | 20 | seed=4,model=qwen2.5-coder:7b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11017 | 109 |  |  |  |
| oracle | 21 | seed=4,model=llama3.1:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11019 | 129 |  |  |  |
| oracle | 22 | seed=4,model=deepseek-coder-v2:16b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11014 | 117 |  |  |  |
| oracle | 23 | seed=4,model=gemma2:9b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11015 | 114 |  |  |  |
| oracle | 24 | seed=4,model=granite3.3:8b,benchmark=humaneval,policy=expel | OK | 1 | 1 | fc11004 | 136 |  |  |  |
| collect | 0 | - | RUNNING | 1 | 2 | fc11004 | 21 |  |  |  |

