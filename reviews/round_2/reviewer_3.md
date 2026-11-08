# Reviewer 3 — practitioner and AI harness expert — round 2

This is an automated review in the project's reviewer exercise. It is not independent human peer review, a practitioner study or an external TSE recommendation. Scores range from 1 (poor) to 5 (excellent).

## Material and verification

Read the round-1 response, revised manuscript passages, README, `capture.py`, `examples/recovery.py`, CLI and focused tests. Checked the revised processed summary (1,905 records) and controller-cost reporting. Executed `python -m examples.recovery`, `pytest tests/test_cli.py -q` (9 passed), and `pytest tests/test_capture.py -q` (3 passed). No implementation changes were made. This is a targeted follow-up of my practical concerns; it is not an independent re-execution of the whole experimental campaign or external bibliographic verification.

## Summary

The revision makes the intended prototype considerably easier to assess. The capture adapter now exposes a concrete host-owned boundary rather than implying source exposure can be recovered automatically. The same-history recovery example demonstrates containment, rejected unsafe rollback, successful empty local restore, independently justified fresh lineage and explicit redeployment. It retains old quarantine and external effects. CLI history persistence resolves the misleading sequence identified in round 1. Separate controller measurements now expose whole-state transaction/replay cost rather than letting fast graph queries stand in for admission throughput.

These changes resolve my actionable major concerns for a bounded feasibility study. Production capture, external practitioner benefit and real incident remediation remain unvalidated, but the manuscript explicitly avoids claiming them. Their absence is an external-evidence boundary rather than a newly discovered contradiction requiring another prototype revision.

## Scores

| Criterion | Score | Justification |
|---|---:|---|
| Novelty | 3/5 | The contribution remains integration and revocation/rollback semantics rather than a new provenance or checking algorithm. The worked continuation now makes that integration concrete. |
| Rigor | 4/5 | The operational walkthrough, focused CLI regression, capture-boundary tests and separate full-controller workloads strengthen evidence for the limited claims. They do not independently validate production adoption. |
| Relevance | 4/5 | Preserved historical identities, transitive suspension and the inability to restore a revoked snapshot address credible harness maintenance tasks. |
| Verifiability and Transparency | 4/5 | Saved histories, expected outputs, explicit observation coverage, retained quarantine and separately scoped timings make the central behavior reproducible. |
| Presentation | 4/5 | The added capture/recovery paragraph joins formal rules to executable behavior and explains the difficult fresh-lineage qualification plainly. |

## Disposition of round-1 major concerns

1. **Capture boundary: resolved for prototype/interface scope.** `prepare` freezes explicitly selected texts/IDs and `propose` attaches host-owned source identities around the policy call. Untracked inputs can be declared. The manuscript says ambient context, side channels and production generation are outside validation, including adjacent to public replay. This is illustrative instrumentation, not demonstrated complete provenance in a deployed agent.
2. **Recovery continuation: resolved.** The executed example produced contained local state `[m2]`, rejected rollback to version 5, restored an empty local set while deployments still contained `[m2]`, then admitted and deployed `[a3,m3,s2]`. Old quarantine `[a1,a2,s1]` and effect `x1` remained. Permanent quarantine/no revalidation and the independent-feedback assumption are explicit. This avoids disguising an edit of withdrawn content as fresh recovery.
3. **CLI process-local state: resolved.** README explicitly documents stateless invocation and the `--save-events`/`--events` sequence. The focused test confirms that rollback-plan on the saved withdrawn history reports inadmissible. Fresh-file output semantics are documented.
4. **Controller costs: resolved as measurement/claim calibration.** E13 separately measures modest complete guarded workloads, capture serialization, withdrawal and replay at 4/8/16/32 artifacts. Manuscript distinguishes these from graph timing, notes allocation tracing and excludes claims about production overhead or large-scale admission. Costs remain a practical limitation; now they are exposed rather than obscured.

## Major concerns

None remaining for the stated bounded research-prototype claim. I do not infer production safety, useful human remediation, or sufficient TSE novelty from this disposition.

## Minor concerns

1. The recovery configuration `a3` has no required capability, while its new skill `s2` provides no declared capability. That is a valid dependency-only recovery example, but a brief sentence could distinguish it from the earlier recovery-capability contract example; optionally carry explicit capability labels through the continuation. This does not invalidate containment/recovery results.
2. README still includes the moving-head `--depth 40` suggestion. Exact replay is now correctly designated as bundled content and has an offline command, so this is no longer a reproducibility blocker. Removing the dated shallow-clone suggestion would simplify the distinction between exact bundled replay and a broader-history extension.
3. Keep the host trust assumption prominent: a frozen Exposure record does not authenticate a real generator's complete context or prevent a caller from fabricating host inputs. Current wording about side channels and ambient context is appropriately bounded and should be retained.
4. As an editorial improvement, state the graph-versus-controller timing difference whenever the 2,048-artifact graph result is summarized outside RQ3; the small full-controller workloads are the relevant evidence for lifecycle execution.

## Author questions

- In a future controlled revalidation design, will valid corrective use of withdrawn content be represented as a distinct remediation relation rather than simply bypassing source lineage?
- Will deployment acknowledgment and running-task cancellation be explicit state transitions? They remain the most significant next step from logical membership containment to operational containment.

These are future-work questions, not prerequisites for the present restricted claim.

## Recommendation

**Minor revision.** My round-1 major concerns are addressed. The remaining items are small clarifications; external practitioner efficacy and production source capture remain honestly unclaimed. Automated reviewer convergence must not be described as independent human approval or evidence of submission acceptance.
