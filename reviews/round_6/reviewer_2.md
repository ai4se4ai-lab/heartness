# Round 6 -- Reviewer 2 (empirical rigor and verifiability)

Paper: docs/TSE/main.tex and main.pdf (both 2026-11-07 14:58; the PDF is current, 23 pages, no undefined references). Line numbers refer to main.tex. My scratch scripts and outputs are in `/tmp/claude-1000/r6rev2/`; I reused the round-5 scripts in `/tmp/claude-1000/r5rev2/` unchanged.

## Summary

This round makes these changes:
- It adds positive judge agreement.
- It discloses H_EME-fail and the revalidation re-run as post hoc (Threats, introduction, Lessons, conclusion).
- It replaces the false "every detector had higher F1" claim and reports the H vs R3 F1 test.
- It counts HS_judge vs R4 differences from the data.
- It breaks the ExpeL noise down by learned state.
- It adds an adopted-runs sentence and the cross-policy adoption count (74) to the abstract.
- It drives the source line count from a macro.
- It aligns `supplement.py` with Algorithm 5.

**Verification.**
- **Raw data.** No file under `results/raw/` has changed since round 5.
- **Independent script.** My round-5 independent script (`indep5.py`, raw JSON only) produces byte-identical output on both campaigns. It still reproduces the logged H, H_noEME and H_noDeps sets in 75/75 runs per policy, and every row of Tables IV-VII. Run it with the project venv: the system SciPy chooses a different exact/normal Wilcoxon mode, which changes p-values but no paired count.
- **Pipeline.** I re-ran `experiments.live.process report` from a scratch directory. Both `live_runs.csv` files are byte-identical to the shipped ones. The two `live_summary.json` files differ only in the `campaign` path.
- **New script.** `r6.py` checks every new or changed number independently.
- **Supplements vs current code.** `supp_check.py` checks the current `experiments.live.supplement.restore` (after the alignment change) against the shipped supplements. It reproduces `restored` and `suspended` for all 150 ExpeL-style and 150 curation (run, screen) pairs. The code change therefore has no effect on the data, as the response states.
- **Tests.** `tests/test_revalidation.py` and `tests/test_eme.py` pass (16 tests, one new).

**Outcome.** Every new or changed number matches the data (table below). All four round-5 required changes were made in substance. What remains are three summary sentences that still say more than the data:
1. The RQ1 box says TF-IDF and the judge had "clearly higher F1 under both policies". The E-L text says that under the ExpeL-style policy none of those differences is significant.
2. The abstract and the RQ1 box count detector misses "folded into composed artifacts / skills and profiles" as 2 (R2) and 13 (R4) runs. The data give 1 and 12; the other runs are memory-only misses.
3. The setup paragraph (L2152) still says the revalidation conditions were added "before the reported campaign was analysed". This contradicts the correct disclosure in Threats (L2388).

## Scores

| Criterion | Score (1-5) | Justification |
|---|---|---|
| Novelty | 3 | Unchanged: the lifecycle formulation (withdrawal across deployments, EME, rollback conflict) is new and useful; the model checking is standard. |
| Rigor | 3 | Post-hoc status is now disclosed, positive agreement is reported, the unfavourable tests are all present, and revalidation equals Algorithm 5 (re-verified on 300 plans). Still limiting: no human validation of the LLM-judge oracle, which defines every recall number; an effective n of 10 under the ExpeL-style policy; no confidence intervals in the paper; and the H_EME-fail recall rests on one run whose outcome was known (now stated). |
| Relevance | 4 | Unchanged. |
| Verifiability and Transparency | 4 | Pipeline output is byte-identical, the supplements reproduce from current code, the stray directory is removed, and the superseded supplements ship. Deductions: `environment.git` is still empty, with a reason given (the `source_sha256` of the code tree substitutes), and `campaign` in `live_summary.json` still stores the command-line path. |
| Presentation | 3 | The body is well calibrated, and the E-L curation paragraphs are clear and honest. The RQ1 box and abstract, the most-read parts, still carry two overstatements (R1, R2 below), and the F1 sentence at L2252 is hard to parse. |

## Status of round-5 issues

| Round-5 issue | Status | Evidence / remaining gap |
|---|---|---|
| **N1** "every content detector had higher F1"; report H vs R3 F1 | **Addressed** | Abstract (L1680), RQ1 box (L2301), Lessons (L2401) and conclusion (L2463) now say "every detector was more precise". Verified: ExpeL precision H 0.335 vs R2 0.498, R3 0.386, R4 0.553; curation H 0.102 vs R2 0.235, R3 0.119, R4 0.784. L2252 reports R3 as comparable: 0.16 vs 0.18, H higher in 27, lower in 14, Holm p = 0.091 (reproduced). **New overstatement:** the RQ1 box says "clearly higher F1 under both policies". See R1. |
| **N2** H_EME-fail post hoc; revalidation re-run | **Mostly addressed** | Threats (L2388) now states that H_EME-fail was defined after the first analysis, when the EME-only run was known to have failed, and that its recall rests on that run. It also discloses the revalidation re-run and the kept superseded results. Introduction (L1705: "a variant we defined after seeing the data ... rests on that single run"), Lessons (L2399: "a post-hoc variant") and conclusion (L2465: "tested only post hoc") are appropriately hedged. **Leftovers:** the setup paragraph (L2152) still lists only T, A and H_faulty as post hoc. It still says the revalidation conditions were added "before the reported campaign was analysed", which contradicts L2388 (see R3). L2271, where the H_EME-fail result is reported, does not say "post hoc". |
| **N3** positive agreement; human audit | **Partly addressed** | Positive agreement is reported: ExpeL 0.99 (L2183), curation 0.89 (L2250). Verified independently: 38 both-YES / 1 disagreement of 1,384 items, giving 0.987; 143 / 35 of 4,500, giving 0.891. The human audit was declined again. The abstract still does not say that recall is measured against an LLM-judge oracle. I repeat the recommendation but do not make it a condition. |
| L2210 "context order" sentence | **Fixed** | L2221 now ends "within inference noise". |
| "HS_judge differs in a single run" | **Fixed** | L2217: "differs in 2 of the 10 propagated runs" (macro). Reproduced: 2/10 propagated, 12/75 overall. The curation count (11 of 42, macro `LiveCHSjudgeDiffersRfour`) is generated but unused, while L2273 says HS_judge "is essentially the judge" under curation. Its suspension sets differ from R4's in 11 of 42 propagated runs (31/75 overall), so cite the macro there. |
| RQ1-box precision sentence | **Fixed** | L2301: "What it suspends is bounded by the time cut: the same set under the ExpeL-style policy, slightly less under curation." Correct. |
| RQ1 box "as only rollback and reset did" | **Fixed** | Now "as did rollback, reset and the EME-fail variant". H_EME-fail has recall 1.00 in both tables. |
| "only where folded into larger artifacts" | **Partly fixed** | The introduction (L1705) now says "mainly where". The abstract (L1680), RQ1 box (L2301), Lessons (L2401) and conclusion (L2463) still attribute all misses to folding, with counts that include memory-only misses. See R2. |
| L2252 "only because that threshold is low" | **Not changed** | Still framed as a caveat. Minor; repeated below. |
| L2152 / post-hoc list | **Not fixed** | See R3. |
| CIs in the paper | **Declined** | L2160 states that CIs are package-only. I confirmed `lo`/`hi` in `live_summary.json`. Acceptable for TSE given the paired counts and Holm p reported in text, but a supplementary table would help readers. |
| Code: plan vs execution in `revalidate()` | **Resolved** | `revalidate()` now prunes `p.admitted` of members whose admission failed (`del p.admitted[key]`), so the returned plan reflects what was executed. A dependent whose dependency failed admission keeps the quarantined dependency and is rejected by admission. That is still correct. |
| Code: supplement restores only previously active members | **Fixed** | `supplement.py` L55 now re-admits every cleared admissible member. The current code reproduces all 300 shipped plans (`supp_check.py`). |
| Lessons noise 4.1% dominated by one prompt type | **Fixed in E-L** | L2221: 177 of 178 flips on prompts with no learned insight (reproduced; pipeline `flips_without_learned_state` = 177). Lessons (L2405) still says "up to 4.1%". That is acceptable because Threats (L2388) gives both rates. |
| Package: stray `results/processed/live/nonexistent/` | **Fixed** | Removed. |
| Package: `environment.git` empty | **Declined with reason** | Acceptable: `source_sha256` identifies the code. |
| Package: unused all-run precision macros (`LiveCHPrec` 0.06 etc.) | Not changed | Harmless. |

## Number check

Values are from my independent scripts on raw JSON unless marked "pipeline". "Prop." means propagated runs.

| # | Claim | Location | Paper | Mine | Match |
|---|---|---|---|---|---|
| 1 | Root adopted, both policies | L1680 | 74 of 150 | 21 + 53 = 74 | yes (see R4) |
| 2 | Spread beyond root | L1680 | 52 of 150 | 10 + 42 | yes |
| 3 | ExpeL judge items / raw / kappa / positive agreement | L2183 | 1,384 / 99.9% / 0.99 / 0.99 | 1,384 / 0.9993 / 0.987 / 0.987 (38 both-YES, 1 disagreement) | yes |
| 4 | Curation judge items / raw / kappa / positive agreement | L2250 | 4,500 / 99.2% / 0.89 / 0.89 | 4,500 / 0.9922 / 0.887 / 0.891 (143 / 35) | yes |
| 5 | HS_judge differs from R4 (ExpeL, prop.) | L2217 | 2 of 10 | 2 of 10 (12 of 75 overall) | yes |
| 6 | HS_judge differs from R4 (curation) | macro only | 11 | 11 of 42 prop. (31 of 75) | yes (unused in text) |
| 7 | ExpeL noise flips / pairs; flips without learned state | L2221 | 178 / 4,349; 177 | 178 / 4,349; 177 (pipeline and round-5 independent count) | yes |
| 8 | Curation noise | L2275, L2388 | 2 / 273 (0.7%) | 2 / 273 | yes |
| 9 | F1 H vs R3 (curation) | L2252 | 0.16 vs 0.18; H higher 27, lower 14; Holm p = 0.091 | 0.165 vs 0.180; 27 / 14 / 1 tie; Holm 0.0908 | yes |
| 10 | F1 H vs R2 / R4 (curation) | L2252 | 42 of 42; 36 lower, 6 higher; p < 0.001 | 42/42; 36/6; Holm 1.1e-7, 5.8e-7 | yes |
| 11 | Collateral H > R2 / R4 | L2252 | 73, 75 of 75 | 73, 75 | yes |
| 12 | "Every detector was more precise" (both policies) | L1680, L2301, L2401, L2463 | yes | ExpeL H 0.335 < R3 0.386 < R2 0.498 < R4 0.553; curation H 0.102 < R3 0.119 < R2 0.235 < R4 0.784 (R4 undefined in 5 runs where it suspends nothing) | yes |
| 13 | "TF-IDF and the LLM judge had clearly higher F1 under both policies" | L2301 (abstract L1680 without "both policies") | clearly, both | Curation: yes (42/42, 36/6, p < 0.001). ExpeL: 0.60 / 0.65 vs 0.48, but H lower in 6 and 7 runs, higher in 2 and 2, Holm p = 0.352 / 0.273; L2215 itself says "none of these differences is significant" | **mismatch (wording)** |
| 14 | Adopted-runs sentence: H / T / R4 susp. per run in the 53 adopted runs | L2269 | 21.19 / 22.49 / 2.70 | 21.189 / 22.491 / 2.698 | yes |
| 15 | Detector misses "folded into skills and profiles" (R3 / R4 / R2) | L2301; abstract "composed artifacts in 2 to 22" (L1680) | 22 / 13 / 2 | runs with a missed skill or profile: 22 / 12 / 1. R4 has 13 miss runs, 1 memory-only; R2 has 2 miss runs, 1 memory-only | **mismatch** |
| 16 | `src/heartness` line count | L2101 | 1,161 | 1,161 physical lines (993 non-blank, non-comment) | yes |
| 17 | `experiments/live` line count | L2103 | 1,749 | 1,749 | yes |
| 18 | Precision of H below every detector, narrowly for R3 | L2269 | 0.10 | 0.102 vs 0.119 / 0.235 / 0.784 | yes |
| 19 | H_EME-fail susp. / F1 / recall | L2271, L2399 | 17.24 / 0.22 / 1.00 | 17.24 / 0.220 / 1.0 | yes |
| 20 | Tables IV-VII, all rows | L2186-2245 | -- | `indep5.py` output byte-identical to round 5; pipeline CSV byte-identical | yes |
| 21 | Revalidation plans (current code vs shipped) | L2273, response | no data change | 150/150 ExpeL, 150/150 curation | yes |
| 22 | All round-5 numbers #1-#58 (unchanged) | -- | -- | unchanged inputs, identical script output | yes |

Summary: 20 of 22 rows match. The two mismatches (#13, #15) are wording or counting in summary sentences, not errors in the data or tables.

## Remaining issues

**R1. "Clearly higher F1 under both policies" (RQ1 box, L2301; abstract L1680).**
- Under the ExpeL-style policy the F1 gap is not significant: Holm p = 0.352 for R2 and 0.273 for R4, with H better in 2 of 10 runs for each.
- L2215 says so itself ("none of these differences is significant ... low power").
- *Required.* Write "had higher F1, clearly under curation and by a non-significant margin under the ExpeL-style policy", or drop "clearly" and "under both policies". In the abstract, "clearly" is acceptable only if it is tied to curation.

**R2. Miss counts attributed to folding (abstract L1680, RQ1 box L2301, Lessons L2401, conclusion L2463).**
- The RQ1 box says the detectors "missed contamination folded into skills and profiles (R3: 22, R4: 13, R2: 2 of 42 runs)". The abstract says "folded into composed artifacts in 2 to 22 of 42 runs".
- The counts are runs with any miss. Runs with a missed skill or profile number 22, 12 and 1. R4 has one run, and R2 one of its two, where the only missed revision is a memory; R4 misses 2 memories in total.
- The abstract also omits that the "of 42" counts are curation-only. Under the ExpeL-style policy R4 missed one flat insight run, and no detector missed anything else.
- *Required.* Either use the composed-only counts (1 to 22), or keep the counts and write "missed contamination, mostly folded into composed artifacts, in 2 to 22 of 42 curation runs". Apply the same "mostly" in L2401 and L2463, matching the introduction's "mainly where" (L1705).

**R3. Setup paragraph contradicts Threats on what is post hoc (L2152 vs L2388).**
- L2152: "The revalidation conditions and T, A and H_faulty were added after the local pilot, before the reported campaign was analysed."
- But the revalidation semantics (the dependency rule) were re-applied after the analysis and a review. H_EME-fail is also post hoc and is not introduced in this "Variants" paragraph at all; it first appears in a table caption.
- *Required.* Define H_EME-fail at L2152 and mark it post hoc there. Change the sentence to match L2388. Add "(post hoc)" where its result is reported (L2271).

**R4. Abstract adoption vs spread (L1680), minor.**
- "Adopted in 74 and spread beyond its root in 52" reads as if the 52 are a subset of the 74.
- Three of the 42 curation propagated runs have a root that the judges disagreed on (the H_faulty misses, L2269). They are among the 81 runs counting ambiguous roots, not among the 74.
- Suggest "adopted in 74 (81 counting ambiguous root labels)", or just note the three.

**R5. Minor.**
- L2252: the F1 sentence is hard to parse: "TF-IDF and the LLM judge had higher F1 than H (the embedding detector was comparable: ...), R2 in all 42 propagated runs (...) and R4 in 36 of them (6 lower; ...)". Split it into two sentences and say explicitly whose F1 was "lower" in the 6 runs (H's was higher).
- L2252: "kept recall high ... only because that threshold is low and suspends 11.27 revisions per run" (unchanged from round 5). This is 54% of H's 20.79 suspensions at recall 0.99 vs 1.00, which is a result in favour of the frozen TF-IDF. State it neutrally.
- L2273: "under curation it is essentially the judge". Its suspension set differs from R4's in 11 of 42 propagated runs; use the existing macro.
- L2252: collateral H vs R3 (H more in 41 runs, less in 31, Holm p = 0.048) is the one collateral test not reported. Add it for completeness; it is the comparison least favourable to the detectors.
- Abstract: say that contamination labels come from an LLM-judge oracle (no human audit). This is carried over from round 5.
- L2101: "1,161 lines" counts blank and comment lines (993 without them). Say "physical lines" or leave as is; it is reproducible either way.

## Recommendation

**Minor revision.**

All four required changes from round 5 were made in substance, and I verified each against files rather than the response:
- The F1 claim is corrected and the R3 test reported.
- H_EME-fail and the revalidation re-run are disclosed as post hoc in Threats and hedged in the summaries.
- The three leftover sentences are fixed.
- Positive agreement is reported and reproduced (0.99 / 0.89).

The data, tables, pipeline and supplements reproduce exactly from raw records and current code. Every new number I checked matches. Required before acceptance, all prose:
1. Tie "clearly higher F1" to curation in the RQ1 box (and the abstract), consistent with L2215 (R1).
2. Correct the "folded into skills and profiles / composed artifacts" counts or add "mostly", in the abstract, RQ1 box, Lessons and conclusion (R2).
3. Align the setup paragraph L2152 with Threats L2388 on what is post hoc, and introduce H_EME-fail there (R3).

A human audit of the oracle positives remains strongly recommended but is not a condition.
