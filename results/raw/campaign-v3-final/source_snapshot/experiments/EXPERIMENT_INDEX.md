# Experiment-to-evidence index

Selected campaign: `results/raw/campaign-v2-regression`.

All paper numeric macros are inserted by `scripts/build_paper_results.py` from
`results/processed/summary.json`; all graph metrics are in `trace_metrics.csv`.

| Experiment | Raw records | Derived evidence |
|---|---|---|
| E01_traceability | `results/raw/campaign-v2-regression/E01_traceability/*/*/record.json` (810) | `experiments/process.py` |
| E02_capture | `results/raw/campaign-v2-regression/E02_capture/*/*/record.json` (150) | `experiments/process.py` |
| E03_paraphrase | `results/raw/campaign-v2-regression/E03_paraphrase/*/*/record.json` (90) | `experiments/process.py` |
| E04_ablations | `results/raw/campaign-v2-regression/E04_ablations/*/*/record.json` (1) | `experiments/process.py` |
| E05_model_checking | `results/raw/campaign-v2-regression/E05_model_checking/*/*/record.json` (18) | `experiments/process.py` |
| E06_counterexamples | `results/raw/campaign-v2-regression/E06_counterexamples/*/*/record.json` (13) | `experiments/process.py` |
| E07_remediation | `results/raw/campaign-v2-regression/E07_remediation/*/*/record.json` (30) | `experiments/process.py` |
| E08_graph_scale | `results/raw/campaign-v2-regression/E08_graph_scale/*/*/record.json` (150) | `experiments/process.py` |
| E08_state_scale | `results/raw/campaign-v2-regression/E08_state_scale/*/*/record.json` (40) | `experiments/process.py` |
| E09_conformance | `results/raw/campaign-v2-regression/E09_conformance/*/*/record.json` (30) | `experiments/process.py` |
| E10_robustness | `results/raw/campaign-v2-regression/E10_robustness/*/*/record.json` (180) | `experiments/process.py` |
| E11_search | `results/raw/campaign-v2-regression/E11_search/*/*/record.json` (180) | `experiments/process.py` |
| E13_runtime_cost | `results/raw/campaign-v2-regression/E13_runtime_cost/*/*/record.json` (120) | `experiments/process.py` |
| E14_linter | `results/raw/campaign-v2-regression/E14_linter/*/*/record.json` (90) | `experiments/process.py` |
| E15_correspondence | `results/raw/campaign-v2-regression/E15_correspondence/*/*/record.json` (2) | `experiments/process.py` |
| E16_recovery | `results/raw/campaign-v2-regression/E16_recovery/*/*/record.json` (1) | `experiments/process.py` |
| E12_public_replay (supplement) | `results/raw/realistic-20261106T211001890754Z/E12_public_replay/*/*/record.json` | `experiments/realistic.py` |

Paper Table I: notation (definitions, no measured values).
Paper property/operator tables: specification (design/metamodel.md).
Paper RQ1 table and capture plot: E01/E02; RQ2 table: E05/E06;
paper scale table: E08; monitor/remediation numbers: E07/E09;
search table: E11; coverage/mutation: results/validation/*.json.
Counts, seed ranges and size/depth limits are protocol settings, not outcomes.
