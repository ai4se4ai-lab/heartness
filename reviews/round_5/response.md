# Round 5 response

Reviewers: R1 minor (N3/R3/Rel4/V4/P4); R2 minor (N3/R3/Rel4/V4/P3); R3 minor (N3/R4/Rel4/V4/P4).
Internal automated review, not peer review.

## Code

| Request | Action |
|---|---|
| R1.M2 re-admitted copies lose clean lineage | `revalidate()` now keeps every part of x's lineage that is not withdrawn: active sources, re-admitted sources mapped to their copies, experiences whose run context avoided Cl(F); the attestation replaces only the withdrawn part. New test reproduces the reviewer's scenario (withdraw m7, revalidate k1, withdraw m6 -> k1~r suspended). |
| R3.2 Algorithm 5 vs code | `revalidate()` takes a root set, screens only the affected set A \ R, and the attestation records roots, screen and the full cleared set. Copies do not carry `replaces` (they are new revisions); stated. |
| R2 minor: supplement restores only previously active members | Now restores every cleared admissible member, as Algorithm 5 does (no data change: 1,820/1,820 were active). |
| R2 positive agreement | Added (ExpeL 0.99, curation 0.89) to process.py and the paper. |
| R2 noise composition | `flips_without_learned_state`: 177 of 178 ExpeL flips are on prompts with no learned insight; reported. |
| R2 HS_judge vs R4 | Counted from data (2 of 10 ExpeL propagated runs; 11 of 42 curation); text uses the macro. |
| R2 stray directory | `results/processed/live/nonexistent/` removed. |

## Paper

| Request | Action |
|---|---|
| R1.M1/R2.1/R3.1 false "every detector higher F1" | Abstract, E-L, RQ1 box: every detector more precise; TF-IDF and judge clearly higher F1; embedding comparable, with the H vs R3 F1 test reported. |
| R1.M3 late-fault prediction | Corrected: faults after task 12 were not sampled; later tasks would be exposed only through memory retrieval until task 24, so the gap could be larger. |
| R1 "evidenced in RQ2" | Reworded: re-admission and unsafe rollback in RQ2; re-derivation from a withdrawn experience by unit tests only; none exercised live. |
| R1/R3 notation | Forbidden roots F = W ∪ K ∪ {b : expr(b) ∩ Θ ≠ ∅} defined in the metamodel; Table II, Algorithms 2 and 4 use Cl(F); Algorithm 4 has the experience branch; tainted set renamed Θ (no clash with T); effects renamed X (no clash with F); Θ, F in Table I. |
| R1/R3 exposure direction | Definition 4 now reads "b is directly exposed to x, written x ⇝ b", consistent with all later uses; example sentence and Table I fixed. |
| R2.2 H_EME-fail post hoc; revalidation re-run | Stated in Threats, intro, Lessons and conclusion (recall rests on one failed run). Revalidation re-run with the dependency rule disclosed; superseded results kept. |
| R2.3 / R3.4 leftovers | "context order" sentence removed; RQ1 box "suspends slightly less" (not precision); H_local "ineffective by construction"; running example task 9 / run r8 with k0 in context; RQ1 box includes the EME-fail variant among recall-1.00 conditions. |
| R2.4 "only where folded" | "mainly where". |
| R1 abstract adoption | 74 of 150 adopted, in the abstract (244 words). |
| R1 load precondition | In Section III-C running example and in the proofs of Propositions 1 and 2. |
| R1 adopted-run macros | Used in one sentence (curation closure vs time cut). |
| R1 src line count | From a macro (1,1xx lines). |
| R3 minors | τ_t on the grid boundary stated; Fig. 4 caption reworded (50–75%). |

## Not done

- Human oracle audit and anonymized artifact link (as before).
- Confidence intervals remain in the package (per-run values and bootstrap CIs); the paper reports means and paired counts.
- `environment.git` is empty in the records because the cluster copy is not a git checkout; every record carries `source_sha256` of the code tree instead.
- R3 length suggestions partly applied; the compute-platform paragraph is kept at the author's request.
- R3 "line 12" in Algorithm 2: line numbering counts procedure-end lines; line 12 is the P2 check, so the reference is correct.
