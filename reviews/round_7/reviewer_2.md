# Round 7 -- Reviewer 2 (empirical rigor and verifiability)

Paper: docs/TSE/main.tex and main.pdf (tex 19:11:11, PDF 19:11:12, so the PDF is current; 24 pages, no `??` and no undefined references). Line numbers refer to main.tex. New scratch work is in `/tmp/claude-1000/r7rev2/`; I reused my round-5 and round-6 scripts unchanged.

## Summary

This round makes these changes:
- It adds an oracle-free "structural selectivity" analysis (`process.selectivity`, Table `tab:selectivity`, E-L paragraph L2311). The analysis takes every final active revision as a hypothetical root and compares its closure with the revisions written at later tasks.
- It carries the analysis into the introduction (L1743), the RQ1 box (L2361), Lessons (L2459) and the conclusion (L2523).
- It makes the three prose corrections I required in round 6 and most of my minor points.

**Verification.**
- **Raw data.** No file under `results/raw/` has changed since round 6.
- **Pipeline.** I re-ran `experiments.live.process report` from a scratch directory. Both `live_runs.csv` files are byte-identical to the shipped ones. Both `live_summary.json` files are identical apart from the `campaign` path, and that includes the new `selectivity` block.
- **Supplements.** The current `supplement.restore`, after the in-use-candidate change, still reproduces all 300 shipped revalidation plans (`supp_check.py`).
- **Tests.** `tests/test_revalidation.py` and `tests/test_eme.py` pass (19 tests).
- **Selectivity.** I recomputed the selectivity table from raw JSON with my own code (`r7rev2/sel.py`). It uses its own closure, and it takes EME-fail from `experiences[e].outcome` instead of `evolution[i].passed`; the two sources agree on every run. My output matches the table exactly, cell for cell.
- **Macro index.** `paper_macro_index.json` maps all the new macros to `live_summary.json`.

**Outcome.** The definition is sound, and the same-step exclusion is principled and conservative. Every number is correct. One calibration problem remains:
- The introduction, E-L and Lessons quote 0.46 for "roots/a fault after the first composition".
- 0.46 is the most favourable block (tasks 13-18). It also mixes in skill roots, which are never fault roots in this design.
- For roots at tasks 19-24 the figure is 0.61. Pooled over tasks 13-24 it is 0.52, and for memory roots it is 0.50 and 0.61.
- The analysis was also added after the round-6 review, and its definition was revised once after a first version gave an artefactual result (response.md). The paper's Threats section does not say so, although it carefully does so for H_EME-fail.

## Scores

| Criterion | Score (1-5) | Justification |
|---|---|---|
| Novelty | 3 | Unchanged. The lifecycle formulation is new and useful. The selectivity analysis sharpens the interpretation but adds no new mechanism. |
| Rigor | 3 | All round-6 required changes were made. The new analysis has a sound, conservative definition and reproduces exactly. Still limiting: no human validation of the LLM-judge oracle that defines every recall number (declined again); an effective n of 10 under the ExpeL-style policy; and the selectivity result for later faults is counterfactual and post hoc, and is not yet disclosed as such. |
| Relevance | 4 | Unchanged. |
| Verifiability and Transparency | 4 | Pipeline output is byte-identical, the supplements reproduce from current code, and the new macros are indexed to their source. The response openly describes the revised selectivity definition, but the paper does not (R2). `environment.git` is still empty (accepted earlier). |
| Presentation | 4 | The summaries are now calibrated on F1, miss counts, oracle naming and post-hoc status. Remaining: the 0.46 quote (R1) and the still-convoluted F1 sentence at L2292. |

## Status of round-6 issues

| Round-6 issue | Status | Evidence |
|---|---|---|
| **R1** "clearly higher F1 under both policies" | **Fixed** | RQ1 box (L2361): "under curation TF-IDF and the LLM judge had significantly higher F1". Abstract (L1718): "under curation ... clearly higher F1". Both are tied to curation, consistent with the ExpeL non-significance. |
| **R2** folded-miss counts | **Fixed** | A new `missed_runs_composed` field gives R3 22, R4 12, R2 1 (macros `LiveCMissRunsComposed*`). These equal my round-6 independent counts. The abstract (L1718) says "up to 22 of 42 curation runs"; the RQ1 box (L2361) gives 22 / 12 / 1. Lessons (L2461) uses the composed counts (22 and 12) and says "a contaminated skill or profile", which is now literally true. Introduction: "mainly where" (L1743). The E-L body (L2292) keeps the all-miss counts (22 / 13 / 2) with a by-kind breakdown, which is correct there. |
| **R3** setup vs Threats on what is post hoc | **Fixed** | L2192 now says H_EME-fail "was added after the first analysis", and that revalidation "was re-evaluated once with the dependency rule". L2331 calls H_EME-fail "a post-hoc variant computed from the recorded state". Consistent with Threats (L2448). |
| **R4** abstract 52 vs 74 | **Fixed** | L1718: "an LLM-judge oracle found one corrupted feedback message in the lesson it created in 74 of 150 ... and in further revisions in 52". The sentence no longer implies that the 52 are a subset of the 74, and the oracle is named. |
| R5 TF-IDF "only because" | **Fixed** | L2292: "Its threshold is the lowest of the grid, so it suspends 11.27 revisions per run, at precision 0.24." Neutral. |
| R5 HS_judge "essentially the judge" | **Fixed** | L2333: "differs from the judge alone in 11 of 42 propagated runs" (macro). |
| R5 collateral H vs R3 | **Fixed** | L2292: more in 41, fewer in 31, Holm p = 0.048. Matches my round-6 values. |
| R5 oracle in abstract | **Fixed** | "an LLM-judge oracle" (L1718). |
| R5 F1 sentence hard to parse | **Not fixed** | L2292 still reads "... R2 in all 42 ... and R4 in 36 of them (6 lower; ...)". See R4 below. |
| R5 "1,161 lines" | Not changed | Acceptable; reproducible as physical lines. |
| Human oracle audit | **Declined again** | Recommended, not a condition (the oracle is now named in the abstract). |

## Number check

Values are from my independent scripts on raw JSON unless marked "pipeline".

| # | Claim | Location | Paper | Mine | Match |
|---|---|---|---|---|---|
| 1 | Selectivity, ExpeL-style: roots per block | Table `tab:selectivity` | 1 / 73 / 158 / 162 | 1 / 73 / 158 / 162 (394 roots in 80 of 100 runs; insights from the last extraction step have no later revisions) | yes |
| 2 | Selectivity, ExpeL-style: ratio, EME-fail, strict | Table | 1.00 / 1.00 / 0% in every block | 1.00 / 1.00 / 0% in every block | yes |
| 3 | Selectivity, curation: roots | Table | 700 / 700 / 700 / 500 | 700 / 700 / 700 / 500 (7 / 7 / 7 / 5 per run in each of 100 runs) | yes |
| 4 | Selectivity, curation: ratio | Table, L2311 | 0.92 / 0.94 / 0.46 / 0.61 | 0.921 / 0.943 / 0.457 / 0.609 | yes |
| 5 | Selectivity, curation: EME-fail | Table, L2311 | 0.79 / 0.63 / 0.38 / 0.59 | 0.785 / 0.629 / 0.383 / 0.586 | yes |
| 6 | Selectivity, curation: strict | Table, L2311 | 43 / 56 / 97 / 95% | 42.6 / 55.6 / 97.1 / 95.2% | yes |
| 7 | "under the ExpeL-style policy closure equalled the time cut for every root" | L2311 | yes | 0 of 394 roots strictly smaller; also 1.00 under EME-fail, so the equality comes from synthesis sources, consistent with "every later extraction step sees the whole list" | yes |
| 8 | "roots created after the first composition had closures covering on average 0.46" | L2311, L1743 ("a fault after the first composition"), L2459 | 0.46 | Tasks 13-18: 0.457. Tasks 19-24: 0.609. Pooled 13-24: 0.520. Memory roots only (the only kind of fault root in this design): 0.496 and 0.609, pooled 0.547 | **number correct, scope overstated** (R1) |
| 9 | "Closure is thus a time cut for early faults" | L2311 | -- | Tasks 1-12: mean 0.92-0.94, but 43-56% of roots have a strictly smaller closure | wording: "nearly" (R3) |
| 10 | Same-step exclusion (response: including them made ExpeL look selective) | L2311, response | -- | Including same-step revisions: ExpeL 1.00 / 0.92 / 0.80 / 0.27; curation 0.92 / 0.93 / 0.46 / 0.52. The response's account is correct, and the curation result is robust to the choice | yes |
| 11 | Run-level robustness (not in paper) | -- | -- | Run-cluster bootstrap 95% CIs for the curation ratios: [0.92, 0.93], [0.94, 0.95], [0.44, 0.47], [0.60, 0.62]. Clean-only and faulty-only subsets give the same values within 0.02 | supports the claim |
| 12 | Absolute size (not in paper) | -- | -- | Curation, mean later revisions / mean closure / mean spared per root: 25.9 / 24.0 / 1.9; 18.9 / 17.7 / 1.2; 11.9 / 5.6 / 6.2; 6.0 / 3.5 / 2.5 | context (R1) |
| 13 | Composed-miss counts R3 / R4 / R2 | L1718, L2361, L2461 | 22 / 12 / 1 of 42 | 22 / 12 / 1 (round-6 independent count; pipeline agrees) | yes |
| 14 | All-miss counts | L2292 | 22 / 13 / 2 | 22 / 13 / 2 | yes |
| 15 | HS_judge differs from R4 (curation) | L2333 | 11 of 42 | 11 of 42 | yes |
| 16 | Collateral H vs R3 | L2292 | 41 / 31, p = 0.048 | 41 / 31, Holm 0.048 | yes |
| 17 | F1 H vs R3 (curation) | L2292 | 0.16 vs 0.18; 27 / 14; p = 0.091 | as in round 6 | yes |
| 18 | Adoption / propagation | L1718 | 74 / 52 of 150 | 21 + 53 / 10 + 42 | yes |
| 19 | H_EME-fail suspensions / F1 / recall | L2331, L2459 | 17.24 / 0.22 / 1.00 | 17.24 / 0.220 / 1.00 | yes |
| 20 | H vs T vs A suspensions (curation) | L2309, L2459 | 20.79 / 22.20 | unchanged pipeline output | yes |
| 21 | Revalidation plans, current code | response | no data change | 150/150 ExpeL, 150/150 curation | yes |
| 22 | Tables IV-VII and all earlier numbers | -- | -- | Inputs unchanged, pipeline output byte-identical | yes |

Summary: every number is correct. One row (#8) quotes a correct number for a wider scope than it covers.

### Soundness of the selectivity definition

- **Later-task cut.** `cut = {x in universe : created(x) > created(root)}` compares closure with a rollback to just after the root's step. Excluding same-step revisions removes them from both numerator and denominator. Any selectivity closure would show on its siblings, which a step-level rollback also has, therefore does not count in its favour. This makes the comparison conservative toward closure, and the stated reason (L2311) is the right one. My variant run (row #10) confirms that only the ExpeL result depended on this choice.
- **Roots are final active revisions only.**
  - Superseded revisions (`D*-p0`, `D*-p12`, ExpeL insights edited away) are excluded both as roots and from the cut. Curation roots are therefore memories and skills, never profiles.
  - Planted faults always originate in a memory (all 75 curation roots and all 154 ExpeL roots are memories). The relevant estimate for "a later fault" is therefore the memory-root ratio: 0.50 at tasks 13-18 and 0.61 at tasks 19-24, not 0.46.
  - The caption says "every final active revision", which is accurate. The text should not turn this into a statement about faults without the qualification.
- **Counterfactual.** The analysis assumes that a fault at task t would leave the recorded exposure structure unchanged. A real fault changes the trajectory (what is retrieved, merged and composed), so the table measures the structure of the observed runs, not the closure of a hypothetical fault. "Would have a closure covering" (L1743) states this too firmly.
- **Dependence.** Every run contributes the same number of roots per block (7 / 7 / 7 / 5 in curation), so pooling does not over-weight any run. Clean and faulty runs of the same model and seed share almost no prefix (most curation pairs diverge at the first memory), so there is no hidden duplication. The run-cluster CIs are narrow (row #11).
- **Ratio vs size.** The ratio is unweighted per root. For tasks 19-24 the cut has only 6 revisions on average, so 0.61 means about 2.5 revisions spared. For tasks 13-18 it is about 6 of 12. "Markedly more selective" is fair in relative terms, but readers need the absolute numbers to judge it.

## Remaining issues

**R1. The quoted selectivity figure covers only the most favourable block (L1743, L2311, L2459). Required.**
- **Where.** The introduction says "a fault after the first composition would have a closure covering on average 0.46 of the later state". E-L says "roots created after the first composition had closures covering on average 0.46". Lessons says "for roots created after that composition ... on average 0.46".
- **Why it is overstated.**
  - 0.46 is the 13-18 block only; the 19-24 block is 0.61 and the pooled figure is 0.52.
  - It also includes skill roots (ratio 0.22). Memory roots, the only kind a planted fault creates, give 0.50 and 0.61.
- **Fix.** Write "between 0.46 and 0.61 of the later revisions, depending on position (Table ...)", or report the pooled value. In the introduction, replace "would have" with "the recorded structure gives such roots a closure covering ...".
- **Also add** the mean number of later revisions per block to the table, or to the text for tasks 13-24, so readers see that the sparing amounts to roughly 2-6 revisions.

**R2. Disclose that the selectivity analysis is post hoc (Threats, L2448). Required.**
- **The facts.** The analysis was added in response to the round-6 reviews. Its definition was changed once after the first version produced an artefact: ExpeL 0.46 from sibling insights (response.md). The paper gives the reason for the exclusion (L2311), but not its history.
- **Fix.** Add a sentence alongside the H_EME-fail disclosure, for example: "The structural-selectivity analysis was added after the first review; its first version counted same-step revisions, which made sibling insights look spared, and was corrected to the later-task cut." Also note that it measures the observed structure, not the closure that a fault at that position would have produced.
- **Optional.** L2448 says "early faults favour propagation and inflate closure sizes relative to late faults". It can now point to the table.

**R3. "Closure is thus a time cut for early faults" (L2311). Minor.**
- For roots at tasks 1-12 the mean ratio is 0.92-0.94, but 43-56% of roots have a strictly smaller closure. Write "nearly a time cut", matching the RQ1 box's "slightly less under curation".

**R4. Minor, carried over or presentational.**
- **L2292, F1 sentence.** It is still hard to parse. "R4 in 36 of them (6 lower ...)" does not say whose F1 is lower. Split it: "R2's F1 exceeded H's in all 42 propagated runs (p < 0.001) and R4's in 36 (H's was higher in 6; p < 0.001)."
- **Table `tab:selectivity`, ExpeL row 1-6.** The row rests on one root. Mark it, or merge it with 7-12.
- **CIs.** Run-cluster bootstrap CIs for the selectivity ratios are cheap (`boot` exists) and narrow. Consider shipping them in `live_summary.json` like the other means.
- **Human oracle audit.** Still recommended, not a condition.

## Recommendation

**Minor revision (accept after small prose changes).**

All three round-6 required changes were made correctly, and so were most minor points. I verified them in the files:
- The F1 claims are tied to curation.
- The composed-miss counts (22 / 12 / 1) are correct and used consistently.
- The setup paragraph agrees with Threats on what is post hoc, and the H_EME-fail result is labelled post hoc.
- The abstract names the oracle and no longer implies 52 ⊂ 74.

The new structural-selectivity analysis is well defined, conservative toward closure, reproduced exactly by my independent code, and robust at run level. It answers the question whether closure can be more selective than a rollback, and it is reported with the right caveat that sparing is not cleanliness.

Required before acceptance:
1. Quote the post-composition selectivity as the 0.46-0.61 range (or pooled), not the most favourable block alone, in the introduction, E-L and Lessons. Soften "would have" in the introduction (R1).
2. Disclose in Threats that the selectivity analysis is post hoc and that its definition was revised once (R2).
