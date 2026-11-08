# Round 8 -- Reviewer 2 (empirical rigor and verifiability)

Paper: docs/TSE/main.tex and main.pdf. The tex is from 19:18:35 and the PDF from 19:18:37, so the PDF is current. It has 24 pages, no `??` and no undefined references. Line numbers below refer to main.tex. New scratch work is in `/tmp/claude-1000/r8rev2/`. I reused my round-6 and round-7 scripts unchanged.

## Summary

This round is a calibration round. The authors did three things:
- They replaced the single selectivity figure 0.46 with the range 0.46-0.61 in the introduction (L1743) and Lessons (L2459). E-L (L2311) now reports both post-composition blocks.
- They added the window-effect explanation (L2311): the task-24 composition pulls every late root's closure back up.
- They disclosed in Threats (L2448) that the selectivity analysis is post hoc and that its definition was revised once.

In code, the clean frontier of a re-admitted copy now includes inactive clean ancestors (`src/heartness/revalidation.py`), with two new tests.

**What I verified**
- **Raw data and outputs.** No file under `results/raw/` or `results/processed/live/` has changed since round 7.
- **Pipeline.** I re-ran `experiments.live.process report` from a scratch directory. Both `live_runs.csv` files are byte-identical to the shipped ones. Both `live_summary.json` files are identical except for the `campaign` path.
- **Macros.** All 1,577 `\newcommand` values in the tex equal `paper_macro_index.json`. Every Live/Syn macro is defined.
- **Supplements.** The current `supplement.restore` still reproduces every shipped revalidation plan: 150/150 for ExpeL and 300/300 for curation (two screens times 150 supplements). This was expected, because the code change affects only the lineage of copies, not which copies are admitted.
- **Tests.** `tests/test_revalidation.py` and `tests/test_eme.py` pass (21 tests, 2 more than in round 7).
- **New prose claims.** I checked the new window-effect claims against raw JSON with my own closure (`r8rev2/window.py`). Both hold; see Number check rows 5 and 6.

Both required changes from round 7 were made. All numbers are correct. One part of R2 was not done: the caveat that the analysis is counterfactual (it measures the recorded structure, not what a fault at that position would have produced). The introduction now avoids the counterfactual wording, but E-L and the conclusion still use it.

## Scores

| Criterion | Score (1-5) | Justification |
|---|---|---|
| Novelty | 3 | Unchanged. The lifecycle formulation, EME as a first-class edge and guarded admission are new and useful. But the evaluation shows that for every sampled fault, closure-based withdrawal buys almost nothing over a rollback in suspension cost. Its distinctive advantage (selectivity) is shown only structurally and counterfactually. |
| Rigor | 3 | Every number reproduces, the definitions are sound, and post-hoc elements are now disclosed. Three limits remain. First, every contamination label comes from an LLM-judge oracle that no human has validated. Second, the ExpeL-style policy has an effective n of 10 propagated runs. Third, the selectivity claim for later faults is counterfactual, and one part of that caveat is still not stated in the paper (R1 below). |
| Relevance | 4 | Unchanged. |
| Verifiability and Transparency | 4 | Pipeline output is byte-identical, the supplements reproduce from current code, all macros are indexed, and the post-hoc history is disclosed. Remaining small gaps: the new window-effect fact (1,200/1,200) is hard-coded prose and not computed by the pipeline; selectivity CIs are not shipped; a function name and an inline comment in the code still say "active frontier" (R3). `environment.git` is still empty (accepted earlier). |
| Presentation | 4 | The summaries are now consistent with the table. The F1 sentence at L2292 is still hard to parse (carried over twice). The absolute size of the sparing is still not given. |

## Status of round-7 issues

| Round-7 issue | Status | Evidence |
|---|---|---|
| **R1** selectivity quoted from its best block (required) | **Fixed** | Intro L1743: "revisions created after the first composition have closures covering on average 0.46--0.61 of the later state until the next composition". "Would have" is replaced by a statement about recorded revisions. E-L L2311 gives 0.46 (tasks 13-18) and 0.61 (tasks 19-24), with Smaller 97% / 95%. Lessons L2459 gives "0.46--0.61 ... but only until the next broadcast composition". The memory-only values (0.50 / 0.61) lie inside the quoted range, so the skill-root mix no longer distorts the summary. |
| R1 sub-point: absolute number of later revisions | **Not done** | Neither the table nor the text gives it. Mean later revisions / spared per root are 11.9 / 6.2 at tasks 13-18 and 6.0 / 2.5 at tasks 19-24. See R2 below. |
| **R2** disclose post-hoc status (required) | **Mostly fixed** | Threats L2448: "The structural selectivity analysis was added after the sixth internal review round, and its definition was revised once: a first version that counted revisions written in the same step ... made the ExpeL-style policy look selective for late roots, which it is not." This is accurate: in my same-step variant ExpeL gives 0.80 / 0.27 in the late blocks. **Missing:** the second half of the requested fix, that the table measures the observed structure and not the closure that a fault at that position would produce. See R1 below. |
| R2 optional: Threats "early faults ... inflate closure sizes" point to the table | Not done | L2448. Optional. |
| **R3** "time cut for early faults" | **Fixed** | L2311: "Closure is thus nearly a time cut for early faults and exactly one for policies that show every step everything." |
| R4 F1 sentence at L2292 | **Not fixed (second carry-over)** | It still reads "R2 in all 42 propagated runs (Holm p<0.001) and R4 in 36 of them (6 lower; p<0.001)". "6 lower" still does not say whose F1. The R3 parenthetical sits between the subject and these clauses. |
| R4 ExpeL 1-6 row rests on one root | **Fixed** | Caption L2314: "The ExpeL-style 1--6 row rests on a single root." The caption also defines roots as revisions still active at the end, and the column is renamed "Smaller". |
| R4 selectivity CIs | Not done | Optional. My run-cluster bootstrap CIs (round 7) are narrow: [0.44, 0.47] and [0.60, 0.62]. |
| Human oracle audit | Declined again | See the path to Rigor 4 below. |

## Number check

Values are from my independent scripts on raw JSON unless marked "pipeline".

| # | Claim | Location | Paper | Mine | Match |
|---|---|---|---|---|---|
| 1 | Selectivity table, ExpeL-style (roots / ratio / EME-fail / Smaller) | Table `tab:selectivity` | 1/73/158/162; 1.00; 1.00; 0% | same (`r7rev2/sel.py`; inputs unchanged) | yes |
| 2 | Selectivity table, curation, ratio | Table, L2311 | 0.92 / 0.94 / 0.46 / 0.61 | 0.921 / 0.943 / 0.457 / 0.609 | yes |
| 3 | Curation EME-fail; Smaller | Table, L2311 | 0.79/0.63/0.38/0.59; 43/56/97/95% | 0.785/0.629/0.383/0.586; 42.6/55.6/97.1/95.2% | yes |
| 4 | "0.46--0.61 of the later state" after the first composition | L1743, L2459 | range | 13-18: 0.457; 19-24: 0.609. Memory roots only: 0.496, 0.609 | yes; the range now covers both blocks and both root kinds |
| 5 | "both profiles composed at task 24 were in the closure of every such root" | L2311 | every | 1,200 of 1,200 late roots (700 + 500); both task-24 profiles are later revisions in the closure | yes, but hard-coded (R3) |
| 6 | Roots at tasks 19-24 show a higher ratio "because their later revisions include the task-24 profiles and skill" | L2311 | -- | Removing the task-24 composition (2 profiles + 1 skill, in the cut of every late root) from cut and closure lowers the ratio to 0.31 (13-18) and 0.16 (19-24). The ordering reverses, so the explanation is correct | yes |
| 7 | "Counting EME only for failed runs lowered the ratios further (0.63 for tasks 7--12)" | L2311 | 0.63 | 0.629. Lower than the ratio in every curation block | yes |
| 8 | Same-step version made ExpeL "look selective for late roots" | L2448 | -- | Same-step variant: ExpeL 1.00 / 0.92 / 0.80 / 0.27 | yes |
| 9 | "Markedly more selective than a time cut only for curation roots after the first composition" | RQ1 box L2361 | -- | ExpeL: 1.00 in every block. Curation 1-12: 0.92-0.94. Curation 13-24: 0.46-0.61 | yes |
| 10 | Absolute sparing (not in paper) | -- | -- | Mean later revisions / closure / spared per root: 11.9 / 5.6 / 6.2 (13-18) and 6.0 / 3.5 / 2.5 (19-24) | context (R2) |
| 11 | Composed-miss counts R3 / R4 / R2 | L1718, L2361, L2461 | 22 / 12 / 1 of 42 | 22 / 12 / 1 | yes |
| 12 | F1 H vs R4, curation | L2292 | 36 / 6, p<0.001 | 36 / 6 (pipeline, unchanged) | yes (wording R4) |
| 13 | Adoption / propagation | L1718 | 74 / 52 of 150 | 74 / 52 | yes |
| 14 | H_EME-fail suspensions | L2459 | 20.79 -> 17.24 | unchanged pipeline output | yes |
| 15 | Revalidation plans with the new frontier code | -- | no data change | 150/150 and 300/300 | yes |
| 16 | All other tables and macros | -- | -- | Pipeline byte-identical; 1,577 macros equal the index | yes |

Mismatches: none in the numbers. The only remaining gaps are in what the paper says about these numbers (R1-R4 below).

## Remaining issues

**R1. State that the selectivity table is counterfactual (L2311, conclusion L2523). Required, one clause.**
- **Where the wording is too strong.**
  - L2311 says the analysis lets us "ask what they would suspend for a fault at any other position". It ends: "markedly more selective for later faults under retrieval".
  - The conclusion (L2523) says "it becomes markedly more selective only for later faults in a retrieval-based harness".
- **Why it is a counterfactual.** A real fault at task 15 would change what is retrieved, merged and composed afterwards. The table describes the exposure structure of runs in which no fault happened at that position.
- **What the paper says now.** L2311's caveat ("measures only how much closure spares, not whether what it spares is clean") covers precision, not this counterfactual. The Threats disclosure covers the history, not this.
- **Fix.** Add one clause, for example to L2311: "assuming that a fault at that position would leave the recorded exposure structure unchanged, which a real fault need not". Alternatively, in L2311 and L2523 write "for revisions created after the first composition" instead of "for later faults".

**R2. Give the absolute size of the sparing (L2311). Recommended.**
- **What to add.** A clause such as: "on average 6 of 12 later revisions are spared for roots at tasks 13-18, and 2.5 of 6 at tasks 19-24".
- **Why.** At tasks 19-24 the 0.61 ratio rests on six later revisions per root. Readers cannot judge "markedly more selective" without this.

**R3. Small verifiability gaps. Recommended.**
- **Window-effect count.** The "every such root" fact at L2311 (1,200 / 1,200) and the excluded-composition ratios are not computed in `process.selectivity`. One more field in `live_summary.json` would make the sentence traceable like every other number.
- **Selectivity CIs.** Run-cluster bootstrap CIs are cheap and consistent with how the paper treats the other means.
- **Code naming.** `response.md` says "active frontier" was renamed "clean frontier" in the code. The docstring and the paper (L2059, L2071) were updated. The function is still called `active_frontier` (`src/heartness/revalidation.py` L101, L122). The inline comment at L95-96 still says "ACTIVE FRONTIER: the nearest clean, active ancestors", which contradicts the new behaviour (active or not).

**R4. F1 sentence at L2292. Minor, carried over twice.**
- Suggested rewrite: "TF-IDF's F1 exceeded H's in all 42 propagated runs (Holm p<0.001) and the judge's in 36 (H's was higher in 6; p<0.001); the embedding detector was comparable (...)."

### What would earn a 4

**Rigor (3 -> 4)**

*Achievable from existing data:*
- R1 (the counterfactual clause) and R2 (absolute size). These are needed, but on their own they do not lift the score.

*Needs new data, in one of two forms (either suffices):*
- **(a) Human audit of the oracle.** This is the minimal step: human labels, no new runs.
  - Take a stratified sample of about 100-150 revisions. Cover all propagated curation runs, with contaminated, clean and ambiguous strata and every kind (memory, skill, profile).
  - Have two annotators label it blind to the oracle.
  - Report agreement with the judges (κ) and the oracle's false-negative and false-positive rates in each stratum.
  - Every recall, precision and F1 number, and the composed-miss counts (22 / 12 / 1), depend on this oracle. It is the single largest remaining validity threat.
  - The recall of H is close to structural, but the detector comparisons that make up half the paper's message are not.
- **(b) Planted faults after the first composition.** For example, one fault at task 13-18 under curation, about 25 faulty runs on 2-3 models.
  - This would turn the counterfactual selectivity result into a measured one, with recall.
  - It would also remove the main reason the result needs a caveat.

The effective n of 10 for the ExpeL-style policy would also need more runs, but it is disclosed and it is not the primary claim. I would not require it for a 4.

**Novelty (3 -> 4)**

*Achievable from existing data:* nothing that would move the score. A sharper statement of what is new relative to provenance-based rollback (EME as a recorded edge, guarded admission/rollback refusal, deployment-wide closure) would help, but the empirical case would be unchanged.

*Needs new data:* (b) above. It is what would show empirically that withdrawal does something a rollback cannot, namely remove all contamination at markedly lower cost.
- The paper's own evidence says this happens only for faults after a composition under retrieval.
- None of the 150 planted faults fell there.
- With (b) showing, for example, recall 1.00 at roughly half the rollback's suspensions, I would score novelty 4.

## Recommendation

**Minor revision. Accept once the R1 clause is added; no further review round is needed for that.**

Both required changes from round 7 were made and are correct in the files:
- The selectivity figure is now quoted as 0.46-0.61 for both post-composition blocks in the introduction, E-L and Lessons, with the window caveat.
- Threats now discloses the post-hoc origin and the one revision of the definition, and describes the revision accurately.

**Checks this round**
- The new window-effect claims are correct: 1,200 / 1,200, and the ordering reverses once the task-24 composition is excluded.
- The pipeline is byte-identical and every macro matches its source.
- The code change leaves all 450 revalidation plans unchanged.

**Requested before acceptance**
- **Required:** the one-clause counterfactual caveat at L2311 / L2523 (R1).
- **Recommended:** R2-R4.
- **Not a condition for acceptance:** a human audit of the oracle, or planted late faults. As set out above, these are what would raise Rigor (and, for planted late faults, Novelty) to 4.
