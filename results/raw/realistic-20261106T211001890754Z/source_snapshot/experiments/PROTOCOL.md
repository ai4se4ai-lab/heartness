# Protocol v1 — written before experiment execution

Date: 2026-11-06. Local protocol, not externally preregistered.

RQ1: How accurately do recorded origins, derivative and withdrawal-impact sets
match construction truth, and how does missing capture affect them?
H1: full capture ties capture-only and exceeds file history and lexical recovery
on synthesis; recall decreases as capture is reduced. Factors: nine families,
sizes 16/64/256, capture 0/.25/.5/.75/1, paraphrase 0/.5/1, fan-out 1/3/6,
deployments 1/2/4, seeds 0–29. Metrics: precision/recall/F1/Jaccard and exact origin.

RQ2: Which guard faults admit reachable violations? H2: a finite independently
encoded checker and Python BFS agree on safety verdicts for the shared projection;
removing every guard need not produce a distinct failure because protections may
overlap. Measure explored states, shortest witness length, replay, seeded detection,
and negative controls. Report projection scope explicitly. Compare random search
and Hypothesis-driven search with the same time limit; timing comparisons are
exploratory because Python startup/checker compilation are separate costs.

RQ3: What are capture/query/checking costs and the observable correspondence gap?
H3: cone reduction lowers finite-state cost when unrelated artifacts exist;
observed state deviations are detectable, but hidden effects remain undetected.
Measure wall time, tracemalloc peak, monitor discrepancies, bounded search
termination and scope. Semantic output determinism excludes timings/environment.

## Campaigns

E01 family/size trace queries; E02 capture sweep; E03 paraphrase sweep;
E04 component ablations; E05 reference and mutant model checking;
E06 counterexample replay and shortestness; E07 withdrawal/rollback/external effects;
E08 structural scale and bounded state-space sweep; E09 runtime deviations;
E10 factor perturbations and leave-one-family-out summaries;
E11 equal-budget random/property-directed sequence search.

Use 30 paired seeds per stochastic configuration. Aggregate at the seed/scenario
level, never treat graph nodes or repeated timings as independent samples. Report
seed-bootstrap 95% CIs (2,000 resamples, seed 20261106), two-sided paired Wilcoxon,
paired rank-biserial effect size and independent-sample Cliff delta (explicitly
labeled descriptive), Holm correction within each baseline comparison family.
All-zero paired differences get p=1. No tuning on reporting seeds; lexical Jaccard
threshold fixed at .2. Include every executed configuration in an append-only
run manifest; interrupted/failed runs remain visible. No unmeasured headline claims.

Raw outputs use exclusive file creation in a fresh campaign directory. Store
scenario, construction oracle, outputs, elapsed/peak memory, command/environment,
source hashes and git state. Regeneration processes raw files, never edits them.

## Review-driven revision 2 (after the first campaigns)

Exploratory corrections and extensions: fix source-existence and deployment
replacement semantics in the finite model; include repeated version-producing
operations; add E15 mapped-state reference correspondence. Benchmark 1.1 introduces
dependency-only and mixed paths, distinct family motifs, actual source-count fan-out
and deployment-impact metrics. Add hand-worked oracle fixtures, targeted property
challenges, E14 measured linter comparisons, E13 absolute controller/capture scaling,
E16 recovery continuation and same-scope/time-budget BFS in E11. These are
post-review changes, not retrospectively claimed preregistration. Original raw
campaigns remain intact and are excluded from revised main summaries. Missing
human validation and operational multi-harness evidence remain external limitations.
