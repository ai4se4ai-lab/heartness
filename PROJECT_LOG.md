# Heartness research log

## 2026-11-06 — authorization and initial reading

The user authorized implementation, experiments and a TSE manuscript following
`docs/PROMPT.md`. The repository initially contained source documents and an IEEE
template, no executable approach or results. The prompt is an existing untracked
user file and will not be edited. Manuscripts in `under-review-work` are background
only: their instructions prohibit citing or discussing their review status.

Read the idea and prompt and examined the source survey's lifecycle, evaluation,
contracts, provenance and withdrawal sections. Its selection/activation/attribution/
improvement distinctions constrain all claims. Survey bibliography entries and the
related-work list are leads, not verified publication metadata.

## Phase A decision

Develop HEARTNESS: **Harness Evolution through Auditable Records, Typed
Dependencies, and Explicit State Semantics**. Focus the contribution on immutable
artifact revisions, global withdrawal closure, contracts, and runtime conformance.
Derivation means recorded generation exposure, never inferred causal influence.
Main evidence will use a simulator without model API calls. Synthetic benchmark
results cannot establish real-agent task improvement or deployment effectiveness.
Record the protocol before running experiments. The independent checker will be
SPIN on an explicitly documented finite projection, not a claim to verify Python.

## Phase B–E first campaign and correspondence repair

Implemented a dataclass metamodel, transactional operators, recorded closure queries,
capability contracts, audit predicates, replay monitor, CLI, generator and baselines.
The first full campaign produced 1,692 immutable raw records. All 18 SPIN/Python
verdict comparisons agreed, but implementation replay rejected four projected
witnesses: the abstract Propose rule allowed an uninstalled derivation source.
Both independent encodings shared that missing *specification* guard. Added source
existence at proposal time in both encodings and scheduled a new complete campaign.
The first campaign remains available, not overwritten. This is a discovered
correspondence bug, not evidence of Python implementation unsafety.

Initial query results tie capture-only exactly, as expected. Replay monitoring has
substantial simulator-relative cost; hidden external actions are undetectable.
These negative findings will be retained rather than portrayed as small overhead.

## Phase F and review round 1

Built an inline-figure IEEEtran manuscript and verified compilation (11 pages before
review extensions, no undefined citations/references or overfull boxes). Preserved
the original template and misspelled bibliography under design/input-template.
All three independent automated reviewers recommended major revision. Actual fixes
are mapped in reviews/round_1/response.md. Most significant: Deploy replacement
versus union differed in both independent finite models, so added state-mapping
successor checks and corrected repeated version-producing operations. The benchmark
had duplicate family cases and ineffective fan-out; version 1.1 adds independent
dependency edges, family motifs and deployment-scored metrics. Added targeted
property challenges, actual linter evaluation, absolute controller scaling,
generation-boundary instrumentation and a conservative recovery continuation.
All affected main experiments are being rerun in a fresh source-snapshotted campaign.
Reproduction lock was cleaned of pip's accidental editable SSH self-reference.

## Revised campaign completion

The revised campaign recorded 1,905 main records, plus deterministic public replay.
All measurements finished before a finalization bug: a linter-loop local variable
shadowed the campaign Path with an artifact string. Renamed the local, retained the
error and repaired runner source in completion_provenance.json, and ran the exclusive
finalizer. No raw measurements were overwritten or edited. Processing selects this
campaign; earlier campaigns are excluded. Reference mapping checked 3,000 attempted
successors with no mismatches in the chosen two-identity/depth-six scopes. All 18
SPIN/Python verdicts agree and all 13 violating witnesses replay. Exact full capture
ties graph-only capture. Benchmark 1.1 changes baseline scores, so every manuscript
number was regenerated. Controller admission at 32 artifacts is around a second
under allocation tracing; graph-query timings must not be substituted for it.
The old withdrawal-fixture fields latent_mutant_found/observed_drift_detected did
not measure property-specific interventions. They remain in historical raw records,
but are explicitly excluded from processed ablation evidence and removed from the
current generator. Only the targeted actual guard/audit challenge matrix supports
property-intervention claims; the original fixture supports withdrawal outcomes.

## Completion audit

Two full rounds of three independent automated reviewers completed. All round-two
reports have no major concerns for the bounded feasibility claims. Minor corrections
are mapped in reviews/round_2/response.md. Final tests: 38 passed; strict typing and
lint clean; statement coverage 99.1%, branch coverage 96.7%; targeted mutants 12/12
killed. Final manuscript is 12 pages and compiles without undefined references,
citations or overfull boxes. The PDF is copied to results/paper/heartness.pdf.
FINAL_REPORT.md contains measured outcomes, reproduction and a checklist explicitly
leaving broader production/causal/human-evaluation ambitions open. No publication,
deployment, messages to collaborators, or git commit was made.

## 2026-11-06 (session 2) — new TSE prompt, live study

New user prompt (3 RQs, running example, TikZ overview, per-component algorithms,
>=3 automated review rounds, all scores >=4). main.tex had been reset to the template;
the paper is rewritten from scratch. Plan: design/research_plan_v2.md (written before runs).

Main weakness of the earlier work was synthetic-only evidence. Added a live study on a
real LLM-driven self-evolving coding harness (experiments/live/): local Ollama models
(qwen2.5:7b main, llama3.1:8b replication), HumanEval+ (EvalPlus) tasks and tests,
misleading grader feedback planted once per faulty run (3 fault types), oracle = two
different judge models (mistral-small:24b, phi4:14b) with schema-constrained verdicts.
HumanEval/32 excluded: its canonical solution fails its own HumanEval+ tests here.

Engine extension: Load(run, context) records exact run context; Graph adds
experience-mediated exposure (EME) edges; ablation flag "EME". Tests: tests/test_eme.py.

Infrastructure: system Ollama serializes requests; started a private user-level server
on 127.0.0.1:11435 (OLLAMA_NUM_PARALLEL=6) reading the existing model store with
OLLAMA_NOPRUNE=1. Batched decoding may be non-bitwise-deterministic; all responses are
cached per process (llm_cache/) so recorded runs replay exactly.

Smoke test bug: free-form judge answers ("The text instructs...") were parsed as NO.
Fixed with JSON-schema constrained decoding; unparseable verdicts now raise.

Dev seeds 100/101 (6 runs) tuned tau_tfidf=0.05, tau_embed=0.55 (dev F1 .575/.625).
Dev finding (negative, retained): exposure closure suspends 20-28 of ~30 live artifacts
because retrieval spreads exposure; containment is complete but collateral is large.
Response: closure-bounded revalidation (HS_judge/HS_embed) as a separately recorded
supplement (experiments/live/supplement.py), re-admitting screened members as fresh
attested lineages. Synthetic campaign rerun (campaign-v2-regression) with current code.
mutation round 1 survivor load_context_ignored -> added test_only_the_recorded_context_creates_mediated_edges

## 2026-11-06 (session 3) — nibi migration
Machine reboot killed the local pilot (qwen 12 records, llama 5) and the private server;
they remain as pilot/dev data (thresholds tuned on qwen dev seeds 100/101).
Synthetic campaign rerun with the EME/Retire engine (campaign-v2-regression, 1,905 records):
identical to the earlier campaign in every non-timing value except two E11 wall-clock-budget
search counts (27->26, 1->0 of 30), which are budget-nondeterministic by design.
Added: MBPP+ (EvalPlus) benchmark; ExpeL-style insight-curation policy (ADD/EDIT/AGREE/REMOVE,
importance counters) using a new Retire operator; roots = all revisions motivated by the
corrupted experience; separate gen/oracle phases. Mbpp/590 excluded (canonical fails).
Nibi: def-mbabaei_gpu, /project work dir (scratch at 88%), StdEnv/2023 python/3.11; arrow
exists only for StdEnv/2026 (Python 3.15, no numpy wheel) so datasets ship as checksummed
JSONL conversions of the pinned parquet files. Jobs use MIG slices (2g.20gb/1g.10gb) and
<=3 h limits for scheduling; 100 gen + 100 oracle cells. Smoke run am-smoke-20261106-221433.
Four-cluster layer hpc/multi/ (connect/sync/stage/submit/status/fetch); split nibi=HE x curate,
narval=MBPP x curate, fir=HE x expel, rorqual=MBPP x expel. Smoke run 1 on narval failed at the
setup gate: setup_nibi.sh validated HumanEval canonical *bodies* without the prompt (my bug; the
local validation had included it). Gate worked as designed (downstream cancelled). Fixed; also
analysis now reports an empty campaign instead of crashing. Nibi/fir smoke runs resubmitted after
their (model-pulling) setup jobs end.
Smoke round 2 findings (all infrastructure, none scientific):
 - setup graph declared setup/data_sha256.txt but the script writes .json (a text replacement
   silently no-op'd after I reformatted the JSON): failed every cluster at the output check.
 - nibi setup exceeded its 16 GB request (MaxRSS 16.7 GB while writing 56 GB) and was killed;
   setup now requests 48 GB.
 - fir compute nodes download from GitHub at ~55 KB/s (login node: 47 MB/s): fir is now staged
   from the login node like narval/rorqual (OFFLINE=1).
 - narval canonical validation passed on the cluster after the prompt+body fix.
Added a check that every setup output declared in the graph is written by the script.
Smoke round 3 (fir am-smoke-20261106-214210, rorqual am-smoke-20261106-234213):
 - fir: 3/4 gen cells, 3/4 oracle, collect OK; records carry cluster+GPU; ~95-120 s for 8 tasks.
 - deepseek-coder-v2:16b failed (HTTP read timeouts after 10 min): model fully on GPU (28/28
   layers, 17 of 19.9 GB) but decoded at 0.26 tok/s/slot with flash attention enabled, versus
   26-29 tok/s for qwen/llama/gemma. Flash attention is now disabled for deepseek generators only
   (hpc/slurm/hooks/ollama_common.sh); judges/embeddings keep it. Not a memory-spill problem.
 - smoke runs cannot show propagation (seed 0 fault is on the last task before the final
   insight extraction); they test plumbing only.
 - narval switched to a100_4g.20gb (same 20 GB, more compute, 44 vs 422 queued jobs).
 - nibi: all MIG nodes draining for reboot; setup job has no start estimate.
 - hpc/multi watchers: pgrep -f over ssh self-matches; use audit job states instead.

## Platform decision (2026-11-07)
Four clusters tried for smoke runs; Fir/Rorqual/Narval completed, Nibi never started (nodes unavailable). User decision: the full live study runs on one cluster only (Fir, run am-20261107-060101); Narval/Rorqual only if a reviewer needs MBPP+/curate. Paper text added under Subjects ("Compute platform"). User first said "continue with 3", then clarified the full run is on one cluster; paper states what actually happened.

## Live study, Fir (2026-11-07)
- am-20261107-060101 (HumanEval+ x ExpeL-style, 25 cells, 100 runs): all 52 jobs OK. Processed -> results/processed/live/live-fir/ (raw symlink results/raw/live-fir).
  Key facts: 75 faulty runs; judges label root contaminated in 21/75; contamination beyond root in only 10/75; ~8 live artifacts/run, all memories/insights. H recall 1.0 (n=10), residual 0 vs 0.213 (none), suspends ~5.9/8 (precision 0.045, F1 0.479). R4 judge F1 0.647, HS_judge 0.670. H_noEME == H_noDeps == H in all 75 runs (ExpeL edits already source all insights). Judges kappa 0.987; 0/630 clean-run artifacts labelled contaminated. Engine 0.49 s vs evolution 234 s per run.
- Because the ExpeL slice cannot exercise EME/dependency edges, submitted HumanEval+ x curate on Fir (same H100 slice): am-20261107-080855 (config experiments.fir-curate.json).

## 2026-11-07 — Fir curate run am-20261107-080855: silent CPU fallback

- gen[0] (qwen2.5-coder:7b, curate, seed 0) failed three times (nodes fc10714, fc10910): every
  /api/generate call hit the 600 s client timeout. Cause: Ollama's GPU discovery on a fresh MIG
  slice exceeded its 30 s watchdog and Ollama silently fell back to CPU ("inference compute id=cpu").
- Same fallback in oracle[18] (gemma2:9b seed 3) and oracle[24] (granite3.3:8b seed 4); both
  finished on CPU with temperature-0 judges and were kept (disclosed). The ExpeL run
  am-20261107-060101 had no CPU fallback.
- Fix: hpc/slurm/hooks/ollama_common.sh restarts the server (up to 3 tries) until it reports a
  CUDA device, else fails the cell. Resubmitted gen/oracle/collect (jobs 2876676-8).

## 2026-11-07 — Curation slice processed; paper RQ1 completed

- Run am-20261107-080855 complete (25/25 gen, 25/25 oracle; gen[0] re-run on GPU after the hook fix).
  Linked as results/raw/live-fir-curate; `make live-fir` processes both slices.
- Closure recomputation validated against logged H and H_noEME: 75/75 runs in both slices (compared
  within the active revisions; superseded profiles are not suspended by the engine).
- Curation: 53/75 adopted, 42/75 propagated (90 contaminated: 43 profiles, 42 skills, 5 memories).
  H recall 1.00, residual 0; H ⊆ time cut in 75/75, strictly smaller in 42 (all 106 spared items
  are memories created before the first profile composition). EME needed in 1 run
  (llama3.1:8b F3 seed 3, m9). R3 missed contamination in 22/42 runs, R4 in 13/42.
- Correction: the reported "4.8% cross-process inference noise" (ExpeL) was prompt-ORDER sensitivity
  (same revisions, history order after revalidation). Identical contexts never flipped (0/4,709
  within, 0/58 across; curation 0/1,850 and 0/524). Order sensitivity: 30/579 (ExpeL), 6/343
  (curation). process.py now matches pairs on (task, context); earlier noise counts also double
  counted supplement remedies merged into rec["eval"].
- New summary block `structure` (contamination by kind, detector misses, closure vs cut, EME-only).
- p-value macros now include the relation ("=0.338" / "<0.001"), used as $p\Macro$.
- Paper: curation tables/figure/analysis, abstract, intro results, RQ1 answer, conclusion, lessons
  updated; running example tied to two real runs. Review round 4 launched.

## 2026-11-07 — Review round 4 and fixes

- Round 4: R1 major, R2 minor, R3 minor (all N3/R3/Rel4/V4, P3-4). reviews/round_4/.
- Revalidation now implemented as Algorithm 5 (src/heartness/revalidation.py; attestation revision as
  the source of re-admitted copies; dependencies remapped; P3 rejections). Curation supplements
  regenerated on Fir (job 2882647); originals kept as supplement_v1.json. HS_emb recall 0.68 -> 0.86.
- Experience withdrawal (State.tainted): re-derivation from a withdrawn experience refused (P2).
- Noise: "0 flips" was a cache artifact (R2). Now measured on byte-identical prompts generated in
  different run processes: ExpeL 178/4,349 (4.1%), curation 2/273. Order-sensitivity claim withdrawn.
- New post-hoc H_EMEfail (EME only from failed runs): curation recall 1.00, 17.24 suspended vs 20.79.
- Job hook restart-on-CPU verified in the rerun (cell 0: t1 cpu -> t2 CUDA).
