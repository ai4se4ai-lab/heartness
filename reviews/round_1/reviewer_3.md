# Reviewer 3 — practitioner and AI harness expert — round 1

This is an automated review by an independent agent context for the project's requested reviewer exercise. It is not independent human peer review, an external TSE decision, or evidence of practitioner participation. Scores use 1 (poor) through 5 (excellent).

## Material inspected and checks

Inspected `docs/TSE/main.tex`, `docs/work/idea.md`, README, design/metamodel, problem analysis, reading and traceability documents; engine, graph, CLI and simulator sources; processed summary and public-replay metadata. Executed the bundled example's trace, withdrawal plan, withdrawal, and rollback-plan CLI commands. No implementation was changed. Literature positioning is assessed against the supplied manuscript and reading record; external reference metadata was not independently reverified in this review.

## Summary

Heartness makes a relevant maintenance problem concrete: a recorded lesson can be transformed and reused after its original file changes, and a historical snapshot can become inadmissible after revocation. Its immutable identities, transitive suspension, capability checks, external-effect records and observed-state replay form a coherent research prototype. The manuscript deserves credit for explicitly reporting ties with capture-only, limited public-file replay, high relative monitor cost, hidden-action misses, and a modeling error shared by the two encodings. These disclosures materially improve verifiability.

The evidence supports controlled lifecycle feasibility. It does not establish the hardest practical step—capturing generation exposure in an operating harness—or a useful incident-to-recovery workflow. The distinction matters because the complete-capture result is intentionally unsurprising. The paper should demonstrate the operational content of its narrower integration contribution with a small, exact worked workflow and clarify the CLI's process-local behavior. This does not require claiming production readiness or inventing a user study.

## Scores and justification

| Criterion | Score | Justification |
|---|---:|---|
| Novelty | 3/5 | The withdrawal/rollback conflict and integration with registered active sets are a plausible focused contribution. Most individual mechanisms are established; the existing related-work discussion appropriately avoids claiming invention of provenance or graph traversal. Increment beyond an ordinary provenance-backed deployment controller needs a sharper worked comparison. |
| Rigor | 3/5 | Fixed seeds, construction truth, fault replay and independent finite verdicts are useful. Synthetic generation, shallow public revision import, a single principal incident fixture and limited checker coverage constrain practical conclusions. Honest threat statements do not supply the missing operational evidence. |
| Relevance | 4/5 | Persistent skills, memories, multi-source generation and reuse are credible maintenance concerns. Distinguishing exposure, causality, content validity and irreversible actions is particularly relevant to agent maintainers. |
| Verifiability and Transparency | 4/5 | Commands, raw-to-paper indexing, source paths, bounded claims and negative results are unusually explicit. CLI invocation semantics and the exact public-replay boundary still need more usable reproduction instructions. |
| Presentation | 4/5 | The example and property coverage table are clear. A transition trace through actual containment and recovery would connect the formal exposition to the developer interface more effectively. |

## Major concerns and required actions

1. **Capture feasibility is assumed rather than demonstrated.** `simulator.example()` explicitly supplies the source tuple to `s1`; public replay imports revisions but does not observe an autonomous summary/merge. Thus the system is tested primarily downstream of the practical information bottleneck. Required action: add a concrete capture-boundary walkthrough naming which component supplies source IDs, when those IDs become immutable, how seed authority is provided by the host, and how omitted/out-of-band inputs are reported. Prefer a small instrumented adapter/replay illustration; if no adapter is implemented, label the walkthrough as an interface contract and list its untested parts. State this distinction adjacent to the public replay result, not only in threats. External multi-harness evidence remains a prerequisite for strong deployment-utility claims, and must remain unresolved if not conducted.

2. **The running example stops at containment rather than demonstrating recovery.** Withdrawal puts descendants and consumers into quarantine, while `_safe` rejects their closure indefinitely. `Edit` must preserve the previous identity as a source; consequently an edit retaining withdrawn ancestry cannot simply rehabilitate the artifact. The API has no unquarantine/revalidate operation. Required action: explicitly describe this intentional permanence and give one executable continuation from the incident to a newly admissible active configuration, including the provenance/authorization basis for corrected replacements. Do not suggest revalidation clears quarantine unless implemented. Show the rejected unsafe rollback and a successful local restoration in the same engine/event history, and distinguish local restoration from deployment updates. This makes the lifecycle integration assessable without pretending semantic correction is proven.

3. **CLI behavior can mislead a maintainer following the example commands.** Each invocation without `--events` creates a new pristine running example. I ran `heartness withdraw --artifact m1`, which printed `active_after:["m2"]`, followed by `heartness rollback-plan --version 5`, which printed `admissible:true` because the second command rebuilt the pre-withdrawal state. This is coherent process-local behavior, but README does not explicitly explain it, and it obscures the central revocation/rollback result. Required action: document that commands are stateless analyses of supplied event histories and do not persist mutations; supply a single-process library example or an event-history file/command sequence demonstrating post-withdrawal rejection. Include expected outputs. Persistent storage is not required for this research prototype.

4. **The measured fast path is not the lifecycle admission path.** Graph construction/query batches at 2,048 revisions exclude `Engine.apply`'s whole-state deepcopy and growing history. RQ3 correctly discloses this, but readers still cannot estimate the integration's relevant operational cost. Required action: either add a small clearly scoped engine admission/withdrawal/monitor scaling measurement with fixed workloads and raw records, or make the absence of lifecycle throughput evidence explicit in the RQ3 answer and abstract's feasibility interpretation. Do not reuse graph timings as deployment/controller throughput. The latter wording fix resolves claim calibration, while performance feasibility remains unestablished.

## Minor concerns

- The history/lexical comparison establishes an information advantage, and capture-only ties by design. Add a compact worked comparison showing what the controller rejects that equal-information query-only capture merely reports; do not use it as evidence of a new reachability method.
- `trace --artifact s1` returns no descendants, correctly because agent configurations are consumers rather than derived revisions. Show that difference beside `impact` so readers do not mistake the trace output for absence of affected deployments.
- The public replay recipe cannot reliably recreate a historical shallow boundary using `--depth 40` against a moving default branch. Prefer a pinned fetch recipe where supported, or designate bundled content/commit lists as the exact replication input and cloning as a broader-history extension.
- The remediation plan currently lists every recorded external effect. Label this conservative reporting explicitly so it is not interpreted as proven causal attribution of each effect to the withdrawn revision.
- Related work is fair within the supplied set. For submission, sharpen the comparison with existing provenance-backed configuration/dependency invalidation and deployment rollback patterns; do not claim these systems lack lifecycle features solely because the manuscript has not studied them.

## Questions for the authors

1. How does a real harness enumerate source exposure when context includes retrieved memory, skills, ambient instructions and model-internal knowledge? Which of these are deliberately outside the recorded relation?
2. What authorized origin should a corrected replacement carry if retaining its withdrawn predecessor as a source makes admission impossible? Is the system intentionally sacrificing provenance continuity for an independently justified fresh revision?
3. Are deployments snapshots of future availability only, and can a run loaded before withdrawal still record an external effect afterward? The implementation appears to permit that; a short explicit example would make the observation/containment boundary concrete.
4. What is the smallest operational result that distinguishes this integration from complete capture plus a manually invoked dependency invalidation script?

## Recommendation

**Major revision for the automated project review.** The prototype and manuscript already justify a transparent bounded feasibility study. Resolve the actionable interface, lifecycle and claim-calibration issues above, while preserving the explicit statement that production utility, independent practitioner benefit and real synthesis capture remain unvalidated. No amount of automated reviewer convergence should be presented as replacing those external validations or establishing TSE acceptance.
