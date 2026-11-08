# Round 4 response

Reviewers: R1 major revision (N3/R3/Rel4/V4/P3); R2 minor (N3/R3/Rel4/V4/P3); R3 minor
(N3/R3/Rel4/V4/P4). Internal automated review, not peer review.

## Implementation and analysis changes

| Request | Action |
|---|---|
| R3.1, R1.M6 revalidation evaluated is not Algorithm 5; attestation does not exist | New `heartness.revalidation`: Algorithm 5 as a composition of existing operators. An attestation revision (kind `attestation`, host-authorized seed) is admitted first; each cleared member is re-admitted in history order as a fresh copy with `src = {attestation}` and dependencies remapped to re-admitted copies; members with a dependency that is neither active nor re-admitted are rejected (P3). Withdrawing the attestation suspends every re-admission through the ordinary closure (tested). The live evaluation (`experiments/live/supplement.py`) now calls the same pure `plan()` that the engine executes; a test checks plan == execution. Under the old restore, 59 of 75 curation runs (95 revisions, all profiles) differed. All 75 curation supplements were regenerated on Fir (run am-20261107-080855, job 2882647; old files kept as `supplement_v1.json`); all 150 recorded plans equal `plan()`. ExpeL is unaffected (insights have no dependencies). Result: HS_judge is essentially R4 (recall 0.79, F1 0.65 vs 0.69; 19 rejections, none contaminated); HS_emb recall rose from 0.68 to 0.86 because P3 rejected 20 contaminated revisions the embedding screen had cleared (76 rejections in 51 runs). |
| R1.M2 re-derivation from the corrupted experience passes every guard | `Withdraw` now accepts an experience: it is marked tainted (`State.tainted`), every revision it motivates is withdrawn with its closure, and every future revision motivated by it is a forbidden root (P2). Two new tests (re-learning refused after experience withdrawal; still admitted after revision-only withdrawal, documenting scope). Proposition 2 extended (forbidden roots F include tainted motivation). Re-learning from *new* evidence stated as out of scope. |
| R2.M1 "identical contexts never flip" is a cache artifact | Correct. Replaced by an independent-generation measure: byte-identical evaluation prompts (model, seed, task, deployment, context texts) in two different runs, i.e. separate processes with separate caches. ExpeL 178/4,349 (4.1%), curation 2/273. Revalidation evaluations excluded (they read every cache file). The order-sensitivity claim was withdrawn (confounded). All four places in the paper fixed. |
| R1.M4 EME trade-off; operator-configurable EME | New post-hoc condition H_EME-fail (EME edges only from runs whose task failed), computed from recorded state: recall 1.00 (including the EME-only run, whose task failed), 17.24 vs 20.79 suspended, F1 0.22 vs 0.18. Reported in E-L, table, Lessons, conclusion. |
| R2.M4 closure-vs-cut is structural | Stratified by fault task: strictly smaller in 0/15 (task 2), 33/45 (task 8), 9/15 (task 9); text explains the dependence on the first composition and states that EME applied to broadcast contexts is the cause. |
| R2.M5 / R1 minor 7 H_faulty misses | All 3 runs have ambiguous root labels; text says so. |
| New derived numbers | `structure` block: contamination and detector misses by kind, closure vs cut (overall and by fault task), EME-only runs (paths relative to campaign), runs with contaminated profiles; `cost.engine_percent_max`; harness line count and evaluated-condition count as macros. |

## Paper changes

| Request | Action |
|---|---|
| R1.M1, R2.M2, R2.M3, R3.2 summaries more favourable than tables | Abstract, intro, RQ1 box and conclusion rewritten: every detector had higher F1 under both policies; misses named per detector (R2 2, R4 13, R3 22 of 42); "as rollback and reset did"; unfavourable F1 and collateral tests H vs R2/R4 reported with Holm p and paired counts; effective n stated for both policies. "Containment is inductive" -> "suspension invariant", "prove" -> "show"/"proof sketch". |
| R1.M3 value over rollback | "Needs no fault time" dropped (root time is in the history); "reaches every deployment" restated as a design requirement that a rollback meets only if redeployed; enforcement after the fact stated as evidenced only by RQ2 controlled scenarios, not live evolution (Limitations, conclusion future work); rollback-and-re-evolve discussed, with the paired clean run as its counterfactual and replayability as its precondition. A live mid-run withdrawal experiment was not run: in both policies no later step re-reads suspended state or rolls back, so it would exercise no guard; stated as future work. |
| R1.M5 positioning | PROV can express the EME path; claim narrowed to "harnesses do not record run contexts as inputs, and no provenance system uses such paths for admission". EVOMAL: "candidate remedy for the non-adversarial case". Deletion propagation: forward direction related to view maintenance (counting) and provenance semirings (new, verified citations), with the reason LLM synthesis forces all-inputs semantics. "Exact removal" replaced by rollback-and-re-evolve discussion. |
| R3.3 running example hides closure cost | Running example now states that every memory after the first profile rewrite is EME-exposed and joins the closure. Indices aligned with code (task 8 -> m7). |
| R3.4 length | Abstract 249 words; intro components as a list; intro results paragraph qualitative; RQ1 box five sentences; duplicate "both policies" paragraph removed. |
| R3 Fig. 1 | Revalidation arrow (10) added. |
| R1 minors | Load precondition in Proposition 2 proof; rollback does not change deployments; T cut vs Proposition 1 cut; seeds t=0; judge prompt receives all roots; E-G contribution beyond mutants; E-S claim qualified; "model-driven" justified (models@run.time, verified citation); harness line count from a macro; Table XI: version-control row, HEARTNESS cells qualified. |
| R2 minors | p for H vs R2 fixed; ExpeL suspension "of learned revisions"; dev F1 three decimals; Table VII caption denominators and by-construction rows; Fig. 5 caption; EME price quantified; CPU fallback for generation attempts disclosed (no reported run affected; device table shipped); CIs described as shipped in the package. |
| R3 minors | Base-profile fallback after withdrawal stated in the E-L procedure; Dpl_before defined in Algorithm 5; projection description made consistent; RQ3 box "1-3 s"; organization paragraph; user-study sketch in Limitations; Limitations mention revalidation. |

## Not done / disagreed

- Live continuation experiment (R1.M3): see above; claims narrowed instead.
- Human oracle check (R2): not available; remains the main construct threat.
- Anonymized artifact link (R3): cannot be minted here.
- Compute-platform paragraph kept (requested by the author); shortened earlier.
- Per-generator stratified analysis (R2.M6): per-generator adoption and propagation are in Tables IV/VI; per-generator remedy tests would have n <= 11.
