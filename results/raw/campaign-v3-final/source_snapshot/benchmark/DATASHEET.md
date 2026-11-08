# EvoTraceBench 1.1

Purpose: evaluate recorded lineage queries and lifecycle safeguards for evolving
harnesses, not model intelligence, semantic safety, or user productivity.

Generation: deterministic Python random seeds; seven artifact types, nine scenario
families. DAGs are built in revision order with configurable source count, depth,
multi-source synthesis, lexical decoupling, inactive-revision fraction, deployment
count and root frequency. `withdrawal_frequency` is reserved metadata in v1; it is
not a tested workload parameter. `capture` is applied by the observation adapter,
not by the truth generator. Families share a random backbone but have distinct
initial structural motifs; family labels alone do not prove realistic failures.
Engine-level challenge fixtures are separate. Version 1.1 adds dependency-only
consumers, alternating source/use paths, deployment-only active revisions and
realized factor counts. Fan-out 3 and 6 now differ. Version 1.0 results remain
available as explicitly superseded campaigns.
Fan-out and depth constrain the random backbone, not the fixed initial motifs.
For example synthesis/adversarial motifs require two sources and can have derivation
depth two even when fan-out=1/depth=0 is requested. The realized fields expose these
exceptions. E10 uses the faulty-lesson motif, which respects its reported fan-outs.
Lexical decoupling substitutes controlled phrase families and random identifiers;
it is not a claim about natural paraphrase quality. No LLM, personal data or
production traces are used. All content is synthetic and locally generated.

Schema: scenario JSON has benchmark version, config, artifact records, active IDs,
deployment membership and construction truth. Artifact record fields are the
dataclasses in `src/heartness/model.py`. Truth for queried root and target consists
of descendants, active impact, experience origins, fault indicator and challenge
description. Oracle ancestry uses inherited integer labels at construction time,
not Graph traversal, Engine admission, or baseline output.

Validation: tests check closure labels against hand-computed examples, source
ordering, determinism, parameter effects and roots. A recorded random sample audit
is an approach-versus-oracle agreement check, not independent benchmark validation.
`hand_cases.json` separately specifies expected source-only, dependency-only, mixed,
disconnected and deployment-only sets without using generator or query output.
This is still not independent human validation. Generator and tool share
artifact schema and authorship, so common conceptual mistakes remain possible.

Limitations: no real harness dataset is bundled. Deployments are connected logical
sets. Text similarity intentionally has limited evidence when source text changes;
this measures information loss rather than competing with a tuned learned model.
The B0 baseline models log/blame within a path, not all Git copy/move heuristics.
Contracts are finite capability labels. Family holdout is a sensitivity summary
without training, not a generalization test. These limits must appear in the paper.
