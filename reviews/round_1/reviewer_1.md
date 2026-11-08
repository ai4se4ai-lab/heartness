# Reviewer 1 — Formal methods and methodology

This is an automated artifact review, not actual IEEE TSE peer review.

## Summary

HEARTNESS integrates immutable revision identities, recorded derivation/use closure, guarded acceptance, local rollback, registered deployment containment, and event replay. I inspected the manuscript, all six requested core modules, `formal/SCOPE.md`, checker tests, the implementation witness translator, and the processed campaign summary. The manuscript appropriately disclaims unbounded verification, provenance completeness, causal attribution, and production correspondence. Its disclosure of a previously shared abstraction error is particularly useful. Nevertheless, a remaining reference transition mismatch shows that agreement of safety verdicts and replay of selected mutant witnesses is too weak to support the current correspondence evidence without further repair.

## Scores (1–5)

| Criterion | Score | Justification |
|---|---:|---|
| Novelty | 3 | The operational integration and rollback/revocation choice are useful; graph reachability, finite contracts, and replay are established techniques, as the manuscript itself acknowledges (main.tex:99, 110, 116–120). |
| Rigor | 3 | Guards and immutable source identity make the core protocol understandable. Explicit projection exclusions are unusually clear. State-level agreement with the engine is not checked, and the Deploy semantics still differ. |
| Relevance | 4 | Persistent harness withdrawal, derivative containment, and preservation of external-effect records are significant maintenance problems. |
| Verifiability and Transparency | 4 | Sources, finite scopes, retained witnesses, cap reporting, negative controls, and raw evidence are available. The summary reports 18/18 verdict agreements and 13 implementation replays, but neither is a transition-relation equivalence check. |
| Presentation | 4 | Scope distinctions and the example are clear. Some implementation preconditions, observation completeness, and checker domain restrictions need a more explicit account. |

## Major concerns

1. **Deployment update semantics still disagree between the reference engine and both finite encodings.** `engine.py:159–164` replaces membership for a deployment with the requested/current active set. `checker.py:83–84` instead accumulates `s.deployed | s.active`, and additionally enables Deploy only if an active identity has not already been deployed. Generated Promela repeats these choices at `checker.py:189`. This is not explained by the advertised restriction to one deployment. A concrete reference trace on two independent identities is: propose/validate/accept a0; deploy; propose/validate/accept a1; deploy; rollback to snapshot 1; deploy. The engine's final deployment is `{a0}`; the projection cannot execute the final deployment because a0 is already in its deployed mask, and leaves `{a0,a1}`. Both models can remain safety-safe, so an 18/18 Boolean verdict comparison cannot expose this error. **Required action:** implement matching replacement semantics in both finite encodings, or explicitly define and justify an overapproximation relation that covers this behavior. Add a regression for this trace. Add bounded reference correspondence checks comparing enabled operations and mapped state fields, rather than only fault verdicts. Re-run affected model-checking, replay, and state-space campaigns, and update all manuscript tables. This is directly relevant to the earlier correspondence-error discussion at main.tex:484.

2. **The implementation replay evidence is too narrowly sampled to assess the correspondence gap it is used to discuss.** `experiments/run.py:116–149` translates only the shortest mutant witnesses selected by the campaign, and records only engine violations/rejection, with no comparison against the projected post-state after each step. The P4 translator also inserts an extra failed Validate event (lines 133–135), so the translation is not uniformly one projected operation to one engine event. These choices are reasonable engineering devices, but the reported 13/13 success is conditional fault-witness executability, not representative reference-model conformance. The newly identified Deploy mismatch illustrates the practical consequence. **Required action:** document an explicit state mapping and event translation (including the P4 administrative step), test reference traces as well as mutant traces, compare mapped states after every translated operation, and report the number of transitions/traces checked and any mismatches. An exhaustive small-scope transition correspondence experiment is sufficient; an unbounded refinement proof is not requested. Keep the paper's existing distinction between bounded evidence and proof.

## Minor issues

- `monitor.py:25–33` returns an empty findings list when all events lack observations. `main.tex:375` correctly calls missing observations an evidence gap, but the CLI (`cli.py:53–54`) reports only deviations and does not expose observation coverage. Include supplied/missing observation counts or an explicit observation-completeness status so absence of deviations cannot silently stand in for observed-state agreement.
- The monitor calls `violations(engine)` without the preceding state (`monitor.py:32`), so the transition checks for P7 history-prefix preservation and P5 effect retention (`properties.py:48–54`) are not exercised there. Pass a previous-state snapshot or explicitly limit the monitor's invariant claims to the checks actually invoked.
- The finite encoding uses byte masks/counters (`checker.py:163–164`) but exposes unrestricted public `n` and `depth` arguments and CLI scope/depth values. Reject unsupported bounds (especially more than eight identities or byte-counter overflow) rather than silently generating a different SPIN model. The measured n=3 campaign is unaffected.
- `Validate` coerces its result with `bool(args["passed"])` (`engine.py:122`), so a JSON string `"false"` is treated as passing. Likewise base/version values are coerced using `int`. The manuscript says malformed events are rejected (main.tex:238). Either enforce the declared input types or narrow that statement and document the trusted-input requirement.
- The current scope restriction to the first n snapshot indices is explicitly disclosed (main.tex:348), which is good. Explain why it is useful and include the same restriction in `formal/SCOPE.md`, where a reader could otherwise assume all in-scope historical snapshots are rollback candidates.

## Questions for the authors

1. Is Deploy intended to replace a deployment snapshot or add availability to an existing deployment? Please make the same choice in the full and finite semantics.
2. What exact relation maps engine state to SmallState, particularly quarantine, deployment membership, validation records, and administrative replay events?
3. Should a monitor run with zero observed digests be presented as event admissibility alone, or as an incomplete conformance result?

## Recommendation

**Major revision.** The manuscript's honest limitations and accessible implementation support a focused repair. The major issues concern demonstrated transition correspondence, rather than a request to claim or prove unbounded implementation correctness.
