# Specification scope and independent encoding

The executable metamodel is `model.py`; `engine.py` supplies transactional
transitions. `properties.py` audits P1–P10. All ten are safety properties: G(Pi).
P7 (prefix preservation), P5 (rollback event) and P9 (accept event) are transition
predicates, using pre/post state. No unconditional liveness claim is made: the
environment can stop proposing, reject forever, or remain disconnected.

SPIN 6.5.2 independently implements a finite projection in Promela. Python BFS
and SPIN use different transition code, sharing only graph masks and scope values.
Both quantify nondeterministically over Propose, Validate, Accept, Withdraw,
Deploy/Reuse, and Rollback. Derive/Edit/Merge are represented by static chain/star
edges selected before exploration, not dynamically synthesized graph structure.
Validation is Boolean; hashes, contracts as arbitrary capability sets, external
effects, experience records, history chains, multiple deployment identities and
runtime Load are outside this projection. P2/P3/P4/P8/P9 have projected checks;
P5's restoration assignment is modeled but not independently asserted. P1/P6/P7/
P10 are tested in Python, not verified by SPIN. This is bounded cross-validation,
not a refinement proof for the engine. Steps bound operations, not pan's internal
statement depth. Python state count and SPIN storage count are not comparable.

No counterexample is fabricated: guard-mutant witnesses are explicitly seeded
faults. Reference failures, if found, are recorded separately as genuine bugs.
Python BFS gives shortest paths by operation count. SPIN trails are independently
retained, but their internal statement count is not a shortest operator length.
Engine replay of projected witnesses is a separate integration test; projection
replay alone cannot establish implementation correspondence.

Rollback and revocation conflict: an old snapshot may contain withdrawn lineage.
The resolution is to reject exact rollback to such a snapshot, keeping revocation
monotone. Successful rollback restores exactly the target active set and creates
a new history entry; it does not rewrite historical snapshots or external effects.
Rollback affects the local harness; other deployments require explicit plans.
