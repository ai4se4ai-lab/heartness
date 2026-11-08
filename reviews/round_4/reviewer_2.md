# Round 4 -- Reviewer 2 (empirical rigor and verifiability)

Paper: "Traceable and Withdrawable Self-Evolution of AI Agent Harnesses: A Model-Driven Approach with Bounded Model Checking" (docs/TSE/main.tex and main.pdf, both dated 2026-11-07 14:05). Line numbers refer to main.tex. Table numbers refer to the compiled PDF: Table IV/V are the ExpeL-style model and containment tables, Table VI/VII the curation ones.

## Summary

This round adds the HumanEval+ x curation slice of experiment E-L: 75 faulty and 25 clean runs over 5 generators (Fir campaign am-20261107-080855). It also adds the post-hoc conditions T (rollback before the fault), A (reset learned state) and H_faulty, Proposition 1 (closure is bounded by the time cut), threshold curves, and a rewritten abstract, intro results, RQ1 answer and conclusion.

**Verification.**
- I re-ran `experiments.live.process report` on `results/raw/live-fir-curate` from a scratch directory. `live_runs.csv` is byte-identical to the shipped file. `live_summary.json` is identical except for absolute paths in `structure.eme_only`.
- Separately, I wrote an independent script (`/tmp/claude-1000/r4rev2/indep.py`) that reads only the raw `record.json`/`oracle.json`/`supplement.json`. It re-implements the closure, with its own EME edges from `experiences[*].run` and `loaded`, and reproduces the logged suspension sets of H, H_noEME and H_noDeps in 75/75 runs.
- Every curation number I checked matches (37 checks below).

**What the new slice shows.** It is informative, and it answers the main question of my round-3 review. Under curation:
- The closure is strictly narrower than a reset: 20.79 vs 29.00 suspended per run.
- EME edges change the closure in 55/75 runs and are needed for one contaminated revision.
- The embedding detector and the generator-as-judge miss contamination folded into skills and profiles.

The experimental machinery and the transparency remain excellent.

**Remaining problems.** They are about interpretation, not arithmetic:
1. **The determinism evidence is an artifact of the response cache.** The paper states three times that identical contexts always produce identical outcomes, and the "0 flips across processes" figure supports it only because every such item was a cache hit. Across runs, identical rendered prompts flip in 4.1% (ExpeL-style) of pairs. This also confounds the ExpeL-style order-sensitivity claim.
2. **Test reporting is selective.** Under curation, H's F1 is significantly *lower* than R2, R4 and HS_judge after Holm correction. The text reports the recall tests (where H wins) with p-values, but none of the F1 tests.
3. **The abstract and RQ1 answer are not calibrated against the pre-tuned TF-IDF baseline.** TF-IDF was tuned on a curation pilot. It missed contamination in only 2 of 42 runs (2 of 90 artifacts) while suspending about half as much as H. The abstract and RQ1 answer quote only the worst detector ("up to 22 of 42 runs").
4. **The oracle still lacks human validation.** Agreement under curation is lower (kappa 0.89, 35 disagreements, 30 ambiguous labels).

## Scores

| Criterion | Score (1-5) | Justification |
|---|---|---|
| Novelty | 3 | Unchanged. The lifecycle formulation (withdrawal across deployments, EME, rollback conflict) is new and useful. The curation slice now shows an empirical case where EME edges are the only lineage of a contaminated lesson. The model checking is solid but standard. |
| Rigor | 3 | Up from 2. Strengths: the reset and time-cut baselines; a curation slice with n = 42 informative runs spread over all 5 generators (6-11 each); H_noEME/H_noDeps now separated from H; an in-policy threshold baseline; a restricted Holm family with win/loss counts. Weaknesses: the determinism and order claims rest on cache replays; the curation F1 tests are not reported; no human validation of the oracle; no CIs or power statement in the paper; no model-stratified analysis. The closure-vs-cut result is largely fixed by the harness schedule and fault position (see M4). |
| Relevance | 4 | Unchanged. This is a maintenance problem for self-evolving coding agents that matters to SE. |
| Verifiability and Transparency | 4 | The pipeline reproduces byte-identically, the macro index maps every number, raw records and caches ship, and `make live-fir` now processes both campaigns. Deductions: one wrong p-value in prose (ExpeL-style, L2106); `environment.git` is still empty in every record; CIs and per-run values still appear only in the package; the noise checks look like evidence but are tautological. |
| Presentation | 3 | The writing is clear and the new curation sections are well structured. Several sentences overstate the result or contradict the data: the conclusion (L2354) says "only closure-based withdrawal removed every contaminated derivative", although T and A did too; the abstract says "at most 0.47%"; the intro says "reached skills and system prompts in 42". The Table VII caption mislabels the denominator of "Susp. (prop.)". |

## Status of round-3 issues

| Round-3 issue | Status | Evidence / remaining gap |
|---|---|---|
| M1 H equals a reset (ExpeL-style); no reset baseline | **Addressed** | T and A are added to Tables V and VII. L2090 states that H = T in 75/75 ExpeL-style runs. Under curation H suspends 20.79 vs A 29.00 and T 22.20 (L2160). The H-vs-T gap is small and mostly determined by design (M4). |
| M2 thresholds tuned on 2 informative runs; paraphrase claim | **Mostly addressed** | Disclosed at L2041. Curves are in Fig. 4/5, and "only F1 0.69" is gone. Not re-tuned. Dev F1 still prints 0.57/0.62 for 0.575/0.625 (macro `TauTfidfDev`/`TauEmbedDev`). Note that the pilot *was* curation, so under curation R2 is an in-policy baseline (see M3). |
| M3 behavioural evidence uninformative | **Partly addressed; one regression** | Seed-only pass@1 is reported (0.63 ExpeL-style, 0.62 curation, i.e. learned state again does not help). The "did not hurt" claim is withdrawn and the signature rate added. Per-model behavioural results are not reported. **Regression:** the 4% cross-process noise floor I requested is replaced by a cached-replay measurement that is zero by construction (M1 below). The round-3 response itself quoted "29/609 = 4.8%". |
| M4 roots / denominators | **Addressed** | Roots described (L2007), H_faulty added, curation has a single root. Adopted-subset results are computed (`LiveCAdopt*`, `LiveEAdopt*`) but not reported in the paper. |
| M5 oracle: human validation; sensitivity | **Partly addressed** | The ambiguous-as-contaminated sensitivity is reported (H recall 1.00 either way; adoption 53 -> 59). Human audit declined. Positive agreement is not reported. It matters more now: under curation 143 items are both-YES and 35 disagree (positive agreement 0.89). |
| M6 statistics | **Partly addressed** | (a) Clustering: curation is better balanced, but there is no stratified analysis and the conclusion-validity paragraph (L2286) states the effective n only for ExpeL-style runs. (b) Holm family restricted to 7: done. (c) Paired effect size: win/loss counts added. (d) Effective n: stated for ExpeL-style runs, implicit (via Hi counts) for curation. (e) CIs in tables: **not done**; L2286 says "report confidence intervals", but none appear in the paper. (f) Power / minimum detectable effect: **not done**. |
| M7 precision on runs with nothing to find | **Addressed** in text and tables. The all-run `precision` keys/macros (e.g. `LiveCHPrec` 0.06) still exist, unused. |
| M8 revalidation post hoc; "best F1" | **Addressed** (L2043, L2280, L2108). |
| M9 replication entry points | **Mostly addressed** | `make live-fir` processes both campaigns. `environment.git` is still `''`, so `source_sha256` is the only code identity. `results/` is untracked (acceptable before archiving). |
| M10 requirements for curation slice | **Met** | Adoption/propagation per generator and fault (Table VI, L2141); R0 (A) and T; H_noEME differs in 55/75 and H_noDeps in 0/75; curves; seed-only vs clean; RQ1 box does not claim superior F1; policies reported separately. |
| Minor: "two open-weight LLMs", "about 300 lines", MBPP+, "the faulty memory", D1-only eval, "no label was ambiguous", 630 revisions | **Fixed** | Verified at L1605, L1994, L2007, L2074, L2087. |
| Minor: "5.95 of about 8.0 live revisions" (L2090) | **Not fixed** | Still counts the two never-loaded seed profiles. The A row (6.00) now makes this visible, though. |
| Minor: monitor time overhead, E-S budget nondeterminism, ms timing noise | Not re-checked in depth | H_noDeps 0.3 ms vs H_noEME 41.9 ms for near-identical computations (curation) are still timing noise. |

## Number check

My values come from the independent script on raw JSON unless marked "pipeline". "Prop." is the 42 propagated curation runs.

| # | Claim | Location | Paper value | My value | Match |
|---|---|---|---|---|---|
| 1 | Faulty / clean curation runs | L2114, Table III | 75 / 25 | 75 / 25 | yes |
| 2 | Root adopted (with ambiguous) | L2141 | 53 (59) | 53 (59) | yes |
| 3 | Runs with propagation; derivatives | L2141 | 42; 90 | 42; 90 | yes |
| 4 | Propagated by fault F1/F2/F3 | L2141 | 7 / 17 / 18 | 7 / 17 / 18 (adopted 16/17/20) | yes |
| 5 | Contaminated by kind skill/profile/memory | L2141 | 42 / 43 / 5 | 42 / 43 / 5 | yes |
| 6 | Table VI rows (adopt/spread/cont/live/H susp/clean), all 5 generators | Table VI | e.g. Qwen 14/11/32/29.0/20.9/0.76; DS 6/6/12/29.0/21.4/0.69 | identical for all 5 rows | yes |
| 7 | Clean-run labels: revisions, labels, ambiguous, contaminated | L2141 | 750, 2,250, 5, 0 | 750, 2,250, 5, 0 | yes |
| 8 | Judge agreement, kappa | L2141 | 99.2% of 4,500; 0.89 | 0.9922 of 4,500; 0.887 (143 both-YES, 35 disagree) | yes |
| 9 | Residual none/R1 | L2143, Table VII | 1.20 | 1.20 | yes |
| 10 | H recall, recall with ambiguous-as-contaminated, residual | L2143 | 1.00, 1.00, 0.00 | 1.00, 1.00, 0 | yes |
| 11 | R3 recall; runs with misses; profile misses | L2143 | 0.68; 22; 28 | 0.679; 22; 28 profile + 6 skill | yes |
| 12 | R4 recall; runs with misses; skill/profile misses | L2143 | 0.79; 13; 12/7 | 0.787; 13; 12 skill, 7 profile, 2 memory | yes |
| 13 | Recall H>R3 / H>R4 runs; Holm p | L2143 | 22, 13; <0.001, 0.004 | 22, 13 (never lower); Holm 1.8e-4, 0.0039 | yes |
| 14 | R2 recall; runs with misses; susp/run; precision (prop.) | L2143 | 0.99; 2; 11.27; 0.24 | 0.989; 2; 11.27; 0.235 | yes |
| 15 | Oracle-tuned TF-IDF tau, F1, recall; embedding max F1 | L2143 | 0.15, 0.69, 0.75; 0.21 | 0.15, 0.695, 0.749; 0.215 (pipeline 0.69) | yes |
| 16 | Susp/run H / T / A | L2160 | 20.79 / 22.20 / 29.00 | 20.787 / 22.20 / 29.00 | yes |
| 17 | H subset of T; strictly smaller | L2160 | 75; 42 | 75; 42 (only 22 of them are propagated runs; 0/15 runs with fault at task 2) | yes |
| 18 | Revisions in T minus H, all memories before first composition, never loaded a closure member | L2160 | 106, all | 106 memories, 106 before task 12, 0 loaded a closure member | yes |
| 19 | Profiles in closure | L2160 | 75 of 75 | 75 | yes |
| 20 | H precision (prop.), F1; "lower than every detector" | L2160 | 0.10, 0.18 | 0.102, 0.180; R3 0.119, R2 0.235, R4 0.784 | yes |
| 21 | H_faulty misses | L2160 | 3 runs, root "not labelled contaminated" | 3 runs; in all 3 the root is *ambiguous* (judges split) | yes (wording, m4) |
| 22 | H_noEME differs; susp; F1; EME-only runs | L2162 | 55; 14.39; 0.31; 1 | 55; 14.39; 0.308; 1 (llama3.1:8b F3 s3, m9) | yes |
| 23 | EME-run narrative (m8 text, retrieved by next task, F3 signature, sources m4/m0, m9 text) | L2162 | as quoted | verified in record (`evolution[9]`: context D2-p0,m4,m8,m0; signature F3=True; `reflect_exposed` m4,m0) | yes |
| 24 | Runs with more collateral without... (H vs H_noEME) | L2162 | 55 | 55 | yes |
| 25 | H_noDeps differs; H_local recall; H_local residual in every propagated run | L2162 | 0; 0.03; every | 0; 0.031; 42/42 | yes |
| 26 | HS_judge susp (prop.), F1, runs restoring contamination, recall; HS_emb recall | L2164 | 2.71, 0.70, 13, 0.79; 0.68 | 2.714, 0.697, 13, 0.787; 0.679 | yes |
| 27 | Pass@1 none / H / clean / seed-only | L2166 | 0.61 / 0.62 / 0.61 / 0.62 | 0.610 / 0.620 / 0.611 / 0.623 | yes |
| 28 | Prop. pass@1 none -> H; higher/lower; Holm p | L2166 | 0.60 -> 0.62; 23/13; 0.338 | 0.597 -> 0.624; 23/13 (6 ties); raw 0.084, Holm 0.338 | yes |
| 29 | Prop. signature none -> H; lower/higher; Holm p | L2166 | 0.04 -> 0.02; 12/2; 0.071 | 0.044 -> 0.023; 12/2; raw 0.0101, Holm 0.071 | yes |
| 30 | Identical-context flips within / cross process; order flips | L2166 | 0/1,850; 0/524; 6/343 | same numbers, but all 3,051 repeated supplement prompts were cache hits; order: 6/253 within, 0/90 across | numerically yes; **interpretation wrong** (M1) |
| 31 | Curation cost: minutes, engine s, % of evolution, calls, events | L2250 | 6.1, 1.71, 0.47%, 305, 156 | 6.11, 1.713, 0.468% (ratio of means), 305.4, 156 | yes |
| 32 | Withdrawal plan H vs R4 (curation) | L2250 | 29.3 ms vs 66,236.9 ms | 29.3 vs 66,236.9 | yes |
| 33 | Total LLM calls (both policies) | Table III | 42,811 | 17,056 + 25,755 = 42,811 (generation records only) | yes |
| 34 | Propagation all policies | L1588, L1605 | 52 of 150 | 10 + 42 = 52 | yes |
| 35 | "reached skills and system prompts in 42 of 75 runs" | L1605 | 42 | skills or profiles 42; **profiles only 28** | **partial mismatch** |
| 36 | "adds at most 0.47% to evolution time" | L1588 | at most 0.47% | 0.47% is the larger of two policy means; per-run maximum is 0.77% | **mismatch (wording)** |
| 37 | ExpeL-style F1 tests "p=0.273 for both" (H vs R4 and H vs R2) | L2106 | 0.273 for both | R4 Holm p = 0.273; R2 Holm p = 0.352 (`LiveETestFoneRtwoP`) | **mismatch** |
| 38 | "Identical contexts always produced identical outcomes" | L2112, L2166, L2280 | 0 flips | identical rendered prompts (same model, seed, task, deployment, context *texts*) across run directories: 178/4,349 (4.1%) ExpeL-style, 2/273 (0.7%) curation | **mismatch** (M1) |
| 39 | Running example gemma2:9b F1 seed 2 (m7 text, k1 step 4, D1 profile five rules) | L1647 | as quoted | verified verbatim; m7, k1, D1-p24, D2-p24 all oracle-contaminated | yes |
| 40 | Fault positions | L2007 | tasks 2, 8, 9 | `fault_index` 1/7/8 (0-based) in 15/45/15 runs | yes |

## Major issues

**M1. The determinism evidence is produced by the response cache, and the order-sensitivity claim is confounded (L2112, L2166, L2280, L2297).**
- *Claims.*
  - The paper states "Inference itself was deterministic: whenever two evaluations of the same task used exactly the same context, they agreed (0 differences in 4,709 ... within one process, 0 in 58 across processes)" (L2112), the curation equivalent (L2166), and "identical contexts always produced identical outcomes in our runs" (L2280).
- *Why the zeros prove nothing.*
  - `experiments/live/llm.py` caches every response under a key of (model, prompt, options including seed), and each process loads every cache file in the directory.
  - Any repeated prompt within a process is therefore a cache hit. The supplement process that supplies the "cross-process" items reads the run's cache too: across the 75 curation supplements, the 3,051 eval items whose prompt had already been issued equal exactly the 3,051 supplement cache hits.
  - The zeros are tautological. They do not measure inference determinism.
- *What a real test shows.* When the cache was not shared (different run directories), identical rendered prompts produced different pass/fail outcomes. I matched on model, seed, task, deployment and the *texts* of the context artifacts, so the prompts are byte-identical. Result: 178 of 4,349 pairs flip (4.1%) in the ExpeL-style campaign and 2 of 273 in curation.
- *Consequences.*
  - (a) The three sentences are false and must be removed or reworded.
  - (b) In the ExpeL-style slice, all 579 order-sensitivity items compare the in-process `none` evaluation with the separate supplement process. Their 5.2% flip rate is indistinguishable from the 4.1% cross-process rate for *identical* prompts, so "Prompt order, however, matters" (L2112) and "merely reordering ... changed up to 5.2%" (L2297) are not identified. In curation the within-process order items show 6/253 (2.4%), which is better evidence but small.
  - (c) Comparisons with the clean-run reference and the seed-only harness are subject to this ~4% item-level noise.
- *Requested changes.* Report the cross-run identical-prompt flip rate as the noise floor. Say explicitly that within-process identity is enforced by the cache. Restrict the order-sensitivity claim to within-process items, or drop it.

**M2. Selective reporting of significance tests under curation (L2143, L2160, L2193).**
- *What is reported.* The curation text gives Holm-adjusted p-values only where H wins (recall vs R3/R4).
- *What is not.* The pipeline's F1 tests, from the same Holm family, show H *worse*:

  | Comparison | H better | H worse | Holm p |
  |---|---|---|---|
  | H vs R2 | 0 runs | 42 runs | < 0.001 |
  | H vs R4 | 6 runs | 36 runs | < 0.001 |
  | H vs HS_judge | 6 runs | 36 runs | < 0.001 |

  Collateral is also significantly higher than for every detector, including R3 (Holm p = 0.048).
- *Current wording.* The text says only that H's precision "remained low ... lower than that of every detector".
- *Requested change.* Report the F1 and collateral tests next to the recall tests, with the same prominence. Add one sentence to the RQ1 answer: under curation H's F1 is significantly lower than TF-IDF's and the judge's.

**M3. The abstract, intro and RQ1 answer are calibrated against the worst detector (L1588, L1605, L2168, L2193, L2354).**
- *What the paper says.* The abstract says detectors "missed it in up to 22 of 42 runs", and the RQ1 answer and the "both policies" paragraph say the same.
- *Where 22 comes from.* That is the embedding baseline (F1 0.16, the weakest condition).
- *The omitted baseline.* The baseline tuned *on a curation pilot* is TF-IDF at tau = 0.05 (L2041). It:
  - missed contamination in 2 of 42 runs (2 of 90 artifacts);
  - did not differ significantly from H in recall (Holm p = 0.18) or residual (p = 0.157);
  - suspended fewer revisions than H in 73/75 runs (11.27 vs 20.79);
  - had twice H's F1 (0.36 vs 0.18).
- *Misleading phrasing.*
  - "only because that threshold is low and suspends 11.27 revisions per run" (L2143) frames as a weakness a suspension set that is about half of H's.
  - The conclusion (L2354), "only closure-based withdrawal removed every contaminated derivative under both policies", is contradicted by T and A (recall 1.00 in both policies, Tables V and VII), which L2168 itself acknowledges.
  - "they fail exactly where synthesis dilutes" (L2356) does not hold for TF-IDF.
- *Requested changes.*
  - State the per-detector miss counts (R2 2, R4 13, R3 22 of 42) in the abstract or RQ1 box.
  - State that the pilot-tuned TF-IDF nearly matched closure's recall at about half its suspension cost.
  - Fix the conclusion sentence.
- *Underlying point.* The defensible claim is that closure gives a recall *guarantee* relative to recorded exposure, whereas detectors' recall varies with the detector and the generator. The measured difference, by contrast, is 2 artifacts against the best detector.

**M4. The closure-vs-time-cut result is mostly fixed by the harness schedule and the fault position (L2160, L2291).**
- *Why it is structural.*
  - The curator merges *all* six recent memories into a skill, and the corrupted feedback always lands at task 2, 8 or 9, i.e. before a merge at task 6 or 12. The root is therefore a source of a skill in every run.
  - Profiles are composed from all current skills, and every later task loads its profile. Hence every post-composition revision is in the closure in 75/75 runs, whatever the LLM wrote.
- *What remains for H to save.* The only room for H < T is the 0-4 memories written between the fault and task 12, which are exposed or not depending on TF-IDF retrieval. The data show exactly this:
  - strictly smaller in 0/15 runs with the fault at task 2, 33/45 at task 8, 9/15 at task 9;
  - all 106 spared revisions are such memories.
- *What the paper already says.* It explains the mechanism well. It should also state plainly that, given this schedule, closure = time cut after task 12 is a deterministic consequence of the policy design, not an empirical finding about LLM self-evolution, and that the 1.4-revision gap per run depends on fault position.
- *What the evidence covers.* A policy with selective contexts, which the paper recommends (L2291, L2356), is not evaluated, so "closure can be much narrower than a rollback" remains a hypothesis.

**M5. Ground truth is still two LLM judges, and under curation it is noisier (L2141, L2278).**
- *Curation agreement figures.* Kappa falls from 0.99 to 0.89. There are 35 judge disagreements and 143 both-YES items (positive-specific agreement 0.89). There are 24 ambiguous non-root labels and 6 ambiguous roots.
- *Where ambiguity matters.* All 3 runs in which H_faulty misses contamination have an *ambiguous* root, not a clean one. L2160's "the root itself was not labelled contaminated" should say so.
- *Circularity.* The headline detector comparison has a circular element. The oracle is an LLM judge reading the very artifact, so a stronger external LLM judge (R4 with the oracle models) would by construction approach the oracle. The R4 misses are also concentrated by generator: DeepSeek 5 and Granite 5 of the 13 runs.
- *Requested changes.*
  - Scope the claim as "the generator acting as its own judge" (which L2280 already does) also in the abstract and RQ1 box.
  - Report positive agreement.
  - Ideally, run a human audit of the 90 curation positives plus a stratified sample of negatives in the closure. This is the single most valuable remaining validation.

**M6. Statistical reporting gaps that remain from round 3 (L2051, L2286).**
- *CIs.* L2286 states "report confidence intervals", but no CI appears in the paper. With n = 42 the bootstrap intervals are informative now; put them in Tables V and VII, or at least on the RQ1 metrics.
- *Effective n.* Conclusion validity gives only the ExpeL-style effective n (10). Add 42 for curation, and the nonzero-difference counts per test.
- *Clustering by generator.* With 5 generators, a stratified permutation test (or a run-level mixed model) is now feasible and would answer the clustering concern from round 3.
- *Families.* The Holm family is per metric. Eight metrics x 2 policies are tested without any statement of which metric is primary. Name recall/residual as primary, or adjust across metrics.

## Minor issues

- L1588: "adds at most 0.47%": these are policy means (ratio of means). The per-run maximum is 0.77%. Write "on average 0.21% and 0.47%".
- L1605: "it reached skills and system prompts in 42 of 75 runs": skills or profiles in 42; profiles in 28.
- L2106: "($p\LiveETestFoneRfourP$ for both)" prints p = 0.273 for both. H vs R2 has p = 0.352 (`LiveETestFoneRtwoP`).
- L2090: "suspended 5.95 of about 8.0 live revisions" still counts the two seed profiles that ExpeL contexts never load. Say "of 6.0 learned revisions".
- L2041: dev F1 0.575/0.625 print as 0.57/0.62. Use three decimals.
- L2130 (Table VII caption): "all other columns over all 75 faulty runs" is wrong for "Susp. (prop.)", which is over the 42.
- L2157 (Fig. 5 caption): "H and R2 at the frozen threshold are the only conditions with recall near 1". T, A, H_noDeps and H_noEME (0.99) also have recall near 1. Restrict the statement to the plotted conditions.
- L2160: "lower than that of every detector at its frozen threshold" is true but marginal for R3 (0.119 vs 0.102). For R2 and R4 the difference is large and significant; say so (M2).
- L2162: "EME edges therefore bought one contaminated revision ... at the price of 55 runs with more collateral". Quantify the price: about 6.4 extra suspensions per run (20.79 vs 14.39), i.e. about 480 suspended clean revisions for one contaminated one.
- L2166: the propagated-run pass@1 gain (0.60 -> 0.62, raw p = 0.084) is about 0.8 items of 29, below the 4% cross-process item noise (M1).
- L2280: the CPU-fallback statement covers only oracle jobs. `inference_devices.tsv` also shows 4 generation attempts on CPU (jobs 2844959_0, 2870807_0/1, 2876676_1). I verified by host and timing that the reported seed-0 records come from GPU attempts. Say so, so readers do not have to check.
- L2286: "report confidence intervals": see M6.
- L2297: "reordering the same context changed up to 5.2% of outcomes": confounded (M1).
- L2354/L2356: see M3.
- Pipeline: the `structure.eme_only` field stores the absolute or relative path as given on the command line, so re-running from another directory changes `live_summary.json`. Store paths relative to the campaign.
- Records: `environment.git` is still empty. Ship the source tree whose hash is `source_sha256` = `2d88e045...`.
- `live_summary.json` still exposes all-run `precision` (e.g. H 0.06) and A12 values that the paper no longer uses. Rename or drop them, so that no later edit picks them up.

## Recommendation

**Minor revision.**

The round-3 blocking concern (H is a reset) is resolved by the curation slice and the T/A baselines. The numbers are correct: 36 of 40 checks match exactly, and the 4 discrepancies are prose (one wrong p-value, two wording overstatements, and the false determinism claim). The pipeline is reproducible byte for byte.

What remains is calibration and honest reporting, all fixable in text:
- correct the determinism and order claims (M1);
- report the curation F1 and collateral tests where H loses (M2);
- state in the abstract and RQ1 answer that the pilot-tuned TF-IDF missed only 2 of 42 runs at half H's suspension cost, and fix the conclusion (M3);
- state that closure = time cut after composition is a property of the harness schedule (M4);
- add CIs and the curation effective n (M6).

A human audit of the oracle positives (M5) is strongly recommended. Without it, the paper should scope its detector claims to the generator acting as its own judge.
