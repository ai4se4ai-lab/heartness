# Round 8 -- Reviewer 3 (presentation, clarity, relevance)

This is an internal, automated review of a draft, not independent peer review. Scores run from 1 (poor) to 5 (excellent). Line numbers refer to `docs/TSE/main.tex` as of this round (2,535 lines; `\begin{document}` at l.1701). Page numbers refer to `docs/TSE/main.pdf`, which has the same timestamp as the .tex (24 pages; Conclusion and Table XII on p.22). I read the abstract, introduction, Sections III-D to III-F, the E-L results including Table VIII, the RQ1 box, Lessons and the Conclusion in the source, and checked the rendering of Algorithm 5 and Table VIII in the PDF text (p.7 and p.14). I checked `src/heartness/revalidation.py` and its callers, ran `tests/test_revalidation.py` (10 passed) and collected the full suite (59 tests). I edited no file other than this review.

## Summary

Heartness is a controller for self-evolving agent harnesses. Its parts are immutable revisions, host-recorded exposure including experience-mediated exposure (EME), guarded admission, closure-based withdrawal of revisions or experiences across deployments with rollback admissibility, closure-bounded revalidation under an attestation, bounded model checking with two encodings and witness replay, and a conformance monitor. The live study is unchanged: 200 runs, five generators, two policies. The structural selectivity analysis added in round 7 (Table VIII) is now reported with both post-composition blocks and a horizon caveat.

This round was a clean-up round, and the clean-up is good. The P2 line reference is now a `\label`/`\ref`. "Affected set" has one meaning across Definition 5 and Algorithms 4-5. The abstract sentence reads correctly. The selectivity result is reported as 0.46-0.61 in the main places, with an explicit window/horizon explanation. `active_before` is a required parameter. What remains is small:
1. Two summary places (the RQ1 box and the Conclusion) still state the selectivity result without the window qualifier that the body now gives.
2. The validation macros in the paper are stale relative to the shipped results files (54 tests vs 59).
3. A few leftover naming slips in code comments and one clause about what Withdraw returns.

## Scores

| Criterion | Score | Justification |
|---|---:|---|
| (i) Novelty | 3/5 | Unchanged. The contribution is the integration (run contexts as inputs so that EME enters admission and withdrawal; deployment-wide suspension with admissible rollback; closure-bounded revalidation) and a two-policy measurement of non-adversarial fault spread. The one place where closure would be clearly *better* than the obvious baseline (a rollback) is shown only by structural reanalysis, not by an observed containment. |
| (ii) Rigor | 4/5 | The two round-7 inconsistencies in Section III are fixed. Algorithm 5 l.1 (l.2065) now *is* Definition 5's affected set before withdrawal, and Algorithm 4 uses Z for the full closure (l.2028). Code and paper agree on candidate selection and the frontier. Remaining small gaps: the RQ1 box and Conclusion overstate selectivity slightly; Alg. 5 l.3's "admissible" is still undefined. |
| (iii) Relevance | 4/5 | Good and unchanged. Software-engineering framing (change impact, traceability, rollback for self-modifying software). The Lessons paragraph (l.2459) now gives designers the correct lever: what a composition broadcasts and when, not merely "use retrieval". No maintainer or practitioner study. |
| (iv) Verifiability and Transparency | 4/5 | Strong macro discipline, selectivity reproducible, post-hoc decisions disclosed (l.2448 now also discloses the revised selectivity definition). Held at 4 because the validation macros are stale against the shipped `results/validation/*.json` (see Remaining issue 2) and because no anonymized artifact link is given (l.2528). |
| (v) Presentation | 4/5 | Required fixes made and rendered correctly. The paper is still 24 pages; six paragraphs exceed 300 words (l.2059 346, l.2292 320, l.2309 369, l.2311 312, l.2448 423, l.2490 406), and the internal-validity paragraph *grew*. Several third- and fourth-round minors remain (Fig. 1 label ⑩, Table II, Table XII `\resizebox`, transitive "exposed to"). None of these blocks understanding. |

**Overall recommendation: minor revision (accept once the three small required items below are done).**

## Status of round-7 issues

| Round-7 item | Status | Evidence |
|---|---|---|
| **M1.1** "Line 12" in §III-D | **Resolved** | `\label{line:p2}` on Alg. 2's P2 line (l.1992); both references use `\ref` (l.1999, l.2001). The PDF (p.6) reads "Line 10 recomputes a closure", which is correct. |
| **M1.2** "affected set" means two things | **Resolved** | Definition 5 (l.1800) is unchanged. Algorithm 4 now names the full closure Z (l.2029-2032). Algorithm 5's Require no longer defines A. Its l.1 (l.2065) is {x ∈ Cl(R) \ R \| x ∈ Act_b ∪ ⋃Dpl_b, φ = clean}, which is Definition 5's affected set before withdrawal minus the roots. The prose states this explicitly (l.2059: "Candidates are the members of the affected set (Definition 5) before the withdrawal"). *Residual (minor):* Fig. 1 ⑦ (l.1901, caption l.1910) says the operator receives "the affected set", while Alg. 4 l.6 returns Z. Definition 6 says withdrawal "suspends its affected set", while Alg. 4 quarantines all of Z \ R. Both are equivalent on Act and Dpl, but one clause after Alg. 4 ("Z ∩ (Act ∪ ⋃Dpl) is the affected set of Definition 5; the operator is shown that set") would close it. |
| **M2** selectivity quoted from its best cell | **Resolved in the body; partly in the summaries** | Intro (l.1743) and Lessons (l.2459) give 0.46-0.61 with "until the next (broadcast) composition". E-L (l.2311) gives both rows, explains why 19-24 is higher, states "both profiles composed at task 24 were in the closure of every such root" and "the low ratios therefore partly reflect the 24-task horizon". This is exactly what I asked for. *Not carried through:* the RQ1 box (l.2361) says "markedly more selective than a time cut only for curation roots after the first composition". The Conclusion (l.2523) says "it becomes markedly more selective only for later faults in a retrieval-based harness". The last sentence of l.2311 says "markedly more selective for later faults under retrieval". None of these three carries the window qualifier, and these are the sentences a skimming reader takes away. See Remaining issue 1. |
| **M2** table: 1-root cell | **Resolved** | Caption (l.2314): "The ExpeL-style 1–6 row rests on a single root." |
| **M2** table: "Strict" header | **Resolved** | Renamed "Smaller", and the caption defines it. |
| **M2** table: final-active roots only | **Resolved** | Caption: "roots are the revisions still active at the end of a run (insights edited or removed earlier are not roots)". |
| **M2** table: mean of per-root ratios | **Acceptable** | "mean share … over every final active revision r" makes the averaging unit clear. No pooled ratio was added; optional. |
| **M3** abstract sentence | **Resolved** | l.1718: "Like a rollback to before the fault, withdrawal suspended every contaminated derivative, and deleting the root removed none; but for these early faults withdrawal also suspended almost as much as the rollback." Rollback is named as the comparator, the subject is unambiguous, and "for these early faults" is a good qualifier. The related minor ("found one corrupted feedback message in the lesson it created") is not done; the sentence still says the oracle found the *message* in the lesson rather than the practice it planted. |
| Code: `active_before` default | **Resolved** | `revalidate(..., deployments_before, active_before)` has no default (`revalidation.py:62-63`). All 10 call sites in `tests/test_revalidation.py` pass it. `supplement.py:55` uses `h["active"]` together with the deployments, as before. *Residual (minor):* the response says "active frontier" was renamed "clean frontier" in the code. The docstring was renamed (l.15), but the function is still `active_frontier` (l.122) and the inline comment at l.92-93 still says "ACTIVE FRONTIER: the nearest clean, active ancestors". That contradicts both the docstring and the paper (l.2059: "active or not"). The module docstring (l.3) still calls the quarantined set "the affected set A". |
| **M3 (round 7)** length and density | **Not done (declined)** | Still 24 pages. l.2448 grew from 378 to 423 words. l.2059 grew from 334 to 346 words. The response cites TSE's lack of a page limit, which I accept as the authors' call. I keep it as a strong recommendation, not a condition. |
| "Precision tells the other half" | **Resolved** | l.2292: "On F1 and collateral the comparison reverses." |
| Transitive "exposed to" (Def. 4) | Not done | l.1793 still defines only "directly exposed"; the transitive form is used at l.1804, l.2044 and l.2054. |
| Letter clashes (D in Alg. 5, T in Alg. 1, C/A metric sets) | Partly | A is gone from Algorithms 4/5. D (Alg. 5 l.5) still clashes with the deployment domain of Definition 5. |
| Alg. 1 run r not introduced | Not done | l.1956 `Load(r, C)`. |
| Alg. 5 l.3 "admissible" undefined | Not done | Still "if some x ∈ C is admissible" (l.2067). |
| Fig. 1 ⑩ label | Not done | l.1897 still `sloped`. |
| Table II justified column | Not done | No `\raggedright` in the file. |
| l.2331 "(indices of that run)" | Not done | m₈/m₉ still clash with the running example's m₇/m₈. |
| "3.30 of them clean" in no table | Not done | |
| E-C has no objective | Not done | |
| Table XII `\resizebox`; anonymized link | Not done (acknowledged) | |

## Remaining issues

### Required (all cheap)

1. **Carry the window qualifier into the summary sentences.** Edit l.2311 (last sentence), the RQ1 box (l.2361) and the Conclusion (l.2523) to match the body. For example: "…markedly more selective for roots created after the first composition, *until the next broadcast composition*, a position our planted faults did not cover." Right now the body says the effect is a window effect partly produced by the 24-task horizon, while the three summary sentences present it as a property of "later faults in a retrieval-based harness".

2. **Regenerate the macros.** `results/validation/tests.json` (19:18) reports 59 passed tests; `\TestCount` in main.tex (l.39) is 54. `results/validation/coverage.json` gives 98.4% statements and 94.9% branches; `\LineCoverage`/`\BranchCoverage` (l.37-38) are 98.6 and 95.4. `paper_macro_index.json` is dated 19:10, before the last validation run. The paper claims that every number is generated from the results files, so run `make macros` (and check that no other macro moved) before submission.

3. **Make the code comments match the paper.** Rename `active_frontier` to `clean_frontier` (or fix the comment at `revalidation.py:92-93`, which says "active ancestors"), as the response states was done. Add one clause after Algorithm 4 saying that Z ∩ (Act ∪ ⋃Dpl) is Definition 5's affected set and is what the operator is shown (Fig. 1 ⑦).

### Strongly recommended (not conditions)

- Split the four longest paragraphs (l.2448 into design/inference threats; l.2490 by topic; l.2309 after "…which runs count as exposure"; l.2059 into candidates/attestation, copy lineage, deployment/P2). This costs nothing and fixes the main readability problem in Sections III-F and IV.
- Define transitive "exposed to" in Definition 4 (one clause). Define "admissible" in Alg. 5 l.3 as "passes the dependency check of l.6".
- Set Fig. 1's ⑩ label horizontally, `\raggedright` in Table II, and add "(indices of that run)" at l.2331.
- Abstract: "found the practice planted by one corrupted feedback message in the lesson it created".

### What would raise Novelty from 3 to 4 (minimal, concrete)

The paper's distinctive claim over "roll back to before the fault" is selectivity plus enforcement. In the live data, both are shown only indirectly: selectivity by an oracle-free reanalysis, and enforcement (refused re-admission or rollback) only in controlled scenarios (l.2525, "Second"). Either of the following would earn a 4 from me:

- **(a)** One additional curation campaign slice with the fault planted *after* the first composition (for example at task 14-16), on even two or three generators with the existing seeds. Report recall, collateral and |Cl| / |T| against the oracle. This turns Table VIII's 0.46-0.61 from a structural prediction into an observed, oracle-scored containment that is strictly cheaper than rollback. It would also show what the window looks like across the task-24 composition (or extend the stream past it).
- **(b)** A live mid-evolution withdrawal: withdraw the root at the moment it is detected, let evolution continue, and count how often the policy would re-derive from the tainted experience or re-merge a quarantined member, i.e. how often P2 enforcement *fired* on live, non-adversarial generation.

Either is a bounded experiment that reuses the existing pipeline. Without one, the paper is a well-engineered and honestly evaluated integration, which I rate 3 on novelty.

Rigor, Relevance, Verifiability and Presentation are at 4. I see no criterion below 4 other than Novelty.

## Recommendation

**Minor revision; accept once the three required items are done.**

The authors fixed every required round-7 item correctly:
- the line reference now uses `\ref`;
- "affected set" is consistent;
- the selectivity result shows both cells with a horizon explanation in the body;
- the abstract sentence is correct;
- `active_before` is required.

For a TSE audience, the paper offers a clear SE framing, a sound and checked controller, and an unusually candid evaluation that says where its own approach is no better than rollback and why. What remains:
1. Three summary sentences that are a little stronger than the body.
2. Stale validation macros.
3. Comment-level naming in `revalidation.py`.

None of these needs new experiments. Splitting the long paragraphs is recommended but not required.
