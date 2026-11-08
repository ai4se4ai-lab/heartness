# Reviewer 2 — empirical software engineering — round 2

**Automated review.** This is follow-up artifact inspection, not independent human validation. I read the round-one response, revised generator/datasheet and hand-specified cases, targeted ablation and linter runners, runtime-cost campaign, processor, revised evaluation text, factor/runtime/exact-origin outputs, finalization provenance and sampled actual raw E13/E14/E04/E11 results. I confirmed that the selected campaign `campaign-20261106T210441873255Z` contains 1,905 experimental records. I did not rerun the whole campaign.

## Summary

The revision addresses the substantive empirical defects from round one. Dependency-only links and scored deployment membership now exercise distinctions central to the approach. E10 realizes different source counts at fan-outs 1/3/6 and different deployment membership workloads. Targeted property challenges expose guard effects separately from deliberately removed audit predicates. B3 is actually measured on 90 withdrawal cases and 90 clean controls; its seed-clustered affected-set F1 is approximately 0.229. E13 measures small guarded workloads rather than extrapolating controller cost from graph queries. E11 now includes BFS at the same scope, bound and nominal budget as the sequence searches. The hand-specified mixed-path fixture adds a useful check independent of generator labels.

The resulting evidence remains synthetic feasibility evidence. The manuscript says so consistently. Missing production instrumentation, external incident annotation and practitioner benefit are research limitations rather than new actionable defects in the stated narrow evaluation. I do not request them as a condition for resolving this review.

## Scores (1 poor–5 excellent)

| Criterion | Score | Justification |
|---|---:|---|
| Novelty | 3 | The evaluated integration now has clearer operational content beyond exact reachability, although it remains an integration contribution rather than a new recovery or checking algorithm. |
| Rigor | 3 | Targeted challenges, effective factors, B3 measurements and actual guarded-workload timings substantially improve coverage. Scale and realism remain limited but appropriately bounded. |
| Relevance | 4 | Immutable inherited revisions and withdrawal across registered deployments address a meaningful maintenance problem. |
| Verifiability and Transparency | 4 | Raw preservation, source snapshots, explicit finalizer repair provenance and inspectable seed-level processing support verification. A few report/schema inconsistencies remain below. |
| Presentation | 4 | The revised text distinguishes graph correctness, enforcement, audit dependence and production claims. Minor wording and artifact references still need correction. |

## Major concerns

**None remaining for the explicitly bounded feasibility claims.** Round-one major concerns are addressed by measured changes or appropriately narrowed interpretation. This does not imply that every original project aspiration or a production-effectiveness evaluation is complete.

## Minor issues and required actions

1. **Generator parameter bounds have motif exceptions.** Fixed family motifs override fan-out/depth constraints. I directly checked `Config(family='synthesis', fanout=1, depth=0, artifacts=16)` and the adversarial equivalent: both realize `max_sources=2` and `max_depth=2`. The selected E10 family respects the reported fan-outs, so this does not invalidate its factor table. **Action:** document motif minima/exceptions in the datasheet or enforce/reject incompatible configurations, and add a small parameter-contract check. Do not advertise depth/fan-out as unconditional generator bounds.

2. **One manuscript reference overstates the runtime CSV contents.** The E13 paragraph says history lengths are recorded in `runtime_cost.csv`; the processor writes them to raw records (`history_events`) but omits them from that CSV. **Action:** add the history-length summary to the CSV or point readers to the raw E13 records. The timing values themselves are traceable.

3. **E14 terminology should describe constructed graph violations precisely.** `reviews/round_1/response.md` calls these “source-only withdrawal faults,” but the v1.1 generator includes dependency-only paths and the linter inspects both sources and dependencies. E14 removes the source from the active set and declares it withdrawn while descendants remain active; it does not enact these corrupt states through the guarded engine. **Action:** describe them as constructed post-withdrawal graph states with mixed provenance/use links. Keep affected-set F1 distinct from binary defect-detection rate; the current manuscript mostly does this correctly.

4. **Legacy ablation fields should be clearly segregated in processed evidence.** E04 still retains the old `latent_mutant_found` and switch-based monitor fields alongside the new targeted matrix. They remain weak ablation evidence even though the paper no longer relies on them. **Action:** label the legacy output as a withdrawal fixture/separate component demonstration in the data documentation, or omit those fields from the interpreted ablation table. Preserve raw history. The targeted guard/audit distinction is adequate for the revised claim; manually filtering an audit finding is predicate-dependence evidence, not an independently configured admission mechanism.

5. **Complete small oracle controls and snapshot coverage.** The new hand-worked fixture covers disconnected and deployment-only membership, but every specified local impact is nonempty. Source snapshots cover `src`, `benchmark`, `experiments`, `formal` and `tests`, while the new experiment runner also imports `examples.recovery`. **Action:** add an explicit empty-impact expected case and include imported example sources in future campaign snapshots (or document the full repository revision as their required source). These are inexpensive completeness improvements, not grounds to rerun the current measurements.

## Questions for the authors

1. Will future reports distinguish nine structural motif labels from nine independently sampled real incident populations? The current restricted wording should be retained.
2. Can the response identify original aspirational deliverables that remain outside the measured scope, such as production overhead, causal culprit localization and practitioner diagnosis, without marking those complete solely because limitations are disclosed?

## Recommendation

**Minor revision.** The main empirical objections from round one have been substantively addressed. Resolve the artifact/wording corrections above and preserve the present feasibility-only scope. No additional production study is required to resolve this automated review; external novelty and significance assessment remain the responsibility of human reviewers and the authors.
