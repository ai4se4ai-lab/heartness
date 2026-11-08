# MASTER PROMPT: Traceable Self-Evolving AI Harnesses via MDE + Model Checking
# (implement -> test -> benchmark -> experiment -> write IEEE TSE paper -> 3-reviewer loop)

---

## 0. ROLE AND OPERATING RULES

You are a senior research software engineer and academic author. You will carry out an
entire research project end to end: design and implement an approach, test it rigorously,
build a benchmark, run many experiments, and write a journal paper for **IEEE Transactions
on Software Engineering (TSE)**. You work autonomously, but you follow these rules:

1. **Honesty over appeal.** Report results exactly as measured. Report negative and null
   results. Never fabricate data, citations, numbers, or experimental outcomes. If something
   was not run, say so.
2. **No invented references.** Cite only works that appear in `docs/work/` (or that you can
   verify with certainty). Every `\cite{}` key must exist in `references.bib`. If a needed
   reference is missing, add a `% TODO: verify` comment in the bib and tell me in the final
   report rather than guessing metadata.
3. **Reproducibility.** Fixed seeds, pinned dependencies, one-command re-run scripts, and
   every number in the paper traceable to a raw file under `results/`.
4. **Scope claims carefully.** `idea.md` itself says formal methods and model checking do NOT
   guarantee complete provenance or correct runtime behavior, and do not recover missing
   history or reverse external effects. The paper must inherit these limits and state them
   as threats/limitations, not hide them.
5. **Work in iterations**, keep a `PROJECT_LOG.md` (decisions, failures, fixes, reviewer
   feedback and how each item was addressed).
6. There is **no page limit**; favor completeness, clarity and rigor over brevity.

---

## 1. INPUTS

| Path | Purpose |
|---|---|
| `idea.md` | The approach to implement (read it fully first). It frames the traceability problem of self-evolving harnesses and proposes formal methods + MDE + model checking as a direction. It is high-level: you must turn it into a concrete, implementable, evaluable approach. |
| `harness-self-evolution.md` (if present) | Source document the idea is grounded in (Sections 2, 6, 8.5, 9.2, 9.7). Use its terminology. |
| `docs/work/` | Related work + material for the Background and Related Work sections. Read ALL of it before designing the paper outline. |
| `docs/TSE/main.tex` | The IEEE TSE LaTeX template. Follow it exactly (class, packages, author block, bibliography style). |

Output layout (create it):

```
project/
  PROJECT_LOG.md
  README.md                 # how to reproduce everything with single commands
  src/                      # implementation
  tests/                    # unit, property-based, mutation, integration tests
  benchmark/                # generator, scenarios, ground truth, schema, docs
  experiments/              # experiment runners + configs (one per RQ/experiment)
  results/
    raw/                    # untouched raw outputs per run (JSONL/CSV/logs/counterexamples)
    processed/              # aggregated tables, stats, figure data
    figures/                # generated plots (also used by the paper)
  reviews/                  # reviewer reports per round + response-to-reviewers
  docs/TSE/
    main.tex                # ALL paper text lives here (single file)
    references.bib          # ONLY other paper file
```

**Paper deliverable constraint: exactly two LaTeX-side files: `main.tex` and
`references.bib`.** Everything in the paper (diagrams, tables, pseudocode, plots) must be
inline in `main.tex` (TikZ/PGFPlots/algorithm environments; plots from CSV may be embedded
via `pgfplotstable` data pasted inline, or drawn in TikZ). Do not depend on external image
files for the final paper.

---

## 2. PHASE A: DEEP READING AND PROBLEM FORMALIZATION

1. Read `idea.md` and the related material. Produce `design/problem_analysis.md` capturing:
   - The definition of a self-evolving harness: persistent revisions to instructions,
     memory, skills, workflows, tool orchestration, agent coordination, executable
     components, loaded by later runs.
   - The traceability problem: experience -> modification -> artifact -> derived artifacts
     -> harness versions; copying/summarizing/merging of lessons; original artifact edited
     or withdrawn while derivatives stay active; multi-source synthesis not recoverable by
     file history or textual similarity.
   - Consequences: which experience motivated a change; which revision introduced a
     regression; which components depend on a problematic artifact; which earlier state to
     restore; causal contribution of an update vs. mere record of what state operated;
     cross-deployment reuse; rollback does not undo external effects.
2. Turn this into a precise **research problem statement** with 4-6 concrete *tasks* the
   approach must support (e.g., origin tracing, impact analysis, withdrawal closure,
   consistency preservation, rollback target selection).

---

## 3. PHASE B: DESIGN THE APPROACH (make it concrete, novel, and checkable)

Design a named approach (give it a memorable name and acronym) with these components. You
may refine them, but every idea in `idea.md` must be covered and tied to a component.

### B1. Harness Evolution Metamodel (MDE layer)
- Metaclasses: `Experience`(run/trace, outcome, task), `Proposal`/`Modification`
  (produced by a *policy*), `Artifact` with subtypes `Memory`, `Skill`, `Prompt/Instruction`,
  `Workflow`, `ToolConfig`, `AgentConfig`, `ExecutableComponent`; `HarnessVersion`
  (a snapshot of active artifacts), `Deployment`, `Contract` (assumes/guarantees),
  `ValidationRecord`, `ExternalEffect` (recorded but explicitly *not reversible by rollback*).
- Relations: `motivatedBy` (Modification -> Experience), `produces/edits/removes`
  (Modification -> Artifact), `derivedFrom` (Artifact -> Artifact, many-to-many, with
  derivation kind: copy | summary | transform | merge/synthesis), `dependsOn`/`uses`
  (Artifact -> Artifact, Agent -> Skill...), `activeIn` (Artifact -> HarnessVersion/
  Deployment), `loadedBy` (Version -> Run), `validates` (Record -> candidate).
- Statuses: `candidate | accepted | active | withdrawn | quarantined`.
- Make **state and permitted transitions independent of the policy that proposes changes**
  (explicit requirement in `idea.md`): the policy (LLM or heuristic) only proposes; the
  transition system decides admissibility.
- Provide the metamodel as an Ecore-like/UML-like spec AND a machine-readable schema
  (JSON Schema or Python dataclasses/pydantic) used by the implementation.

### B2. Evolution as Model Transformations
- Define a closed set of **transformation operators** over the model:
  `Propose`, `Validate`, `Accept(candidate -> new version)`, `Derive(a, sources, kind)`,
  `Edit`, `Merge`, `Withdraw`, `Quarantine`, `Rollback(to version)`, `Deploy/Reuse`.
- Each operator has formal pre/postconditions (guards) and a trace-link side effect.
  Distinguish **records of what state operated** (observational) from **evidence of causal
  contribution of an update** (kept separate; do not conflate; the paper should treat
  causal contribution as an *estimable annotation*, not a proven fact).

### B3. Provenance Graph and Trace Capture
- Build a typed provenance graph (PROV-inspired) updated by each transformation.
- Capture modes (these are evaluated as experimental factors because `idea.md` stresses
  that provenance may be incomplete):
  (i) full structured capture at transformation time,
  (ii) partial capture (drop a configurable fraction of derivation edges),
  (iii) no capture + **recovery heuristics** from text/file history (e.g., lexical/embedding
  similarity), as the realistic baseline.
- Provide queries: `originOf(a)`, `descendants(a)` (transitive closure over `derivedFrom`),
  `activeDependents(a)`, `impactSet(withdraw a)`, `lastGoodVersion(a)`, `whichRevisionIntroduced(failure)`.

### B4. Contracts and Compositional Consistency
- Lightweight assume/guarantee contracts on skills/agents/workflows (input
  assumptions, output guarantees, validity conditions for reuse). Define a dependency
  consistency check: when artifact `a` changes, every consumer's assumptions must still be
  satisfied or be flagged `stale`.
- Distinguish *origin* of an artifact from *conditions under which it is valid to reuse*.

### B5. Formal Properties (the checkable specification)
Express in LTL/CTL (and equivalent invariants/predicates in the implementation language).
Minimum set, each with a unique ID (P1..Pn) and a plain-English reading:
- **P1 History:** every persistent artifact has a non-empty, well-formed history reaching
  an experience or an authorized seed.
- **P2 Withdrawal closure:** if a source is withdrawn, no active artifact has it in its
  transitive derivation closure without being quarantined/re-validated (the "no active
  derivative of a withdrawn source" property from `idea.md`).
- **P3 Dependency consistency:** active consumers' contracts hold w.r.t. current
  producers (no stale dependents).
- **P4 Candidate-to-version fidelity:** the version loaded after `Accept` equals the
  validated candidate (no drift between validated and deployed content).
- **P5 Rollback soundness:** after `Rollback`, active set = recorded snapshot; derived
  artifacts created after the target version are inactive; external effects are *flagged*,
  never claimed undone.
- **P6 Acyclicity/well-formedness of derivation**, **P7 monotone history** (no history
  deletion), **P8 Reuse propagation:** reused artifacts across deployments remain
  linked so withdrawal reaches all deployments.
Add 2-3 further properties you judge valuable. State which properties are safety vs.
liveness and which need bounded checking.

### B6. Model Checking Component
- Encode the transition system and run exhaustive/bounded model checking over all
  sequences of operators up to depth k on small scopes (artifact count, versions,
  deployments). Choose a real tool and justify (e.g., TLA+/TLC, Alloy, NuSMV/nuXmv,
  Spin, or Python explicit-state/BFS with an independent implementation). Preferred:
  an **independent encoding in a mature checker** PLUS the Python implementation, so the
  two can be cross-validated (differential testing).
- Generate **counterexample traces** and automatically translate them into readable
  evolution scenarios (sequence of operators) reproducible in the implementation.
- Check two kinds of models: (a) the **reference transition system** (does the
  specification itself admit violating sequences? find spec bugs), and (b) a
  **harness-under-test model** built from observed traces (does the real/simulated harness
  violate P1-Pn?).

### B7. Model <-> Implementation Correspondence (do not skip: `idea.md` calls it open)
- Implement a **runtime conformance monitor** that replays logged harness events against
  the model's transition rules and flags deviations (trace conformance checking).
- Quantify the correspondence gap in the evaluation (e.g., rate of events the model
  rejects, undetected-by-model violations injected at the implementation level).

### B8. Policy-agnostic Harness Simulator + (optional) LLM policies
- Build a **self-evolving harness simulator**: tasks -> runs -> experiences -> proposals ->
  accept/reject -> new versions, with synthetic but realistic artifacts (skills, memories,
  prompts, workflows, agents).
- Policies: (1) scripted/stochastic policy (reproducible, default for the main
  experiments), (2) optionally, an LLM-driven policy through a pluggable adapter. If the
  LLM is used, record model name/version, prompts, temperature, seeds, raw responses; run
  repeated trials and report variance. Keep the core claims valid under the deterministic
  policy so that results are reproducible without API access.

### B9. Developer-facing interface
- CLI + library: `trace`, `impact`, `withdraw --dry-run`, `check`, `rollback-plan`,
  `monitor`, `export-model`. Withdrawal must output the **affected active state** and a
  remediation plan, including a list of external effects that remain unreversed.

---

## 4. PHASE C: IMPLEMENTATION AND RIGOROUS TESTING

- Language: Python 3.11+ (type hints, pydantic/dataclasses, networkx or custom graph).
  Pin dependencies; provide `requirements.txt`/lockfile. Follow clean-code practice
  (small functions, no dead code, docstrings, linting with ruff + mypy clean).
- **Testing pyramid (all must exist and pass; report coverage):**
  1. Unit tests for every operator (guards, postconditions, trace-link effects).
  2. **Property-based tests** (Hypothesis): random operator sequences must preserve
     P1..Pn when guards are respected; adversarial sequences must be rejected or flagged.
  3. **Differential tests:** Python engine vs. the independent model-checker encoding
     on identical scenarios (they must agree on property verdicts; investigate and fix
     any disagreement).
  4. **Mutation testing** (e.g., mutmut/cosmic-ray) on the guards and graph queries; report
     mutation score and kill the survivors that matter.
  5. **Fault injection into the model checker's inputs**: deliberately weaken a guard and
     verify the checker produces a counterexample (the checker can actually fail).
  6. Integration/end-to-end tests of the running example (see 8).
  7. Determinism tests: same seed -> byte-identical raw outputs.
- Target >= 90% line and branch coverage on core modules; document anything excluded.
- CI-style script `make test` / `./run_tests.sh`.

---

## 5. PHASE D: BENCHMARK

Build **a benchmark of evolving-harness scenarios with ground truth** (name it, version
it, document it with a datasheet: purpose, generation process, schema, limitations).

- **Generator** parameterized by: number of experiences, artifacts, versions, deployments,
  derivation fan-out/depth, share of synthesis (multi-source) derivations, edit/withdrawal
  frequency, reuse across deployments, provenance-capture completeness, noise level, and
  seed. Scales: small (exhaustively model-checkable), medium, large (stress).
- **Scenario families** (each with injected ground-truth labels):
  1. *Faulty lesson propagation:* incorrect memory entry -> copied/summarized into skills ->
     reused in agent configs (the `idea.md` example). Truth: full derivative closure.
  2. *Source deleted/edited while derivatives live.*
  3. *Multi-source synthesis* where influence is not recoverable from textual similarity
     (include paraphrase and lossy summarization to defeat lexical baselines).
  4. *Regression introduced by a specific revision;* truth = culprit revision.
  5. *Cross-deployment reuse* of a problematic artifact.
  6. *Stale dependency* after a producer change (contract violation).
  7. *Rollback with external effects* (truth: which effects remain).
  8. *Benign evolution* (no faults) to measure false positives.
  9. *Adversarial/corner cases:* cyclic derivation attempts, concurrent proposals
     against shared state, re-activation of withdrawn artifacts, validated-vs-loaded drift.
- Ground truth must come from the generator's construction (not from the tool under test).
  Include a **validation of the benchmark itself** (sanity checks, manual audit of a random
  sample, independence of oracle from approach).
- Where feasible, add a small **realistic set** by instrumenting or replaying public
  agent-harness artifacts (e.g., skill/memory/config files from open-source agent
  projects, with real git histories) to test beyond synthetic data; clearly label the
  limits of its ground truth.

---

## 6. PHASE E: EXPERIMENTS (run many; record raw + processed)

**Baselines (must include):**
- B0: *file/git history only* (git log/blame style lineage).
- B1: *textual-similarity recovery* (TF-IDF/embedding/n-gram overlap + threshold) of
  derivations without captured provenance.
- B2: *Provenance capture without formal checking* (graph queries only, no model
  checking, no contracts).
- B3: *Ad hoc rule-based linter* (hand-written checks of common failure patterns).
- Optional B4: *LLM-as-analyst* reading the artifacts/history and answering the same
  questions (record prompts/responses; multiple trials).
- Ours: full approach + ablations (no contracts; no model checking; no conformance monitor;
  partial provenance capture; each property removed).

**Research questions (use these three unless the related-work reading reveals three
stronger ones; they must be interesting, answerable, and each tied to experiments):**
- **RQ1 (Effectiveness on traceability tasks):** How accurately does the approach recover
  origins, descendants, active dependents and withdrawal impact sets compared with
  file-history, similarity-based, and capture-only baselines, and how does accuracy degrade
  with incomplete provenance capture?
- **RQ2 (Defect/violation detection by model checking):** Can model checking over the
  evolution model find violations of the provenance/consistency properties (including
  seeded faults and spec-level bugs) that testing, linting and baselines miss, and how
  informative/minimal are the counterexamples for diagnosis and rollback selection?
- **RQ3 (Scalability and practicality, incl. model-implementation correspondence):** What
  are the cost, scalability limits (state space, runtime, memory) and overhead of capture,
  monitoring and checking, and how well does the conformance monitor close the gap between
  the abstract model and the executing harness?

For each RQ define: objective, hypothesis (stated before running), independent/dependent
variables, metrics, number of runs/seeds, statistical analysis.

**Metrics:** precision/recall/F1 and Jaccard of impact/descendant sets; exact-match of
origin; culprit-revision top-1/top-k; violation detection rate, false-positive rate on
benign scenarios; counterexample length/minimality; time-to-diagnosis proxies (steps
needed); runtime, peak memory, states explored, model-checking depth reached; overhead of
capture/monitoring (% time); conformance deviation rate.

**Statistics:** >= 30 seeds per configuration where stochastic; report mean +/- 95% CI
(bootstrap); non-parametric tests (Wilcoxon signed-rank/Mann-Whitney) with effect sizes
(Cliff's delta / Vargha-Delaney A12); multiple-comparison correction (Holm). No
cherry-picking: report all configurations run.

**Experiments to include at minimum:**
1. Traceability accuracy vs. baselines across scenario families and sizes.
2. Sensitivity to provenance completeness (100% -> 0% edge capture) and paraphrase level.
3. Ablation study of every component and every property.
4. Model-checking campaign: exhaustive small-scope checking of the reference spec
   (find and report spec bugs); seeded-fault detection; comparison against random testing
   and property-based fuzzing with equal time budgets.
5. Counterexample quality study (length, shrinkage, and whether replaying it in the
   implementation reproduces the failure).
6. Withdrawal-and-rollback study including unreversible external effects (verify the tool
   never claims to undo them).
7. Scalability sweep (artifacts, versions, fan-out, deployments) with time/memory/state
   counts and the point where checking becomes infeasible; show what the bounded
   abstraction/slicing (e.g., checking only the relevant cone of influence) buys.
8. Conformance-monitor experiment: inject implementation-level deviations that the model
   alone cannot see; measure detection.
9. (Optional) Realistic-data replay and LLM-policy runs with variance reporting.
10. Threat-driven robustness checks (different seeds, generator parameter perturbation,
    leave-one-family-out).

**Recording requirements:**
- `results/raw/<experiment>/<config>/<seed>/` containing: input scenario, ground truth,
  tool outputs, logs, counterexamples, timing/memory, environment info (versions, CPU,
  OS), config hash, git commit. Never overwrite raw files.
- `results/processed/`: tidy CSVs per experiment, a `summary.json`, statistical-test
  tables, and figure-ready data. Provide `make results` to regenerate processed files and
  figures from raw.
- Keep an `experiments/EXPERIMENT_INDEX.md` mapping every paper figure/table/number to
  its raw files and the script generating it.

---

## 7. PHASE F: THE PAPER (IEEE TSE) - `docs/TSE/main.tex` + `references.bib` ONLY

Follow `docs/TSE/main.tex` template conventions strictly. Write in precise,
reader-friendly academic English aimed at a **software-engineering PhD student**. Before
every new concept or definition, put 2-4 sentences motivating *why* it is needed; after it,
anchor it to the running example. Define terms once and use them consistently. Use
`\label`/`\ref` throughout; numbered definitions, properties and research questions.

### Section 1 - Introduction (in this order)
1. Motivate the study (self-evolving AI harnesses are becoming persistent, cumulative
   software; their behavior depends on histories of experience and modification).
2. Problems with the current state of the art (history is recorded but derivation across
   synthesis/reuse is unrecoverable; withdrawal does not reach derivatives; rollback
   limits; recorded state vs. causal contribution; no formal account of permitted
   transitions independent of the proposing policy). Support with citations from
   `docs/work`.
3. The approach at a very high level: its components and how they interact (no details).
4. A brief summary of experimental results with the *actual headline numbers*
   (taken from processed results).
5. Contributions (numbered, specific, verifiable).
6. Three research questions (RQ1-RQ3 as in Section 6, adjusted if justified).
7. Paper organization paragraph and artifact availability statement (link placeholder).

### Section 2 - Background
Read `docs/work` first to decide the subsections; a likely set (adapt):
self-evolving agents/harness; provenance and traceability (PROV, software traceability);
model-driven engineering (metamodels, model transformations, trace links); formal
specification and temporal logic; model checking (explicit-state/bounded, counterexamples);
contracts and compositional reasoning. Close with a **running example** (a small
self-evolving harness: e.g., a coding-assistant harness whose memory gets an incorrect
lesson that is summarized into a skill and reused by two agents in two deployments, later
withdrawn). Include a figure (TikZ) of the example's evolution and use it for ALL later
definitions and algorithm walk-throughs. Pre-announce the running-example IDs
(experience e1, memory m1, skill s1, agents a1/a2, versions v0..v4, ...).

### Section 3 - Approach
- **3.1 Overview:** a TikZ **overview diagram** showing components, sub-components and
  annotated links (what data/artifact flows between them, labeled), plus a narrative
  walk-through; list assumptions and the problem statement.
- 3.2+ one subsection per component (metamodel; transformations; provenance capture and
  queries; contracts; properties; model checking; conformance monitor; policy-agnostic
  simulator/CLI). Each subsection: motivation -> formal definition (concise) -> **simple,
  readable pseudocode** (algorithm environment, <= ~15 lines each, no dense notation) ->
  step-by-step application to the running example.
- Include a subsection on **guarantees and limits** (what is and is not guaranteed; link
  to the unresolved correspondence/causality/external-effects issues).

### Section 4 - Evaluation
- 4.1 Implementation (languages, tools, sizes, architecture, tool versions, availability).
- 4.2 Experimental setup (benchmark description + datasheet summary, baselines,
  metrics, statistical methods, hardware/software environment, seeds, protocol).
- 4.3 Description of each experiment: objective, how it works, parameters.
- 4.4 RQ1 / 4.5 RQ2 / 4.6 RQ3 (each: results with tables/plots, statistical analysis,
  explicit answer in a boxed/bold "Answer to RQ" statement, and discussion of
  surprising or negative findings).
- 4.7 Threats to validity (construct, internal, external, conclusion; synthetic-data
  threat; oracle independence; model-implementation gap; LLM nondeterminism).
- 4.8 Discussion/lessons learned and limitations.

### Section 5 - Related Work
Group the related work from `docs/work` into ~4-6 groups (e.g., self-evolving/agentic
harnesses; software traceability and provenance; MDE/model versioning and trace links;
formal verification/model checking of software evolution and ML/agent systems; runtime
verification and conformance checking; governance/auditing of AI systems). For each group:
summarize, then **compare explicitly with our work** (what they do, what they lack for this
problem, how we differ). End with a short positioning table.

### Section 6 - Conclusion and Future Work.

**Quality bar for TSE:** problem clarity, precise contributions, sound methodology,
complete evaluation, honest limitations, artifact statement. Include: all tables with
captions that explain the takeaway, consistent notation table, algorithm floats, TikZ
figures readable in grayscale, bibliography via `references.bib` (IEEEtran style as given by
the template). The LaTeX must compile cleanly (`latexmk`), without undefined references or
overfull-box disasters. Report compile status.

---

## 8. PHASE G: THREE-REVIEWER LOOP (mandatory, >= 2 full rounds, until convergence)

Spawn **three independent reviewer agents** (separate contexts, different personas, each
told to be critical, specific and fair, and to ground comments in the actual manuscript,
code and result files):

- **Reviewer 1 - Methodologist / Formal methods expert:** soundness of formalization,
  property definitions, model-checking encoding, correspondence claims.
- **Reviewer 2 - Empirical SE expert:** benchmark validity, baselines, statistics,
  threats, reproducibility, whether claims are supported by data.
- **Reviewer 3 - Practitioner / AI-agent systems expert:** relevance, practicality,
  realism of scenarios, clarity for readers, related work completeness.

Each reviewer scores and comments on the **TSE criteria**:
1. **Novelty** - novelty and innovativeness of solutions, problem formulations,
   methodologies, theories and/or evaluations relative to the state of the art.
2. **Rigor** - soundness, clarity and depth of the technical/theoretical contribution;
   thoroughness and completeness of the evaluation.
3. **Relevance** - significance/potential impact on software engineering.
4. **Verifiability and Transparency** - enough information to understand how the
   innovation works, how data was obtained/analyzed/interpreted, and to support
   independent verification/replication; artifacts attached or linked will be checked.
5. **Presentation** - clarity of the exposition.

Reviewer output format: summary; score 1-5 per criterion with justification; major
concerns (numbered, with the required action); minor issues; questions for the authors;
recommendation (accept / minor / major revision / reject).

**After each round:** write `reviews/round_N/` reports and `reviews/round_N/response.md`
mapping every comment to an action: *implementation fix*, *new/changed experiment*,
*paper edit*, or *rebuttal with justification*. Actually perform the actions (re-run
experiments, regenerate processed results, update the paper numbers and text). Then run
the next round on the revised version. Stop when no reviewer raises a major concern or
after 4 rounds; list any unresolved concerns honestly in the final report.

---

## 9. DEFINITION OF DONE (checklist - verify each and print it at the end)

- [ ] `idea.md` fully mapped to components (traceability matrix idea-claim -> design -> test -> experiment -> paper section).
- [ ] Implementation + CLI work; `make test` passes; coverage + mutation score reported.
- [ ] Independent model-checker encoding built; differential tests agree.
- [ ] Benchmark generated, documented, validated, ground truth independent of the tool.
- [ ] All baselines + ablations + >= 10 experiments run with fixed seeds; raw + processed saved.
- [ ] Every number/figure/table in the paper traceable via `EXPERIMENT_INDEX.md`.
- [ ] `main.tex` follows the template, all five sections complete, running example used throughout, overview diagram present, pseudocode simple, 3 RQs answered explicitly.
- [ ] `references.bib` contains only verified entries; no undefined citations.
- [ ] Paper compiles without errors.
- [ ] Three-reviewer loop completed, responses documented, revisions applied.
- [ ] Limitations from `idea.md` (no guaranteed complete provenance, abstract-model vs implementation gap, causal contribution vs recorded state, external effects not reversible) stated in the paper.
- [ ] Final report: what was done, headline results, unresolved issues, how to reproduce.

Begin with Phase A. After each phase, summarize what you did and any decision you made,
then continue to the next phase without waiting for me unless you are blocked.
