# Round 5 -- Reviewer 2 (empirical rigor and verifiability)

Paper: "Traceable and Withdrawable Self-Evolution of AI Agent Harnesses: A Model-Driven Approach with Bounded Model Checking" (docs/TSE/main.tex and main.pdf, both dated 2026-11-07 14:47). Line numbers refer to main.tex. Table numbers refer to the compiled PDF: Tables IV/V are the ExpeL-style model and containment tables (L2167, L2181), Tables VI/VII the curation ones (L2222, L2234). My scratch scripts and outputs are in `/tmp/claude-1000/r5rev2/`.

## Summary

This round makes four changes:
- It replaces the revalidation evaluation with an implementation of Algorithm 5 (`heartness.revalidation.plan`, shared by the engine and `experiments/live/supplement.py`) and regenerates all 75 curation supplements.
- It withdraws the cache-based determinism claim and replaces it with an independent-generation noise measure.
- It adds a post-hoc EME policy (H_EME-fail), the closure-vs-cut breakdown by fault task, and the unfavourable F1 and collateral tests.
- It rewrites the abstract, introduction, RQ1 box, Lessons and conclusion.

**Verification.**
- **Pipeline.** I re-ran `experiments.live.process report` on both campaigns from a scratch directory. Both `live_runs.csv` files are byte-identical to the shipped ones. Both `live_summary.json` files differ only in the `campaign` field, which stores the path as given on the command line.
- **Independent script.** My script (`indep5.py`, extended from round 4 to the ExpeL-style layout) reads only raw `record.json`, `oracle.json` and `supplement.json`. It re-implements the closure, T, A, H_faulty and the Wilcoxon/Holm tests. It reproduces the logged H, H_noEME and H_noDeps sets in 75/75 runs of each policy, and every row of Tables IV-VII.
- **New post-hoc condition.** A separate script (`r5.py`) re-implements H_EME-fail.
- **Revalidation.** `r5.py` also contains my own Algorithm 5: history order from the evolution log, the dependency check against the active set after H, and redeployment. It reproduces the recorded `restored` and `rejected` sets and the resulting suspension sets in all 150 curation (run, screen) pairs. ExpeL-style supplements equal "H minus cleared" in 75/75 runs (no artifact has dependencies).
- **Old vs new supplements.** Comparing `supplement_v1.json` with the regenerated files confirms the response: 59 runs and 95 revisions differ, all of them profiles.

**Outcome.** Every number I recomputed matches (60 checks below). The round-4 interpretation problems are mostly fixed: the determinism claim, the selective test reporting, the conclusion, the p-value, and the closure-vs-cut mechanism.

**What remains is mostly prose.**
1. A new summary claim contradicts Table VII. "Every content detector had higher F1" than closure is stated in the abstract, the RQ1 box and E-L. It is false for the embedding detector under curation: R3 F1 is 0.16 vs H 0.18, and H is higher in 27 runs and lower in 14.
2. H_EME-fail was defined after the data were analysed, with knowledge that the single EME-only run had a failed task. It is not disclosed as post hoc, yet it is promoted to the introduction, Lessons and conclusion.
3. Several smaller leftovers remain:
   - one order-sensitivity sentence that the response says was withdrawn;
   - "HS_judge differs in a single run" (it differs in 2 of 10);
   - "lost recall only where advice was folded into larger artifacts" (memory and insight misses exist);
   - a garbled RQ1-box sentence on precision.

## Scores

| Criterion | Score (1-5) | Justification |
|---|---|---|
| Novelty | 3 | Unchanged. The lifecycle formulation (withdrawal across deployments, EME, rollback conflict) is new and useful. Revalidation is now a composition of existing operators with an attestation, which is cleaner. The model checking is standard. |
| Rigor | 3 | The revalidation evaluated now equals Algorithm 5 (verified independently on 150/150 plans). The noise floor is measured correctly, the unfavourable tests are reported, and the closure-vs-cut result is stratified by fault position. Remaining weaknesses: no human validation of the oracle; positive agreement not reported; H_EME-fail is post hoc, rests on n = 1 informative run, and is undisclosed as post hoc; no CIs in the paper (only in the package); no stratified analysis. |
| Relevance | 4 | Unchanged. |
| Verifiability and Transparency | 4 | Pipeline output is byte-identical, raw data and superseded supplements ship, and CIs and per-run values are in `live_summary.json`. `structure.eme_only` paths are now relative. Deductions: `environment.git` is still empty in every record; `campaign` in `live_summary.json` stores the command-line path; a stray `results/processed/live/nonexistent/` directory is in the package; the post-hoc status of H_EME-fail and of the round-5 revalidation rerun is not stated. |
| Presentation | 3 | The rewritten summaries are much better calibrated than in round 4, and the new curation paragraphs are clear. However, the headline F1 sentence in the abstract, RQ1 box and E-L contradicts Table VII, and a few sentences remain that the response says were removed or fixed. |

## Status of round-4 issues

| Round-4 issue | Status | Evidence / remaining gap |
|---|---|---|
| M1 determinism is a cache artifact; order claim confounded | **Addressed, with one leftover** | The three "identical contexts" sentences are gone. Cross-run noise is reported in E-L (L2210, L2264), Threats (L2377) and Lessons (L2394): 178/4,349 (4.1%) and 2/273 (0.7%), both reproduced. The text says within-run replay is enforced by the cache. **Leftover:** L2210 ends "the effect on pass@1 is within the agent's sensitivity to context order", which is the withdrawn order claim. Replace it with "within inference noise". |
| M2 selective reporting of F1/collateral tests | **Addressed** | L2241 reports H vs R2 F1 (42/42 worse, p<0.001), H vs R4 (36 worse, 6 better, p<0.001), and collateral vs R2 (73) and R4 (75) with Holm p. All reproduced. Collateral vs R3 (p = 0.048) and F1 vs R3 (p = 0.091, H *better* in 27) are not mentioned. The latter matters for issue N1. |
| M3 summaries calibrated against the worst detector | **Mostly addressed; new error** | The abstract (L1672) gives the range "2 to 22 of 42". The RQ1 box (L2290) lists R3 22, R4 13, R2 2. The conclusion no longer says "only closure" (L2452). **But** the replacement claim "every content detector had higher F1" (L1672, L2241, L2290) is false for R3 under curation (N1). The framing "only because that threshold is low and suspends 11.27 revisions per run" (L2241) remains. 11.27 is about half of H's 20.79, so the pilot-tuned TF-IDF nearly matched H's recall at half its suspension; the text still presents this as a weakness. |
| M4 closure-vs-cut fixed by schedule and fault position | **Addressed** | L2258 gives the stratification 0/15, 33/45, 9/15 (reproduced), attributes the effect to EME applied to a broadcast context, and states that no gap is expected after the first composition. Lessons (L2388) and conclusion (L2454) frame selective contexts as future work. |
| M5 oracle validation | **Partly addressed** | The 3 H_faulty misses now say the judges disagreed on the root (L2258; reproduced: 3 runs, all ambiguous roots). There is still no human audit (declined). **Positive agreement (0.89 curation, 143 both-YES vs 35 disagreements) is still not reported.** The abstract and RQ1 box still do not say the R4 judge is the generator judging itself (only L2241 and Threats do). |
| M6 statistics | **Partly addressed** | Effective n for both policies is stated (L2383). "No single primary metric; recall and residual are the designed-for metrics" is acceptable. CIs are described as shipped (L2149), and I confirmed `lo`/`hi` per metric in `live_summary.json`. They are still not in the paper. A stratified analysis was declined with a reason (n <= 11 per generator), which is acceptable. |
| Minor: "at most 0.47%" | Fixed | The abstract no longer has it. The RQ3 box gives both policy means. `LiveCEnginePercentMax` (0.77) exists but is unused. |
| Minor: "skills and system prompts in 42" | Fixed | Removed from the introduction. |
| Minor: L2106 p-value | Fixed | L2204 prints p = 0.273 and p = 0.352. |
| Minor: "5.95 of about 8.0 live revisions" | Fixed | L2188 now reads "of the 6.00 learned revisions". |
| Minor: dev F1 three decimals | Fixed | 0.575 / 0.625. |
| Minor: Table VII caption denominators | Fixed | L2228. |
| Minor: Fig. 5 caption | Fixed | "among the plotted conditions". |
| Minor: "lower than every detector" (precision) | Fixed | L2258: "by a large margin for R2 and R4 and narrowly for R3". |
| Minor: EME price | Fixed | L2260: 20.79 vs 14.39 per run in 55 runs. |
| Minor: pass@1 gain below noise | Fixed | L2264: "less than one of 29 items". |
| Minor: CPU fallback for generation | Fixed | L2377. `inference_devices.tsv` shows the revalidation job 2882647 cell 0 on CPU at try 1 and on CUDA at try 2, consistent with the text. |
| Minor: `structure.eme_only` paths | Fixed | Now `llama3.1_8b/F3/seed-3/record.json`. The `campaign` field still stores the CLI path. |
| Minor: `environment.git` empty | **Not fixed** | Still `''` in every record. `source_sha256` is the only code identity. |
| Minor: unused all-run `precision` keys | **Not fixed** | `LiveCHPrec` (0.06) etc. are still generated, but unused in the text. |

## Revalidation: code vs Algorithm 5

- `src/heartness/revalidation.py` (`plan`, `revalidate`) implements Algorithm 5 (L2014-2028) faithfully:
  - the attestation is a seed;
  - copies are made with `src = {a}` and dependencies remapped;
  - history order is respected;
  - a member is rejected if a dependency is neither active nor re-admitted;
  - the copies are redeployed to `Dpl_before`.
- `experiments/live/supplement.py` calls the same `plan()` with history order from the evolution log (memory < skill < profile within a task) and the active set after H.
- The 15 tests in `tests/test_revalidation.py` and `tests/test_eme.py` pass.
- **Independent check.** My own Algorithm 5, with no shared code, reproduces `restored`, `rejected` and `suspended` in 150/150 curation (run, screen) pairs. Rejections:
  - HS_judge: 19 in 18 runs, none contaminated, all profiles.
  - HS_emb: 76 in 51 runs, 20 contaminated. Each of the 20 has at least one dependency that the screen did not clear and that was not active, as L2262 says.
- **Two small divergences between code and algorithm**, neither of which affects the reported data:
  - (a) `supplement.py` re-activates a restored member only if it was active before withdrawal (`back & rec["active"]`), whereas Algorithm 5 admits every cleared member of A. All 1,820 restored members in the data were active before withdrawal.
  - (b) If `_admit` raises in `revalidate()`, members that `plan()` admitted as depending on it keep the original (quarantined) dependency and are then rejected by admission. So plan and execution can differ there. The test covers only the toy harness. Consider making `plan()` the single source of truth or documenting this.
- **Ordering.** The test that "plan equals execution" runs only on a 5-revision toy. The claim at L2031 is accurate for that test.

## Number check

My values come from independent scripts on raw JSON unless marked "pipeline". "Prop." means propagated runs (10 ExpeL-style, 42 curation).

| # | Claim | Location | Paper value | My value | Match |
|---|---|---|---|---|---|
| 1 | Runs total / faulty / propagated (all policies) | L1672 | 200 / 150 / 52 | 200 / 150 / 10+42 | yes |
| 2 | ExpeL root adopted (amb), propagated, derivatives | L2172 | 21 (22), 10, 16 | 21 (22), 10, 16 | yes |
| 3 | ExpeL per fault adopted/spread | L2172 | 5/1, 7/5, 9/4 | 5/1, 7/5, 9/4 | yes |
| 4 | ExpeL qwen adopted 10 of 15, propagated 6; gemma/granite 0 | L2172 | as stated | 10, 6; 0, 0 | yes |
| 5 | ExpeL clean revisions, labels, agreement, kappa | L2172 | 210, 630, 99.9%, 0.99 | 210, 630, 0.9993, 0.987 | yes |
| 6 | ExpeL H susp of learned; prop susp; collateral; prec; F1 | L2188 | 5.95 of 6.00; 4.90; 3.30; 0.33; 0.48 | 5.947 / 6.00; 4.9; 3.3; 0.335; 0.479 | yes |
| 7 | ExpeL H = T; A more in | L2188 | 75; 4 | 75; 4 | yes |
| 8 | ExpeL H_faulty prop susp | L2188 | 4.90 | 4.9 | yes |
| 9 | ExpeL TF-IDF F1 range with full recall 0.10-0.70; embed from 0.70 | L2204 | 0.66-0.69; >= 0.70 | 0.665-0.690 (recall 1.0); embed 0.659 at 0.70, recall 1.0 throughout | yes |
| 10 | ExpeL R2/R3/R4 F1, R4 prec, R4 recall, R4 miss run | L2204 | 0.60/0.50/0.65, 0.55, 0.90, llama F2 s1 | 0.601/0.503/0.647, 0.553, 0.9, llama3.1 F2 s1 | yes |
| 11 | ExpeL F1 H vs R4 lo/hi; vs R2 lo; Holm p | L2204 | 7/2; 6; 0.273, 0.352 | 7/2; 6; 0.2734, 0.3516 | yes |
| 12 | ExpeL HS_judge F1 (highest), HS_emb F1, never worse | L2206 | 0.67; 0.62; yes | 0.670 (max); 0.619; H worse in 4, never better | yes |
| 13 | "HS_judge differs [from R4] in a single run" (ExpeL) | L2206 | 1 run | 2 of 10 propagated runs (deepseek F1 s2; llama3.1 F2 s3), 12/75 overall; pipeline CSV agrees | **mismatch** |
| 14 | ExpeL pass none / H / clean / seed | L2210 | 0.59/0.62/0.61/0.63 | 0.589/0.617/0.610/0.632 | yes |
| 15 | ExpeL noise flips / pairs / rate | L2210 | 178 / 4,349 / 4.1% | 178 / 4,349 / 4.09% (177 of 178 flips on empty-context prompts) | yes |
| 16 | ExpeL prop pass none -> H, higher/lower | L2210 | 0.60 -> 0.68, 5/5 | 0.600 -> 0.676, 5/5 | yes |
| 17 | ExpeL prop signature 0.09 -> 0.02, lower in 6, never higher, p | L2210 | 6, 0, 0.219 | 6, 0, Holm 0.219 | yes |
| 18 | Curation root adopted (amb), propagated, derivatives | L2239 | 53 (59), 42, 90 | 53 (59), 42, 90 | yes |
| 19 | Curation propagated by fault | L2239 | 7/17/18 | 7/17/18 | yes |
| 20 | Contaminated by kind skill/profile/memory | L2239 | 42/43/5 | 42/43/5 | yes |
| 21 | Table VI rows (5 generators) | L2222 | e.g. Qwen 15/14/11/32/29.0/20.9/0.76 | identical for all 5 rows | yes |
| 22 | Clean curation revisions, labels, ambiguous; agreement, kappa | L2239 | 750, 2,250, 5; 99.2%, 0.89 | 750, 2,250, 5; 0.9922, 0.887 | yes |
| 23 | Residual none; H recall, recall amb-as-c, residual | L2241 | 1.20; 1.00, 1.00, 0.00 | 1.20; 1.0, 1.0, 0 | yes |
| 24 | R3 recall, miss runs, profile misses | L2241 | 0.68, 22, 28 | 0.679, 22, 28 (+6 skill) | yes |
| 25 | R4 recall, miss runs, skill/profile misses | L2241 | 0.79, 13, 12/7 | 0.787, 13, 12/7 (+2 memory) | yes |
| 26 | Recall H>R3 / H>R4 runs; Holm p | L2241 | 22, 13; <0.001, 0.005 | 22, 13; 1.8e-4, 0.0051 | yes |
| 27 | R2 recall, miss runs, susp/run, prec (prop.) | L2241 | 0.99, 2, 11.27, 0.24 | 0.989, 2, 11.27, 0.235 | yes |
| 28 | TF-IDF oracle bound tau/F1/recall; embed max F1 | L2241 | 0.15/0.69/0.75; 0.21 | 0.15/0.695/0.749; 0.215 | yes |
| 29 | F1 H vs R2: R2 higher in all 42; Holm p | L2241 | 42; <0.001 | 42/42; 1.1e-7 | yes |
| 30 | F1 H vs R4: lower 36, higher 6; Holm p | L2241 | 36/6; <0.001 | 36/6; 5.8e-7 | yes |
| 31 | Collateral H > R2 / H > R4 runs; Holm p | L2241 | 73, 75; <0.001 | 73, 75; 3.2e-13 | yes |
| 32 | "every detector had higher F1 than H" (curation) | L2241, L1672, L2290 | every detector | R3 F1 0.165 < H 0.180 (Table VII prints 0.16 vs 0.18); H higher in 27 runs, lower in 14 (Holm p = 0.091) | **mismatch** |
| 33 | Susp/run H / T / A | L2258 | 20.79 / 22.20 / 29.00 | 20.787 / 22.20 / 29.00 | yes |
| 34 | H subset of T; strictly smaller; gap revisions; all memories before task 12 | L2258 | 75; 42; 106; all | 75; 42; 106 memories; 106 | yes |
| 35 | Profiles in closure | L2258 | 75 of 75 | 75 | yes |
| 36 | Strictly smaller by fault task 2 / 8 / 9 | L2258 | 0/15, 33/45, 9/15 | 0/15, 33/45, 9/15 | yes |
| 37 | H precision (prop.), F1 | L2258 | 0.10, 0.18 | 0.102, 0.180 | yes |
| 38 | H_faulty misses; all ambiguous root | L2258 | 3; 3 | 3; root labels a, a, a | yes |
| 39 | H_noEME differs; susp; F1; EME-only runs | L2260 | 55; 14.39; 0.31; 1 | 55; 14.387; 0.308; 1 (llama3.1 F3 s3, m9) | yes |
| 40 | More collateral with EME | L2260 | 55 | 55 | yes |
| 41 | H_EME-fail recall; susp/run; F1; EME-only run's task failed | L2260 | 1.00; 17.24; 0.22; failed | 1.0; 17.24; 0.220 (prec 0.131); e9 outcome `fail` | yes |
| 42 | H_noDeps differs; H_local recall | L2260 | 0; 0.03 | 0; 0.031 | yes |
| 43 | HS_judge susp (prop.), F1, runs restoring contamination, recall | L2262 | 2.90, 0.65, 13, 0.79 | 2.905, 0.651, 13, 0.787 | yes |
| 44 | HS_judge rejections, contaminated; reason | L2262 | 19, 0; skill dependency suspended | 19 in 18 runs, 0 contaminated, all profiles, all "dependency not active" | yes |
| 45 | HS_judge F1 below R4 "because" of rejections | L2262 | 0.65 vs 0.69 | v1 (no P3) 0.697, new 0.651, R4 0.691 | yes |
| 46 | HS_emb contaminated rejections; rejections; runs; recall vs R3 | L2262 | 20; 76; 51; 0.86 vs 0.68 | 20; 76; 51; 0.862 vs 0.679 | yes |
| 47 | Old vs new supplement: runs, revisions, kinds (response) | response | 59, 95, all profiles | 59, 95, 95 agent | yes |
| 48 | Algorithm 5 plan equals recorded plan | L2031, response | all 150 | 150/150 (independent implementation) | yes |
| 49 | Curation pass none / H / clean / seed | L2264 | 0.61/0.62/0.61/0.62 | 0.610/0.620/0.611/0.623 | yes |
| 50 | Prop pass 0.60 -> 0.62, 23/13, Holm p | L2264 | 0.338 | 0.597 -> 0.624, 23/13, 0.338 | yes |
| 51 | Prop signature 0.04 -> 0.02, 12/2, Holm p | L2264 | 0.071 | 0.044 -> 0.023, 12/2, 0.071 | yes |
| 52 | Gain < 1 of 29 items | L2264 | <1 | 0.027 x 29 = 0.78 | yes |
| 53 | Curation noise flips / pairs | L2264 | 2 / 273 (0.7%) | 2 / 273 (0.73%) | yes |
| 54 | Curation cost: min, engine s, %, calls, events; H ms, R4 ms | L2347 | 6.1, 1.71, 0.47, 305, 156; 29.3, 66,236.9 | 6.11, 1.713, 0.468, 305.4, 156; 29.3, 66,236.9 | yes |
| 55 | ExpeL cost: min, engine s, %, calls, events; H ms, R4 ms | L2347 | 3.9, 0.49, 0.21, 198, 106; 20.3, 20,614.6 | 3.90, 0.491, 0.210, 198.1, 106.1; 20.3, 20,614.6 | yes |
| 56 | Total LLM calls | Table III | 42,811 | 17,056 + 25,755 | yes |
| 57 | Evaluated conditions per faulty run / total | Table III | 11 / 15 | 11 evaluated + T, A, H_faulty, H_EME-fail | yes |
| 58 | Lessons: EME-fail cut suspensions 20.79 -> 17.24 without losing recall | L2388 | as stated | as stated | yes |
| 59 | Detector misses "folded into composed artifacts" (abstract) / "only where folded into larger artifacts" (intro) | L1672, L1697 | all misses in composed artifacts | R2: 1 of its 2 miss runs is memory-only; R4: 1 of 13 memory-only (2 memory misses); ExpeL R4 missed a flat insight | **partial mismatch (wording)** |
| 60 | RQ1 box: "Its precision is bounded by the time cut ... slightly below under curation" | L2290 | precision slightly below T | H precision 0.102 is slightly *above* T's 0.096; it is the suspension set that is bounded and slightly smaller | **mismatch (wording)** |

Summary: 56 of 60 match exactly. There are two substantive mismatches: #32, the F1 claim for R3, and #13, the HS_judge vs R4 run count. There are two wording mismatches: #59 and #60.

## Remaining major issues

**N1. "Every content detector had higher F1" contradicts Table VII (L1672, L2241, L2290).**
- *Where it appears.* The abstract says closure "was barely more precise than rollback, and every content detector had higher F1". The RQ1 box says "Content detectors had higher F1 under both policies". E-L says "every detector had higher F1 than \sys{}".
- *What the data show.* Under curation the embedding detector R3 has mean F1 0.16 vs H 0.18 (Table VII, L2234). Run by run, H is higher in 27 of 42 runs and lower in 14 (Holm p = 0.091). Under the ExpeL-style policy R3 is 0.50 vs 0.48, with H higher in 5 and lower in 3, which is not "higher" in any meaningful sense either.
- *What is true.* R2, R4 and the revalidation variants had higher F1 under curation. **Every detector was more precise** (R3 0.119 vs H 0.102), which is what Lessons (L2390) and the conclusion (L2452) correctly say.
- *Requested change.* Say "TF-IDF and the LLM judge had higher F1", or "every detector was more precise", in all three places. Add the H vs R3 F1 test to L2241, so that the one comparison that favours H is reported with the same prominence as those that do not.

**N2. H_EME-fail is post hoc and undisclosed as such, but carries weight in the summaries (L1697, L2260, L2388, L2454).**
- *Timing.* The condition was introduced in response to round-4 review. That review identified the single EME-only run (llama3.1:8b F3 s3), and that run's task failed (`e9.outcome = fail`).
- *Why recall 1.00 is uninformative.* The recall of H_EME-fail on the one informative run is therefore known by construction of the variant. With n = 1 it says nothing about whether "failed runs only" preserves recall in general: a successful run that copies the faulty practice into a lesson is just as plausible.
- *What the paper says.* The baselines paragraph (L2141) and Threats (L2377) list T, A and H_faulty as post hoc, but not H_EME-fail. The introduction ("counting it only for failed runs kept full recall at lower cost", L1697), Lessons (L2388) and conclusion (L2454) present it as a finding.
- *Requested change.* Add H_EME-fail to the post-hoc list. State that it was defined after the analysis, and that its recall rests on a single run whose outcome was known. Phrase the summaries as a hypothesis, e.g. "a narrower EME policy (failed runs only) would have kept the one EME-only lesson at 17% less suspension". Likewise, state in Threats that the revalidation conditions were re-evaluated with revised semantics after the first analysis (`supplement_v1.json` ships, which is good).

**N3. Oracle validation (carried over from M5).**
- No human audit was done, and positive agreement is still not reported. Under curation the judges agree on only 143 of the 178 items that either labels YES (positive agreement 0.89).
- Report positive agreement next to kappa (L2239). Kappa 0.89 over 4,500 mostly-negative items overstates agreement on the items that drive recall.
- The human audit remains the most valuable missing validation. If it is not possible, the abstract's detector sentence should say that recall is measured against an LLM-judge oracle.

## Minor issues

- L2210: "within the agent's sensitivity to context order". The order claim was withdrawn (response, R2.M1). Replace with "within inference noise (4.1%)".
- L2206: "HS_judge differs in a single run". It differs in 2 of the 10 propagated runs (deepseek-coder-v2 F1 s2, where R4 also suspends seed profile D1-p0, and llama3.1 F2 s3). The pipeline CSV agrees.
- L2290 (RQ1 box): "Its precision is bounded by the time cut: equal to it under the ExpeL-style policy, slightly below under curation". It is the suspension set that is bounded by and slightly smaller than T; H's precision is slightly *higher* (0.10 vs 0.096). Rephrase.
- L2290 (RQ1 box): "recall 1.00 in all 52 propagated runs, as only rollback and reset did". This is true of the non-H conditions only: H_noDeps and H_EME-fail also have recall 1.00, and in the ExpeL-style policy R2, R3 and HS_emb have recall 1.00 in all 10 propagated runs. Say "of the conditions that apply to both policies".
- L1672, L1697: the R2 and R4 misses are not all in composed artifacts. One of R2's two miss runs and one of R4's 13 are memory-only, and the ExpeL-style R4 miss is a flat insight. "lost recall only where faulty advice was folded into larger artifacts" (L1697) overstates this; write "mostly".
- L2241: "kept recall high ... only because that threshold is low and suspends 11.27 revisions per run". 11.27 is 54% of H's suspension at recall 0.99 vs 1.00. State this as a result rather than a caveat (round-4 M3).
- L2141: "The revalidation conditions and T, A and H_faulty were added after the local pilot, before the reported campaign was analysed". The revalidation semantics were changed after the analysis (round 5), and H_EME-fail was added then too. See N2.
- L2149 and L2383: CIs remain package-only. At minimum, give CIs for the RQ1 recall/F1 comparisons in the text or in a supplementary table in the paper.
- Code: in `revalidate()`, an admission rejection does not propagate to dependents that `plan()` admitted. Execution can then diverge from `plan()`, although admission still rejects the dependents. Document or fix. The "plan == execution" test covers only a 5-revision toy.
- Code: `supplement.py` restricts restored copies to members active before withdrawal, while Algorithm 5 admits every cleared member of A. There is no effect in the data (1,820/1,820 restored members were active), but align the two or say why.
- Package: `environment.git` is still empty in every record. `live_summary.json` stores `campaign` as the command-line path, so re-running from another directory changes the file. `results/processed/live/nonexistent/` is a stray output from a run on a non-existent path; remove it. Unused all-run `precision` macros (`LiveCHPrec` etc.) are still generated.
- L2394 (Lessons): "independent generations of the same prompt differed on up to 4.1% of items". In the ExpeL-style campaign, 177 of the 178 flips are on prompts with an empty insight context, and the curation rate is 0.7%. Mention that the 4.1% is dominated by one prompt type, or give both rates.

## Recommendation

**Minor revision.**

The empirical core is sound and reproducible:
- I re-derived 60 numbers from raw data, including all new or changed ones: the revalidation rows and rejections, H_EME-fail, the independent-generation noise, closure vs cut by fault task, the F1 and collateral tests vs R2/R4, and the detector misses by kind. 56 match exactly.
- The pipeline reproduces byte for byte.
- The revalidation evaluated now matches Algorithm 5 and `heartness.revalidation` on all 150 plans.

Required before acceptance:
1. Correct "every content detector had higher F1" in the abstract, RQ1 box and E-L. R3 has lower F1 than H under curation. Also report the H vs R3 F1 test (N1).
2. Disclose H_EME-fail as post hoc, defined with knowledge of the single EME-only run. Soften its use in the introduction, Lessons and conclusion (N2).
3. Fix the leftover order-sensitivity sentence (L2210), "differs in a single run" (L2206), and the RQ1-box precision sentence (L2290).
4. Report positive judge agreement (N3).

A human audit of the oracle positives remains strongly recommended.
