# Round 2 response — convergence on bounded feasibility scope

All three automated reviewers reported no remaining major concerns and recommended
minor revision. This is internal artifact review, not independent human peer review,
practitioner approval, or evidence of TSE acceptance.

| Comment | Action type | Resolution |
|---|---|---|
| R1 minor 1: merged-history scope | paper edit | E15 now explicitly retains one shortest engine history per projected state and does not enumerate ledger-only differences separately. |
| R1 minor 2: attempted/enabled counts | paper edit | Added 992 enabled successors alongside 3,000 attempted action applications; scope/negative actions remain explicit. |
| R2 minor 1: motif parameter exceptions | documentation + test | Datasheet says fan-out/depth bounds apply to random backbone, fixed synthesis/adversarial motifs can exceed them. Added explicit minimum/exception regression. E10 measured settings unaffected. |
| R2 minor 2: runtime history CSV | processing | Added mean_history_events to runtime_cost.csv from existing immutable raw records. No new measurements or changed timings. |
| R2 minor 3: E14 terminology | paper/response edit | Constructed post-withdrawal graph states have mixed provenance/use edges; corrupt states are not enacted through guarded admission. F1 remains an affected-set measure. |
| R2 minor 4: legacy pseudo-ablations | processing + generator fix | Historical fields preserved raw, excluded from interpreted summary; current generator omits them. Targeted guard/audit matrix supports the limited intervention claims. |
| R2 minor 5: empty truth / example snapshot | tests + provenance | Added inactive disconnected a5 with empty local/deployment impact. Future source snapshots include examples/scripts; current example added in an explicit post-run extension manifest without altering raw measurements. |
| R3 minor 1: recovery capability labels | paper clarification | Recovery is explicitly a dependency-presence example with empty capability sets; separate contract tests establish capability rejection. |
| R3 minor 2: moving shallow-head recipe | documentation | Removed moving-head depth suggestion; make realistic defaults to exact bundled content, cloning is only an extension. |
| R3 minor 3: host trust | retained scope | Host-owned exposure is not authenticated complete production context; ambient inputs/side channels remain unvalidated. |
| R3 minor 4: timing interpretation | retained scope | Graph batches and full controller timings remain separate; final report includes both limits. |

No numerical experiment required rerunning for these exposition/processing fixes.
Tests and manuscript processing/compilation were rerun. External multi-harness
capture, independent incident annotation, practitioner diagnosis, causal culprit
localization, production overhead and a complete implementation refinement proof
remain outside the measured scope. They are not marked completed by this review.
