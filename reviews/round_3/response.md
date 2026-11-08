# Round 3 response

All three automated reviewers recommended major revision (scores: R1 N2/R2/Rel4/V4/P3;
R2 N3/R2/Rel4/V4/P3; R3 N3/R3/Rel4/V4/P3). This is internal automated review, not peer review.
Reviewer 2 checked 34 numbers against processed and raw data and found no numeric mismatch;
all mismatches were prose. Items marked *curate* are completed when the HumanEval+ x curation
slice (Fir run am-20261107-080855) is processed.

## Analysis changes (experiments/live/process.py, scripts/paper_macros.py)

| Request | Action |
|---|---|
| R1.1, R2.1 timestamp cut / rollback / reset baselines | Added post-hoc conditions T (rollback before fault), A (reset learned state), H_faulty (closure of oracle-contaminated roots only), computed from the recorded final state. Closure recomputation validated: equals logged H suspension in 75/75 ExpeL runs. Result: H == T in 75/75 runs, H < A in 4. Reported plainly. |
| R1.1 lemma | Proposition 1 (closure bounded by time cut) with proof, in Approach. |
| R2.2 thresholds tuned on 2 runs | Disclosed; full F1-vs-threshold curves reported (new Fig.); oracle bound reported as best F1, not "only". |
| R2.3, R1.3 behaviour | Reported seed-only pass@1 (0.63 > clean 0.61), per-run H vs none (5 higher, 5 lower), cross-process inference noise (29/609 items = 4.8%), within-process determinism (0/2,175). Pass@1 claims withdrawn; fault-signature rate reported as the sensitive signal (H lower in 6/10, never higher; not significant). |
| R2.4 roots | Roots described (1-4 per ExpeL run, mean 2.1); H_faulty sensitivity; results on adopted runs computed (summary "adopted"). |
| R2.5 ambiguity | One ambiguous root label reported; adoption 21 (22 with ambiguous). Clean-run labels stated as 210 revisions x 3 faults. |
| R2.6 statistics | Holm family restricted to 7 substantive comparators; ablations and post-hoc conditions descriptive; paired win/loss counts added; effective n stated per metric. |
| R2.7 precision | Precision, recall, F1 only over propagated runs; table columns relabelled with denominators. |
| R2.8 revalidation post hoc | Disclosed in Baselines and Threats. |
| R2.9 reproduction | `make live-fir` target; Data Availability updated. |

## Approach and formal changes

| Request | Action |
|---|---|
| R1.7 formal coverage | Proposition 2: P2/P8 inductive over all engine operators including EME (hand proof sketch). Writing it exposed a real gap: an experience could name a run loaded later, adding edges into accepted revisions. Engine now rejects such a Load (new test; 47 tests, mypy/ruff clean, 14/14 mutants killed). |
| R1.8, R3.3 revalidation unspecified | New Approach subsection + Algorithm 5 (fresh revision, attestation, history order, dependencies kept). |
| R3.5 walkthrough mismatches | Fixed: profiles not restored by withdrawal; k1 over-approximation example; 7-op witness matches the logged witness (accept m7, accept k1, withdraw m7; P2+P3); projection reduces contracts to dependency presence; Algorithm 2 split into Propose/Validate/Accept so the stale-base check can fail; rejection-by-closure explained (candidate included). |
| R3.7 notation | Event history renamed Lambda; Retire/Quarantine listed among operators; cost experiment renamed E-O. |
| R3.4 Table VIII | Projection column was a constant 2-identity control; removed; text corrected (independent topology capped from n=3). Scale timings regenerated from the final campaign (earlier macros were stale). |

## Presentation and positioning

| Request | Action |
|---|---|
| R3.1, R2 similarity claims | Intro and Related Work no longer claim similarity fails; they state when it works (verbatim repetition) and when it does not (paraphrase, behaviour). |
| R1.6, R3.6 related work | New subsection: taint/IFC (TaintDroid, CaMeL, FIDES), deletion propagation, machine unlearning, build-system invalidation, model registries, sagas (all bib entries web-verified; FIDES authors as "Costa et al."). Comparison table columns defined; EVOMAL/AgentSpec cells corrected; CaMeL/FIDES and build-systems rows added. "First measurement" softened relative to EVOMAL. |
| Mismatches (R2) | "two LLMs" (pending intro rewrite), D1-only evaluation, roots description, ~1,500 lines, MBPP+ removed, fault positions (tasks 2, 8, 9) disclosed. |
| R3 minor | Burgueno bib fixed; legends moved below plots; compute-platform paragraph shortened; HPC bug list removed from Lessons. |

## Not done / disagreed

- Locating roots from symptoms (R1.4): out of scope; stated that root identification is given to all remedies.
- Human annotation of the oracle (R2.5): not available; retained as main construct threat.
- Mechanized proof (R1.7): hand proof sketch only, stated as such.
- Anonymized artifact URL: cannot be minted here; package ships with the submission.

## Pending (curate)

Curation-slice table and model table; EME-only reach; closure vs T and A; revalidation; abstract,
intro results, RQ1 answer, conclusion; running-example check against a real curation run.
