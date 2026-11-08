# Heartness delivery report — 2026-11-06

The project now contains an executable research prototype, reproducible experiments,
and a 12-page IEEEtran manuscript. The deliverable is an artifact-backed **bounded
feasibility study**, not a submission-ready claim of production effectiveness or
self-improvement.

Read the paper: [PDF](results/paper/heartness.pdf),
[source](docs/TSE/main.tex), [verified bibliography](docs/TSE/references.bib).
The original template inputs are preserved in `design/input-template/`.

## Implemented approach

HEARTNESS represents experience, proposals, immutable artifact revisions,
validation records, capability contracts, snapshots, deployment membership,
loaded runs and external effects. Transactional guards enforce admission;
recorded source/use graphs support origin and impact queries; withdrawal suspends
registered affected state; incompatible exact rollback is rejected. A host-owned
exposure adapter, observation-aware replay monitor, JSON CLI and conservative
recovery continuation make the lifecycle executable.

The independent SPIN model and Python BFS cover a finite lifecycle projection.
They do not encode the entire implementation or every property. `formal/SCOPE.md`
and the paper's property table state that boundary explicitly. Captured sources
mean generation exposure, not proven behavioral contribution. Quarantine is
permanent in this prototype; corrected state must have an independently justified
fresh lineage, or await a future controlled revalidation design.

## Verified results

The selected main campaign is
`results/raw/campaign-20261106T210441873255Z/` with **1,905** records. It has 15 main
experiments in 16 directories; E12 public-file replay is a separate deterministic
supplement. The finalizer failed after all measurements because a local variable
shadowed the campaign path. The error and repaired finalizer are retained in
`completion_provenance.json`; no raw measurements were overwritten or changed.
Earlier campaigns remain available and are excluded from revised summaries.

- Main traceability: **810** scenarios across nine structural motif labels, three
  sizes and thirty paired seeds. Full-capture impact F1 **1.000**, tying capture-only.
  Within-file history: **0.155**; fixed-threshold lexical recovery: **0.699**.
  These controls differ in available lineage information, not merely algorithms.
- Incomplete capture: impact F1 **0.572** at half derivation capture, **0.103** at
  zero derivation capture. Known use edges and anchors remain available.
- Finite checking: **18/18** Python/SPIN verdict agreements; **13** seeded violating
  configurations, all witnesses replay and pass shorter-depth minimality checks.
  Two edge-free guard removals survive as negative controls.
- Reference correspondence: **3,000** attempted mapped transitions, **992** enabled,
  **zero** mismatches at two identities/depth six. One shortest engine history per
  projected state is retained. This is finite evidence, not a refinement proof.
- B3 direct-edge linter: affected-set F1 **0.229** on 90 constructed post-withdrawal
  graph states; zero alarms on 90 benign controls. Full capture can report the
  closure, while the controller additionally prevents or contains transitions.
- Observation monitor: **30/30** observed-drift and **30/30** invalid-event cases
  flagged; **29/30** omissions flagged; **0/30** hidden external actions detected.
  Wilson intervals are conditional on sampled positions in one synthetic fixture.
- Full controller costs at 32 artifacts: guarded workload **1.137 s**, replay
  **2.968 s**, withdrawal **22.9 ms**, under Python allocation tracing. These are
  absolute prototype costs, not production overhead percentages or graph timings.
- Public replay: **12** actual Voyager file revisions through **36** events, no
  conformance findings. Imported JavaScript is not executed; autonomous synthesis
  provenance and real agent effectiveness are not evaluated.
- Validation: **38 tests pass**; ruff and strict mypy pass; **99.1%** statement and
  **96.7%** branch coverage; **12/12** targeted hand-authored source mutants killed.
  The mutation campaign is not exhaustive mutation analysis.

Evidence: `results/processed/summary.json`, `trace_metrics.csv`,
`statistical_tests.csv`, `factor_analysis.csv`, `exact_origins.csv`,
`runtime_cost.csv`, `paper_macro_index.json`; `results/validation/coverage.json`,
`mutation_selection.json`, and `artifact_audit.json`.
The full raw-to-paper mapping is `experiments/EXPERIMENT_INDEX.md`.

## Research reading and reviews

`design/research_reading.md` records primary TSE/ICSE sources and how their evidence
structures informed the evaluation. Entries from the supplied related-work list
were verified rather than copied with potentially incorrect years. The excluded
local manuscripts are not cited in the paper.

Three independent agent contexts reviewed the actual paper, implementation and
results in two rounds. All initially requested major revision; substantive fixes
included source-existence and deployment semantics, state-mapping checks, meaningful
benchmark factors, measured linter comparison, targeted property challenges,
controller costs, capture boundaries and saved-history CLI behavior. All three
round-two reports had **no remaining major concerns for the bounded claims** and
recommended minor revision. Minor corrections were applied and mapped in
`reviews/round_2/response.md`. This is automated internal review, not human peer
review, evidence of practitioner validation, or TSE acceptance.

## Reproduce

```bash
make setup
make test
make mutation
make experiments
make realistic
make results
make paper
.venv/bin/python scripts/verify_artifact.py
```

`make all` runs the test/mutation/experiment/bundled-replay/results/paper stages.
No GPU or model API credentials are required. Setup needs network access for pinned
Python dependencies and SPIN. Public replay uses the exact bundled content offline.
The generated build PDF is `build/paper/main.pdf`; the delivered copy is
`results/paper/heartness.pdf`. A fresh experiment run creates a new campaign, never
replacing raw files. Timings and wall-clock-budget search counts vary across hosts.

## Unfulfilled broader aspirations / remaining evidence

These items are deliberately **not** represented as completed by the limited paper:

- Complete mature-checker coverage of all full-model operators and P1–P10;
  the independent encoding is a documented projection with five projected checks.
- Unbounded implementation refinement, authenticated complete observation, or
  reliable capture of every source in a deployed autonomous generator.
- Behavioral culprit-revision top-k accuracy, causal source attribution, or
  measured agent-task improvement. First installation is only a diagnostic label.
- Large-scale transactional persistence, distributed acknowledgments, disconnected
  client withdrawal, in-flight cancellation, semantic contract correctness, or
  controlled rehabilitation of quarantined descendants.
- Independent human benchmark annotation, practitioner diagnosis benefit, a
  multi-harness operational study, and competitive tuned Git/embedding recovery.
- A public archival DOI and author/affiliation confirmation for submission.

The benchmark's old random audit is explicitly an approach-oracle agreement check.
Hand-specified expected cases supply additional algorithm-independent controls,
including empty and deployment-only impact, but do not supply independent human
validation. These limitations are substantive research boundaries, not cured by
more synthetic seeds or automated reviewer convergence.

## Definition-of-done audit

- [x] Idea-to-component/test/experiment/paper matrix written, including explicit unmeasured tasks.
- [x] Implementation and CLI work; required tests, lint, typing, coverage and targeted mutation reported.
- [x] Independent SPIN encoding built and differential verdicts agree **within its documented projection**.
- [x] Versioned benchmark, datasheet, construction oracle and independent hand-worked controls supplied.
- [x] B0–B3, capture-only control, component/property challenges and more than ten campaigns executed with raw and processed records.
- [x] Measured manuscript numbers and plots mapped to immutable raw records and generation scripts.
- [x] Six-section IEEEtran manuscript, recurring example, overview, formal definitions, algorithms and three explicit RQ answers supplied.
- [x] Bibliography entries verified; twelve used citation keys resolve.
- [x] PDF compiles; no undefined citations/references or overfull boxes. Template lettersize and underfull-box warnings are nonfatal.
- [x] Three-reviewer exercise completed for two full rounds; responses and applied fixes recorded.
- [x] Incomplete provenance, correspondence, causality and irreversible-effect limits stated.
- [x] Final report and reproduction commands supplied.
- [ ] Full original research ambition validated beyond the bounded prototype: the broader evidence items listed above remain open.
