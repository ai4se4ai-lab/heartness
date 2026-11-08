# Round 6 response

Reviewers: R1 minor (N3/R4/Rel4/V4/P4); R2 minor (N3/R3/Rel4/V4/P3); R3 minor (N3/R4/Rel4/V4/P4).
Internal automated review, not peer review.

## New analysis (R1 novelty: "evidence that closure is clearly more selective than a time cut under late faults")

Oracle-free structural selectivity (`process.selectivity`, Table "Structural selectivity"): every
revision active at the end of each of the 200 runs is taken as a hypothetical root; we report the
mean share of revisions written at later tasks that fall in its closure, by the root's task.
Revisions written in the same step as the root are excluded: a first version that counted them made
ExpeL look selective for late roots (0.46), but that came entirely from sibling insights of one
extraction step (against later tasks the ExpeL ratio is 1.00 everywhere). Curation: 0.92 / 0.94 /
0.46 / 0.61 for roots at tasks 1-6 / 7-12 / 13-18 / 19-24 (strictly fewer for 43/56/97/95% of
roots); EME-fail lowers 7-12 to 0.63. Reported in E-L, intro, Lessons, conclusion and RQ1 box,
with the caveat that it measures sparing, not cleanliness.

## Code

| Request | Action |
|---|---|
| R1.R1 revalidated copies still lose lineage (two probes) | Dropped sources and experience contexts are replaced by their *active frontier* (nearest active ancestors outside Cl(F)); two tests reproduce the reviewer's cases A and B. |
| R3.2 superseded revision could return beside its successor | Candidates restricted to revisions in use (active or deployed) before the withdrawal, in the engine and in the evaluation; test added. No data change (300/300 recorded plans reproduced). |
| R3 attestation admitted only when needed | Algorithm 5 now says so; attestation records <R, phi, C>. |
| Stale docstrings | `revalidation.py` and `supplement.py` rewritten to match the code. |
| R2 folded-miss counts | `missed_runs_composed` (22/12/1 skill-or-profile miss runs) used in abstract, RQ1 box, Lessons. |

## Paper

| Request | Action |
|---|---|
| R2.R1 / R3.4 "clearly higher F1 under both policies"; "barely more precise" | "Under curation ... significantly higher F1"; "suspended almost as much as rollback". |
| R2 abstract implies 52 ⊂ 74; oracle not named | Abstract now: an LLM-judge oracle found the fault in the root in 74 runs and in further revisions in 52. |
| R2.R3 setup vs threats | Setup paragraph now states H_EME-fail as post hoc and the revalidation re-evaluation; result paragraph marks H_EME-fail post hoc. |
| R2 minors | H vs R3 collateral test reported; HS_judge differs from R4 in 11 of 42 (macro); TF-IDF sentence reworded; curation noise as percentage. |
| R1.R2 / R3.1 Definition 8 | State tuple uses Q_acc, Θ, X; withdraw of a revision or an experience. Copy map renamed ν (no clash with mutant μ or policy π). |
| R1.R3 plan vs guards | Stated why admission guards cannot bind on copies in the live records. |
| R1.R4 projection limits | Experience withdrawal and revalidation listed as outside the projection and the mutation campaign (unit tests only). |
| R3.3 "line 12" | Correct: the PDF omits end-procedure lines; changed to line 10. |
| R3 minors | Overview text mentions (10); acronym expansion removed (it did not spell the name); "at frozen settings"; revalidation.py in the module list; Definition 6 covers experience withdrawal; H_local "cannot remove deployed copies". |

## Not done

- Human oracle audit; anonymized artifact link; Table XI font (resizebox kept for width).
- Mid-evolution withdrawal experiment and mechanized proof (R1 novelty options 2 and 3); option 1 addressed by the selectivity analysis.
- Further paragraph splitting (length remains 23 pages).
