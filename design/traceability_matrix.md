# Idea-to-evidence traceability

| Idea claim/task | Design/code | Test | Experiment | Paper |
|---|---|---|---|---|
| persistent feedback revisions | simulator.example, Engine | example + operator tests | E07/E09 | §II, §III |
| experience motivation | Experience/Proposal/Artifact | guards, graph truth | E01 | §III metamodel |
| copy/summary/synthesis lineage | immutable sources, Graph | hand closure, generator oracle | E01/E03 | §III provenance |
| source edited or deleted | Edit/Withdraw with history | derive/edit/merge | E01/E07 | §III transitions |
| origins/descendants/active dependents | Graph | hand-computed closures | E01/E02 | RQ1 |
| cross-deployment reuse | same revision IDs, suspension | example withdrawal | E07 | RQ2/RQ3 |
| invalid dependency reuse | finite contracts | contract replacement rejection | E04/E05 | §III contracts |
| policy-independent transitions | Engine guards | randomized sequences | E04/E05/E11 | §III checking |
| validated vs loaded drift | validation/snapshot digests | digest mutation | E09 | §III monitor |
| regression revision candidate | first installation index | culprit_revision | E01 metadata; not causal evaluation | limits |
| rollback targets | rollback_plan/last_good_version | exact restoration/revocation conflict | E07 | §III rollback |
| external effects remain | ExternalEffect + plans | effects retention | E07/E09 | limits, RQ3 |
| incomplete history | capture adapter | capture endpoints | E02 | RQ1, threats |
| state vs causal contribution | typed exposure semantics | no causal verdict returned | no causal experiment claimed | §§I,III,IV |
| abstract model correspondence | SPIN + BFS + engine replay | differential verdicts | E05/E06/E09 | RQ2/RQ3 |
| privacy/authority of withdrawal | host assumptions only | not implemented/tested | no evidence claimed | future work |

This table explicitly marks non-evaluated tasks; first-installation localization
does not fulfill culprit top-k accuracy without a controlled causal failure oracle.
