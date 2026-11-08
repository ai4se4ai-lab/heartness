# Round 3 -- Reviewer 2 (empirical rigor and verifiability)

Paper: "Traceable and Withdrawable Self-Evolution of AI Agent Harnesses: A Model-Driven Approach with Bounded Model Checking" (docs/TSE/main.tex, draft of 2026-11-07)

Scope of this review: experimental design, statistics, ground truth, whether each number traces to logged results, and replicability. The HumanEval+ x curation slice, the RQ1 answer box, the abstract, the intro results paragraph and the conclusion are placeholders. I do not penalize their absence. I judge everything else as it stands.

## Summary

The paper proposes HEARTNESS, a controller for self-evolving agent harnesses. It records exposure (synthesis sources, use dependencies and experience-mediated exposure, EME). It also provides guarded admission, closure-based withdrawal that propagates to deployments, and rollback rules, with bounded model checking (BFS and SPIN) and a conformance monitor.

The evaluation has three subjects:
- **S1, live harness:** an ExpeL-style self-evolving coding harness on HumanEval+, with 5 open-weight generators x 5 seeds x (3 planted faults + 1 clean) = 100 runs.
- **S2, synthetic:** a synthetic provenance benchmark with 1,905 records.
- **S3, public library:** a replay of Voyager's skill library.

The verification pipeline is in good shape. I re-ran `experiments/live/process.py report` into a scratch directory and got a byte-identical `live_runs.csv` and an identical `live_summary.json`. An independent script I wrote from the raw `record.json`/`oracle.json`/`supplement.json` files reproduces every live number I checked.

The problems are in design and interpretation, not in arithmetic:
1. **H is a reset in the ExpeL slice.** H suspends every evolved revision in 71 of 75 runs, so it behaves like "reset to the seed harness". The paper has no such baseline, and the text hides the equivalence.
2. **The similarity-baseline thresholds rest on two runs.** They were tuned on only 2 informative pilot runs, under a different root definition, and they sit at the grid boundary. On the reported data, TF-IDF beats H at every threshold in the grid.
3. **The paraphrase narrative is not supported by the live data.** The paper says LLM synthesis paraphrases lessons, but contaminated derivatives are verbatim copies of the root.
4. **The behavioural evidence is uninformative.** Discarding all evolved state gives a higher pass@1 than keeping it, so "collateral did not hurt" carries no information.
5. **Several sentences contradict the data.** They are listed in the number-check table below.

The live study is honest about adoption rates and non-significance. Its framing still has to change from "HEARTNESS contains contamination" to "in a flat, fully cross-sourced policy, closure degenerates to reset, and closure plus revalidation is a reasonable compromise". The pending curation slice is where HEARTNESS can show something a reset cannot.

## Scores

| Criterion | Score (1-5) | Justification |
|---|---|---|
| Novelty | 3 | Lifecycle semantics for withdrawal and rollback across deployments, plus EME capture, is a new and useful formulation. The model checking and witness replay are solid but standard. The empirical novelty claim ("first measurement of propagation in a running harness") is weakened because, in the only completed slice, the approach is equivalent to resetting all evolved state. |
| Rigor | 2 | Pairing, Holm correction and the decision to report adoption are good. Against that: no reset baseline; thresholds tuned on 2 informative runs at a grid boundary under a different root definition; n = 10 informative runs clustered in 3 of 5 models (6 from one model); a promised sensitivity analysis that is never reported; no human validation of the oracle; an unmeasured 4.1% evaluation-noise floor; behavioural claims that a "remove everything" control would explain. |
| Relevance | 4 | Highly relevant to SE for LLM agents: poisoning and persistence of learned state (EVOMAL) is a live problem, and the maintenance framing (origin, impact, withdrawal) fits TSE. |
| Verifiability and transparency | 4 | Excellent: generated macros with a source index, raw records with oracle votes, LLM caches, and a deterministic processing script that I reproduced exactly. Deductions: the Makefile and README do not reproduce the reported campaign (`live-results` processes `live-qwen25-7b`/`live-llama31-8b`, not `live-fir`); `results/` is untracked in git; the `git` field in run records is empty; CIs and per-run values appear only in the package, not in the paper. |
| Presentation | 3 | Clear writing and good structure. However, several sentences contradict the data (listed below), and the "Live" denominator includes seed profiles that can never be suspended. Table III mixes "all-run" and "propagated-run" denominators across columns, which readers will misread. |

## Number checks

Columns: the claim, the value in the paper, the value I found in the source, and the verdict. "Recomputed" means I computed it independently from the raw records under `results/raw/live-fir` -> `hpc/fir/am-20261107-060101/live`.

| # | Claim (main.tex line) | Paper value | Source value | Verdict |
|---|---|---|---|---|
| 1 | Faulty / clean runs (948) | 75 / 25 | 75 record+oracle dirs; 25 clean (recomputed) | OK |
| 2 | Runs with an adopted root (998) | 21 | `root_adopted` 21; recomputed 21 | OK |
| 3 | Runs with propagation (998) | 10 | `propagated_runs` 10; recomputed 10; no run propagates without an adopted root | OK |
| 4 | Contaminated derivatives (998) | 16 | recomputed 7+0+0+3+6 = 16 | OK |
| 5 | Per-generator adoption/spread/contaminated (Table II) | e.g. Qwen 10/6/6, DS 3/2/7 | recomputed identical for all 5 rows | OK |
| 6 | Per-fault adopted/spread (998) | F1 5/1, F2 7/5, F3 9/4 | recomputed identical | OK |
| 7 | Live / H-suspended per run (1014, Table II) | 8.0 / 5.95 | recomputed 8.0 / 5.96 | OK numerically. Misleading: "Live" counts the 2 seed profiles, which ExpeL contexts never load. H suspends 99.2% of evolved revisions, and all of them in 71/75 runs. |
| 8 | H precision/recall/F1 on propagated runs (Table III) | 0.33 / 1.00 / 0.48 | recomputed 0.335 / 1.000 / 0.479 | OK |
| 9 | R4 precision/recall/F1 (Table III) | 0.55 / 0.90 / 0.65 | recomputed 0.553 / 0.900 / 0.647 | OK |
| 10 | HS_judge F1, suspended per propagated run (1016) | 0.67, 3.50 | recomputed 0.670, 3.50 | OK |
| 11 | R2 F1 (1014) | 0.60 | recomputed 0.601 | OK |
| 12 | Residual, none/R1 (1012) | 0.21 | 16/75 = 0.213 | OK |
| 13 | Judge agreement (998) | 99.9% of 1,384, kappa 0.99 | recomputed 0.99928 / 0.9866; exactly one disagreement | OK numerically |
| 14 | "no label was ambiguous" (998) | 0 ambiguous | 1 ambiguous label: granite3.3_8b/expel/F3/seed-2, root r2 ("Ensure all operations are integer-based ..."), mistral NO / phi4 YES. It is a root, so the non-root count of 0 is technically right, but the sentence is false and the adoption count would be 22 under the stated sensitivity rule. | **Mismatch** |
| 15 | "none of the 630 revisions of the clean runs" (998) | 630 revisions | 210 revisions, each labelled for 3 faults = 630 labels | **Mismatch (unit)** |
| 16 | Evolution time / controller time / share (1104) | 3.9 min / 0.49 s / 0.21% | 233.9 s / 0.491 s / 0.210% (ratio of means; mean of ratios is 0.217%) | OK |
| 17 | Withdrawal-plan times (1104) | H 20.3 ms, R4 20,614.6 ms | recomputed 20.3 / 20,614.6 | OK. Note H_noDeps takes 0.4 ms for an identical computation, so the ms figures are timing noise at this scale. |
| 18 | LLM calls (948) | 17,056 | sum of `llm.calls` over the 100 generation records = 17,056. This includes about 5.6k cache hits and excludes the oracle-phase calls. | OK, but the definition is not stated |
| 19 | Oracle-tuned bound (1014) | F1 0.69 at tau 0.50 / 0.80 | 0.6897 at 0.50 (TF-IDF) and 0.80 (embedding) | OK. Wording "only" is misleading (see Major 2). |
| 20 | Pass@1 none / H / clean (1020) | 0.59 / 0.62 / 0.61 | 0.589 / 0.617 / 0.610 | OK. The macro `LiveEPassSeed` = 0.63 (seed-only, no evolved state) is computed but never reported. |
| 21 | Propagated pass@1 and signature, none -> H (1020) | 0.60 -> 0.68; 0.09 -> 0.02 | recomputed identical. The 0.08 gain comes from 4 Qwen runs; H lowers pass@1 in all 4 DeepSeek/Llama propagated runs. | OK numerically |
| 22 | Holm p and A12 (1012, 1020) | recall p 0.020, A12 1.00; pass_prop p 1.000, A12 0.70 | `tests_H_vs` identical (raw p 0.00195 and 0.232) | OK |
| 23 | Pilot thresholds (965) | tau_t 0.05 (dev F1 0.57), tau_e 0.55 (0.62) | thresholds.json 0.05 / 0.575, 0.55 / 0.625. Only **2 of 6** dev runs had any contamination; tau_t sits at the grid minimum. | OK numerically; design problem |
| 24 | Synthetic impact F1, history / lexical / ours (1027) | 0.155 / 0.699 / 1.000 | summary.json rq1 0.1548 / 0.6989 / 1.0 | OK |
| 25 | Capture sweep (1045) | 1.000 / 0.833 / 0.572 / 0.289 / 0.103 | summary.json capture identical | OK. The non-zero F1 at 0% capture needs an explanation. |
| 26 | Linter (1027) | F1 0.229, 90 cases, 0 alarms | summary.json linter identical | OK |
| 27 | E-C correspondence (1073) | 3,000 / 992 / 0 | 708 + 2,292 = 3,000; enabled 992; 0 mismatches | OK |
| 28 | Monitor (1127) | 30, 30, 29, 0 of 30 | summary.json conformance identical | OK |
| 29 | Witnesses (1073) | 13, lengths 2-7, all minimal | 13 records, lengths {2,4,5,7}, all `shorter_safe` | OK |
| 30 | "driven by two open-weight LLMs" (575) | 2 | 5 generators (plus 2 judge models and 1 embedding model) | **Mismatch** |
| 31 | Held-out tasks solved with "$D_1$'s context" (983) | D1 only | `eval` entries alternate D1/D2: 1,125 D1 and 1,050 D2 items over 75 runs | **Mismatch** |
| 32 | "All receive the same root (the faulty memory)" (956) | one root | `roots` holds 1-4 revisions (16x1, 44x2, 10x3, 5x4; mean 2.05). They are insights, not memories, and most are clean. | **Mismatch** |
| 33 | Live harness "about 300 lines" (920) | ~300 | experiments/live/*.py has 1,494 lines; harness.py alone has 380 | **Mismatch (minor)** |
| 34 | Behavioural measure uses "HumanEval+/MBPP+ tests" (1132) | MBPP+ | No MBPP+ run is reported, and none is pending per the draft status. MBPP configs exist only for narval/rorqual. | **Mismatch** |

Two further checks:
- **Pipeline re-derivation.** I ran `report()` with `OUT_ROOT` redirected to a scratch directory. The JSON is identical (apart from the campaign path) and the CSV is byte-identical. This used scipy 1.11.4; the pin is 1.16.3.
- **Evaluation-noise floor (recomputed).** I compared H in each faulty run with seed_only in its paired clean run. Both use an empty insight context and identical prompts, model and seed. Of 2,059 such items, 85 (4.1%) flip pass/fail, and 50 of 75 runs contain at least one flip. Within a run the cache makes identical contexts identical (H vs H_noEME: 0/2,175 differ), so within-run comparisons are unaffected. Comparisons to the clean reference are not.

## Strengths

1. **Traceability of numbers is exemplary.** Every number in the paper is a generated macro with a source index. Raw records keep per-judge votes, contexts, suspension sets and per-task outcomes, and the processing script is deterministic and reproduced exactly. Few TSE submissions reach this level.
2. **Adoption is reported honestly.** Separating adoption (21/75) from propagation (10/75), and restricting recall to informative runs, is the right call. The Lessons section turns it into a recommendation for the field.
3. **Non-significance is reported as such** (F1 vs detectors; behavioural effects), and the pass@1 claim is framed as a direction, not an effect.
4. **Ground truth is independent of HEARTNESS's records.** The judges never see exposure edges, the clean-run false-positive check is in place, and judge families differ from the generator families.
5. **The RQ2 evidence chain is strong for what it claims.** It has two encodings, witness replay on the implementation, minimality checks, negative controls, and mapped-state correspondence. The account of the specification gap found by replay, shared by both encodings, is valuable.
6. **The negative results stay in the paper:** ablations that change nothing in ExpeL, H_local having no effect, and capture sensitivity where lexical recovery wins below about 60% capture.

## Major concerns

**M1. In the ExpeL slice HEARTNESS is equivalent to "reset all evolved state", and the paper has no such baseline.**
- *Evidence.* H suspends every evolved non-root revision in 71/75 runs (mean 99.2%). Its held-out evaluation context is empty in the same 71 runs. The paper's phrase "suspended 5.95 of about 8.0 live revisions" (line 1014) hides this, because 2 of the 8 are seed profiles that ExpeL never loads.
- *Consequence.* Recall 1.00 and the behavioural results are therefore the results of a trivial remedy. "Discard everything learned since the root" would score identically and needs no provenance.
- *Requested changes.*
  - Add R0 = "reset to the snapshot before the root" (or "discard all evolved state") as a baseline in every table.
  - Report |closure| / |evolved state| per run.
  - Rewrite "the price of closure" so it states the equivalence explicitly.
  - The pending curation slice must show that H differs from R0, i.e. that it suspends a strict and useful subset. Otherwise the live study does not support the containment contribution.

**M2. The similarity-baseline thresholds rest on 2 informative runs, and the "paraphrase" explanation contradicts the data.**
- *Pilot and tuning.*
  - Of the 6 pilot dev runs (`results/raw/live-qwen25-7b`, seeds 100/101), only 2 had any contaminated non-root artifact, so mean dev F1 is computed over 2 runs.
  - The pilot used the old single-root definition (`root: m1/m6`, about 30 live artifacts, curation policy, qwen2.5:7b rather than the coder model).
  - The reported study uses "all revisions motivated by the corrupted experience" as roots (PROJECT_LOG, session 3).
  - tau_t = 0.05 is the grid minimum: dev F1 is 0.57 at 0.05 and 0.25 at 0.10, a cliff. `tune()` also breaks ties toward the smallest tau.
- *Reported data.* TF-IDF F1 is 0.66-0.69 for every tau in [0.10, 0.70], and embedding F1 is 0.69 for tau >= 0.80, both with recall 1.0. The contaminated derivatives are verbatim copies of the root: in the paper's own example (DeepSeek F1 seed 2), r3, r5 and r13 are all exactly "Ensure functions print their final answer with print().".
- *Consequences.*
  - (a) Line 1014, "a low threshold is needed to catch paraphrases", is false for this data.
  - (b) Line 1014, "even their oracle-tuned upper bounds reached only F1 0.69", is misleading: 0.69 is the best F1 of any condition, above H (0.48) and HS_judge (0.67).
  - (c) Line 1171, "similarity between a root and its derivatives is low", is contradicted by the live study.
- *Requested changes.*
  - State the number of informative dev runs and the root-definition change.
  - Report the full F1-vs-tau curve on the reported runs (a supplementary figure).
  - Either re-tune on dev runs of the reported design or present the frozen thresholds as a weak baseline.
  - Remove the paraphrase claim for ExpeL, or support it with the curation slice.

**M3. The behavioural evidence cannot separate "removing contamination" from "removing state".**
- *Evidence.*
  - Seed-only pass@1 (no evolved state) is 0.632, higher than the evolved clean harness (0.610). The macro `LiveEPassSeed` is computed but never reported.
  - Evolved state therefore has no positive value on the held-out tasks, so "Suspending clean insights did not measurably hurt" (line 1020) is guaranteed and uninformative.
  - The rise from 0.60 to 0.68 on propagated runs comes from 4 Qwen runs (for example 0.41 -> 0.79 and 0.45 -> 0.76). H lowers pass@1 in all 4 DeepSeek/Llama propagated runs (0.66 -> 0.62, 0.62 -> 0.59, 0.52 -> 0.48, 0.55 -> 0.48).
  - Each run has 29 tasks with one sample at temperature 0, and the cross-process flip rate is 4.1% per item.
- *Requested changes.*
  - Report the seed-only reference.
  - Report per-model behavioural results.
  - Report the noise floor in the paper, alongside the platform/temperature-0 discussion.
  - Either drop the "did not hurt" sentence or measure collateral cost on a task distribution where the evolved state demonstrably helps (clean > seed-only).

**M4. The root definition and the all-run metrics inflate collateral and blur the operational scenario.**
- *Definition.* Roots are all revisions motivated by the corrupted 4-task batch (1-4 per run, mean 2.05), and most are clean. In 54/75 runs no root was contaminated, yet every remedy, H included, was "applied".
- *Effect on metrics.* Collateral and suspension averages over all 75 runs (Table III, "Susp. (all)", "Collateral") mostly measure withdrawing a lesson nobody would withdraw.
- *Effect on fairness.* Giving all co-roots to every remedy also benefits closure: it starts from a superset.
- *Requested changes.*
  - Make the operational scenario explicit: withdrawal is triggered when a contaminated revision is detected.
  - Report the main table on (a) adopted runs (n = 21) and (b) propagated runs (n = 10).
  - Run a variant in which the roots are only the oracle-contaminated root revisions.
  - Fix line 956 ("the faulty memory").

**M5. The oracle needs human validation, and the promised sensitivity analysis is missing.**
- *Oracle validation.* The whole RQ1 ground truth is 38 unanimous YES labels from two LLM judges. Kappa 0.99 is pooled over 1,384 items, 97% of them easy NOs, and 630 of the items are clean-run labels across all three faults. Even a small human audit is cheap and would close the main construct-validity gap: all 38 positives, all roots, and a stratified sample of about 100 negatives (especially artifacts that H or R4 suspend but the oracle calls clean).
- *Agreement statistics.* Report positive agreement (or Gwet's AC1) with CIs, separately for faulty-run and clean-run items.
- *Sensitivity analysis.* Line 970 promises one in which ambiguous labels count as contaminated. `recall_amb_c`/`precision_amb_c` are computed but never reported, and the one ambiguous label (a root, see the number checks) is ignored. Report it, including its effect on adoption (21 -> 22).

**M6. The statistical design does not match the data structure.**
- *(a) Clustering.* The 10 informative pairs are not independent units: 6 come from one model (qwen2.5-coder) and 3 models contribute none. A Wilcoxon test over runs treats model as noise. Report per-model results and add a model-stratified analysis (e.g. a paired permutation test stratified by model, or a mixed-effects model). Otherwise state that the population is "runs of 3 models, dominated by one".
- *(b) Holm family.* Holm is applied over 10 comparisons per metric, including H_noEME and H_noDeps, which are identical to H by construction (p = 1). Pre-specify the primary comparisons (H vs R1, R2, R3, R4, R0; HS vs H) and treat ablations descriptively.
- *(c) Paired test, unpaired effect size.* A12 is an unpaired measure reported next to a paired test. Use a paired effect size (e.g. the proportion of positive differences, or matched-pairs rank-biserial), or justify the mix.
- *(d) Mixed denominators.* Wilcoxon on 75 pairs with 65 zero differences (residual, line 1012) relies on a normal approximation, and the effective n is 10. Report the effective n.
- *(e) CIs.* Bootstrap percentile CIs with n = 10 and values at the bound (recall CI [1, 1]) are degenerate and appear nowhere in the paper. TSE readers expect CIs in the tables; use BCa or exact binomial/Wilson intervals for proportions, and put them in Table III.
- *(f) Power.* No power or minimum-detectable-effect statement accompanies the "not significant" findings. With n = 10, the test cannot detect F1 differences smaller than about 0.2.

**M7. Precision on runs with nothing to find.**
- *Code behaviour.* `process.py` computes "precision" over all runs where the suspension set is non-empty. Runs without contamination therefore enter as precision 0. The macros `LiveEHPrec` (0.04), `LiveERtwoPrec` (0.07) and similar are such quantities.
- *Paper status.* Table III uses the propagated-run variant, which is correct, and the all-run macros are not used in the text. Still, the summary JSON exposes them under the bare key `precision`.
- *Requested change.* Rename them (e.g. `precision_allruns_meaningless`) or drop them, so that no later edit of the paper picks them up.
- *Table III columns.* Table III mixes denominators: Susp. (all and propagated), P/R/F1 (propagated), residual and collateral (all), pass@1 and signature (all). Present one block per denominator, with n in each header.

**M8. Revalidation and the "best F1" claims.**
- *Timing of the HS design.* HS_judge and HS_embed were designed after the pilot showed closure's low precision (PROJECT_LOG: "Response: closure-bounded revalidation ... as a separately recorded supplement") and computed post hoc from recorded state (`supplement.json`).
- *Why that matters.* This is legitimate, but it must be disclosed as an extension designed after pilot observation, not as a pre-planned condition.
- *Overstated claims.* "highest F1 of all conditions" (line 1016) and "gave the best F1 in our study" (line 1147) rest on 0.67 vs R4 0.65. The two differ in a single run (the one where HS_judge suspends fewer clean items), with no test, and the oracle-tuned similarity reaches 0.69. Soften both statements and add HS vs R4 to the primary tests.
- *Dependence on the R4 judge.* HS_judge inherits R4's complete miss in one run, so it is not more complete than R4.

**M9. Replication entry points do not reproduce the reported campaign.**
- *Makefile and README.* The Makefile's `live`, `live-llama` and `live-results` targets point to the old local pilot campaigns (`live-qwen25-7b`, `live-llama31-8b`). Nothing processes `results/raw/live-fir`, and the README's "one-command reproduction for each subject" (line 1202) is therefore not true for S1.
- *Symlink.* `results/raw/live-fir` is a symlink into `results/raw/hpc/fir/...`; the archive must dereference it.
- *Version control.* `results/` is untracked, and record `environment.git` is the empty string, so `source_sha256` is the only code identity. Ship the source snapshot that hashes to it.
- *Prompts.* Document where the judge, R4 and reflection prompts live; they are stated to be "in the replication package".
- *Missing re-run instructions.* State how a third party re-runs one cell (the HPC scripts assume Alliance clusters), and give a local single-GPU path, with expected wall-clock time and the cache-only replay command.

**M10. Requirements for the pending curation slice (to avoid repeating the ExpeL issues).**
1. Report adoption and propagation per generator and per fault, as here.
2. Include the R0 reset baseline and |closure| / |evolved state|.
3. Show that H_noEME and H_noDeps differ from H. This is the slice's whole point, and the curation pilot found 20-28 of about 30 artifacts suspended, so the reset risk is real.
4. Re-tune, or at least report the F1-vs-tau curve.
5. Report seed-only vs clean pass@1, to establish whether curated state has value.
6. Fix the RQ1 answer box only after the slice is in. The box must not claim superior F1 for H unless the data show it.
7. Pool policies only with a policy-stratified analysis.

## Minor concerns

- L575: "driven by two open-weight LLMs" -> five generators (plus two judges and an embedding model).
- L920: "about 300 lines" -> the harness and its runner have about 1,500 lines.
- L933: "For each policy, generator and reporting seed ... \LiveTotalRuns{} runs in total" will read wrongly once LivePolicies = 2. Make sure the macro sums both slices.
- L948: define "LLM calls". The figure includes cache hits and excludes oracle and judge-phase calls; give generation, evaluation and oracle counts separately.
- L956: "All receive the same root (the faulty memory)" -> roots are 1-4 insights motivated by the corrupted batch (M4).
- L965: state that only 2/6 dev runs were informative, that tau_t is at the grid minimum, that ties break toward the smallest tau, and that the pilot used a single-root definition. Also, the dev F1 values 0.575/0.625 print as 0.57/0.62 because of float rounding; use 0.58/0.63 or three decimals.
- L970: the ambiguous-as-contaminated sensitivity analysis is promised but not reported.
- L972: say explicitly that S is restricted to non-root live revisions. The code intersects with `targets`.
- L975: precision is also computed only on propagated runs (Table III); say so. Report the bootstrap method (percentile), and include CIs in the tables.
- L983: "($D_1$'s context ...)" -> the evaluation alternates D1/D2 (15/14 tasks).
- L986 (Table II caption): "Live: non-root revisions" includes the two seed profiles, which ExpeL contexts never load. Report evolved revisions separately.
- L998: "no label was ambiguous" is false (one root label). "the 630 revisions of the clean runs" -> 210 revisions x 3 fault labels.
- L998: give the number of positive labels (38 unanimous YES) next to kappa.
- L1001 (Table III caption): Precision, Recall and F1 have n = 10; make n explicit per column block (M7).
- L1012: the residual test vs R1 is redundant with the test vs none (R1 = none on derivatives). Report the effective n = 10.
- L1014: "5.95 of about 8.0 live revisions" -> "of about 6.0 evolved revisions (all of them in 71/75 runs)". "because a low threshold is needed to catch paraphrases" contradicts the oracle-tuned bound (recall 1.0 at tau 0.5 and 0.8). "only F1 0.69" -> the highest F1 observed.
- L1016: "highest F1 of all conditions" excludes the oracle bound and is untested against R4 (0.67 vs 0.65, one run differs).
- L1018: good, but say "by construction" earlier, in the variants paragraph (L967), so readers do not expect a result.
- L1020: report seed-only pass@1 (0.63) and per-model propagated results. "pass@1 after H was the highest" ties with H_noEME and H_noDeps, and the comparison with none is not significant after Holm (p = 0.080).
- L1042 / L1045: explain why impact F1 is 0.103 at 0% edge capture (deployment membership or roots).
- L1059 / L1073: the 18 configurations are deterministic, so "agreement" is 18 single trials. Fine, but avoid CI language for these and for E-S BFS (30/30 is deterministic).
- L1078 / Table IV: E-S results depend on the wall-clock budget. PROJECT_LOG records 27 -> 26 and 1 -> 0 changes across reruns; mention that these counts are budget-nondeterministic.
- L1104: the ms timings are dominated by noise (H_noDeps 0.4 ms vs H_noEME 33.1 ms for the same set). Report medians over runs, or drop the decimals.
- L1125-1127: the 30 "seeded positions" on one running example are not 30 independent subjects, so Wilson CIs in summary.json overstate generality. The monitor's 182% replay time overhead (summary.json `conformance.time_overhead_percent`) is not reported; it belongs in RQ3.
- L1129 (RQ3 box): "tens of seconds" -> "about 20 s".
- L1132: "HumanEval+/MBPP+" -> HumanEval+ only.
- L1134: add that the pilot used a different root definition and harness version. Add that the R4 judge is also the generator, so its misses correlate with adoption.
- L1136: quantify cross-process nondeterminism (4.1% of identical-input items flip). It is directly relevant to the clean-reference comparisons.
- L1140: the "effective sample size" sentence should also mention clustering by model (6 of 10 informative runs from Qwen).
- L1147: "the judge missed every contaminated revision of one propagated run" is correct. "gave the best F1 in our study" needs the qualifier from M8.
- L1171: the paraphrase claim is contradicted in the ExpeL slice (M2).
- L1202: "one-command reproduction for each subject" is not currently true for S1 (M9).

## Recommendation

**Major revision.**

The engineering and the verification pipeline are of high quality, and every number I checked traces correctly to the logged data. The live evaluation, however, does not yet support the containment claims:
- In the only completed slice, HEARTNESS is a reset to the seed harness.
- The similarity baselines are tuned on 2 runs under a different root definition, and on the reported runs TF-IDF beats H at every threshold in the grid.
- The behavioural measure cannot detect collateral harm, because evolved state does not help.
- Several sentences contradict the data.

The pending curation slice is decisive. If it shows H suspending a strict, useful subset (with EME and dependency edges mattering) against a reset baseline and properly tuned detectors, and the issues above are fixed, the paper could become a strong TSE contribution.
