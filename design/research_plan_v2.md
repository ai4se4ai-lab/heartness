# Research plan v2 (2026-11-06) — written before the live study is run

Prompt: user-supplied TSE prompt (3 RQs, running example, TikZ overview, per-component
algorithms, >=3 automated review rounds). Builds on the HEARTNESS prototype and the
selected synthetic campaign `campaign-20261106T210441873255Z` (results unchanged).

## Core claim
Persistent state in a self-evolving harness can be made traceable and withdrawable by
(i) a typed metamodel of immutable revisions, (ii) host-captured generation exposure,
including the experience-mediated channel (behaviour -> experience -> reflection),
(iii) closure-based withdrawal across deployments, (iv) guarded admission whose finite
projection is model checked and replayed against the implementation.
Exposure is an over-approximation of influence; it is not causal attribution.

## Novelty (to be tested, not assumed)
1. Experience-mediated exposure edges: contamination can re-enter memory through runs
   that loaded contaminated state. Prior provenance capture records synthesis inputs only.
2. First live measurement (to our knowledge) of faulty-lesson propagation and withdrawal
   in an LLM-driven self-evolving harness with an independent content oracle and task outcomes.
3. Lifecycle semantics resolving rollback/withdrawal conflict, checked by SPIN + BFS.

## Research questions
RQ1 Containment: how completely and precisely does closure-based withdrawal remove state
   affected by a faulty experience vs file-level deletion, lexical, embedding and LLM-judge
   remediation, and what happens to downstream task success? (live study L1 + synthetic E01-E03, E10, E14)
RQ2 Assurance: do the lifecycle guards prevent property violations, can bounded model checking
   find guard faults, and does the finite model correspond to the implementation? (E04-E06, E11, E15)
RQ3 Cost & limits: what does capture/admission/withdrawal cost in the live harness and at scale,
   and what does runtime conformance detect or miss? (L1 timing, E08, E13, E09, E07)

## Live study L1 design
Generator models: qwen2.5:7b (main), llama3.1:8b (replication). Temperature 0, fixed Ollama seed.
HumanEval+ (164 tasks): 30 fixed held-out evaluation tasks (seed 7 split), evolution tasks drawn
per run from the remaining 134. 24 evolution tasks/run: solve -> test -> experience -> reflect
(memory) ; every 6 tasks curate skill from the batch's memories ; after tasks 12 and 24
compose deployment profiles D1/D2 from skills. One feedback message corrupted per faulty run
(fault types F1 print-not-return, F2 stringify-return, F3 integer-division), position by seed.
Paired clean run with the same seed and no corruption.
Remedies (same root identity given to all): R0 none, R1 delete root (file-level revert),
R2 TF-IDF cosine >= tau, R3 nomic-embed cosine >= tau, R4 LLM judge (generator model),
H HEARTNESS withdrawal; ablations H-noEME, H-noDeps, H-local (no deployment propagation).
tau tuned on dev seeds 100-101 only (reported seeds 0-4). Oracle: two different judges
(gpt-oss:20b, mistral-small:24b), unanimous labels, disagreement reported; no human labels.
Metrics: precision/recall/F1 of suspended non-root set vs contaminated set, residual active
contaminated artifacts, collateral suspensions, held-out pass@1 and fault-signature rate.
Statistics: paired Wilcoxon over runs, Vargha-Delaney A12, Holm correction, bootstrap CI.
Negative outcomes (e.g. no propagation in a run) are reported, not excluded.
