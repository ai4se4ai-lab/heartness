# Reviewer 1 — Formal methods and methodology, round 2

This is an automated artifact review, not actual IEEE TSE peer review.

## Summary

I reviewed the revised finite and engine semantics, mapped-state experiment, monitor, scope statement, manuscript, round-1 response, relevant processed/raw results, and regression tests. Both prior major concerns are resolved at the bounded-evidence level requested. The deployment update now replaces membership in Python and Promela; reference correspondence is checked against an explicit mapping rather than inferred from safety verdicts. The manuscript retains the essential qualification that this evidence is not an implementation-refinement proof. I found no remaining major formal-methods concern within the stated feasibility scope.

## Scores (1–5)

| Criterion | Score | Justification |
|---|---:|---|
| Novelty | 3 | The contribution remains a useful integration of established provenance, guarded lifecycle, finite checking and monitoring techniques; novelty is appropriately calibrated. |
| Rigor | 4 | The demonstrated transition mismatch is repaired, the exact regression is retained, and E15 supplies bounded mapped-state checks. Projection restrictions, stutters and the shared monitor/controller trusted base are stated. |
| Relevance | 4 | Withdrawal of inherited persistent state, compatible rollback and explicit observation limits address concrete maintenance obligations. |
| Verifiability and Transparency | 4 | The state mapper, translator, source snapshots, processed-to-raw links and completion-recovery provenance make the revised claims inspectable. Coverage remains deliberately small and does not imply unbounded correctness. |
| Presentation | 4 | The revised correspondence account distinguishes verdict agreement, witness replay, mapped-state agreement and proof. Remaining suggestions are clarifications rather than correctness repairs. |

## Resolution of prior concerns

1. **R1 major 1 — resolved.** `checker.py:81–92` now models replacement Deploy, including an empty active set, and preserves version changes for repeated Withdraw and same-active-set Rollback. Promela uses `a!=d` followed by `d=a`. `tests/test_correspondence.py:12–23` exercises the exact two-identity rollback/redeployment trace from my report and compares mapped states after every step. The final engine deployment contains only a0.
2. **R1 major 2 — resolved within requested bounded scope.** `experiments/correspondence.py:30–41` specifies the state mapping. Lines 44–78 compare enabled operations and mapped results for every successor of discovered small reference states, recognizing unchanged projected states as stutters. The processed E15 results contain 708 attempted transitions for chain and 2,292 for independent topology, with zero mismatches (3,000 total). The campaign checks 131 and 446 discovered states respectively, using n=2 and depth=6. The manuscript at main.tex:509–522 states both the mapping and its limits, and explicitly describes the P4 translator's administrative failed-validation event.
3. **Observation coverage — resolved.** `observation_summary` reports supplied/missing observations and distinguishes event admissibility from state observation; the manuscript explains this at main.tex:382.
4. **Transition audit invocation — resolved.** `monitor.py:25,34` preserves the prior state and passes it to the P5/P7 audits.
5. **Numeric scope and validation types — resolved for the reported issue.** Unsupported mask/counter scopes are rejected; Validate requires an actual Boolean, while version/base stamps require integers. `tests/test_inputs.py` includes string/number validation-result rejection and invalid checker scopes.
6. **Rollback scope disclosure — resolved.** `formal/SCOPE.md` now explains the first-n-snapshot action restriction and explicitly says later targets are omitted.

The revised E05 results retain 18/18 Python/SPIN verdict agreements and 13 replayed mutant witnesses. The latest main campaign manifest records 1,905 records. Its `completion_provenance.json` identifies a finalizer-only name-shadowing failure and recovery by exclusive metadata creation after measurements. This is transparently documented; I found no basis in the inspected evidence to characterize the finalizer repair as changed measurements.

## Major concerns

None within the manuscript's explicitly bounded lifecycle-feasibility claims.

## Minor issues / optional clarifications

1. **Clarify E15's merged-history boundary in the paper.** The raw scope and `compare_reference` correctly state that one shortest engine history is retained per projected state. Add that exact qualification to the E15 paragraph. Histories differing only in excluded ledger fields or projection stutters are not independently enumerated. This is a limit of the mapping experiment, not a demonstrated unsoundness or a request for an unbounded proof.
2. **Make attempted versus enabled counts explicit when emphasizing E15.** The 3,000 count is attempted action applications, including rejected actions and projection stutters; enabled counts are 215 and 777. The paper already calls the total “attempted,” correctly. A compact parenthetical with enabled/stutter counts would help readers assess coverage. The depth-six experiment does not itself exercise the full ten-operation rollback/redeployment path; the separate exact regression appropriately covers that path.

## Questions for the authors

No blocking questions. For future extensions, how will the state relation change when introducing independent dependency versus derivation topology, multiple deployment identities, dynamic synthesis, or explicit quarantine operations? These are documented exclusions and need not be implemented for this revision.

## Verification performed

I ran `.venv/bin/pytest -q tests/test_correspondence.py tests/test_inputs.py tests/test_checker.py tests/test_capture.py`: **14 passed in 5.22 seconds**. This includes actual Python/SPIN checker tests and the exact deployment regression. I inspected E15 processed/raw references and completion metadata; I did not independently rerun the entire 1,905-record campaign.

## Recommendation

**Minor revision**, limited to the two exposition clarifications above. No major concern remains. The absence of an unbounded proof, real-agent efficacy evidence, authenticated observations, and production deployment semantics is expressly acknowledged and should remain a scope limitation rather than be represented as an unresolved implementation defect.
