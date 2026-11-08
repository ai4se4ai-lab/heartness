# Round 8 response

Reviewers: R1 accept (N4/R4/Rel4/V4/P4); R2 minor (N3/R3/Rel4/V4/P4); R3 minor (N3/R4/Rel4/V4/P4).
Internal automated review.

## New experiment (R2, R3: what would earn Novelty/Rigor 4)

Both reviewers named the same experiment: planted faults after the first composition under
curation, scored by the oracle. Launched on Fir (run am-20261107-192325): curation, HumanEval+,
fault at evolution task 15 (`--fault-index 14`, new option of run.py/cell.py), qwen2.5-coder:7b,
llama3.1:8b, gemma2:9b x 5 seeds = 15 cells (45 faulty + 15 clean runs); same harness, thresholds,
judges and revalidation. Results: pending.

## Code

| Request | Action |
|---|---|
| R1.N1 clean experience of a dropped intermediate lost (probe E) | The clean frontier now also returns the motivating experiences of forbidden intermediates that are not withdrawn and whose run context avoided Cl(F); the copy keeps them. Probe E added as a test (60 tests). |
| R1/R2/R3 stale name | `active_frontier` renamed `clean_frontier`; comments fixed. |
| R2 traceability of the window effect and absolute sparing | `selectivity` now records mean later revisions, mean spared, and how many roots reach the final composition's profiles (1,200/1,200 late curation roots); macros used in E-L. |
| R3 stale validation macros | `make validate` then macros regenerated (TestCount 60). |

## Paper

| Request | Action |
|---|---|
| R2 required: hypothetical vs real fault | E-L states the assumption (a fault would leave the recorded exposure structure unchanged); "later faults" replaced by "revisions created after the first composition ... until the next composition" in E-L, RQ1 box and conclusion. |
| R2 absolute sparing | 6.2 of 11.9 and 2.5 of 6.0 later revisions (macros). |
| R2 F1 sentence | Split; says whose F1 is higher. |
| R3 Algorithm 4 / affected set | Clause: Z ∩ (Act ∪ ⋃Dpl) is Definition 5's affected set reported in (7). |
| R3 Definition 4 transitive; "admissible" in Algorithm 5 | Added; Algorithm 5 condition spelled out. |
| R3 abstract wording | "found the practice planted by one corrupted feedback message". |
| R1 cosmetic | Selectivity table no longer overfull; "sixth internal review round" reworded. |

## Not done

- Human oracle audit (needs human labels).
- Mid-evolution withdrawal experiment.
