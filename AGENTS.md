# AGENTS.md — how to work in this repository

Heartness = traceable state evolution and **withdrawal** for self-evolving AI harnesses.
Python prototype + live LLM study on Alliance Canada HPC clusters + synthetic benchmark +
SPIN model + the TSE manuscript. Human-facing docs: `README.md`. Chronology of decisions
and failures: `PROJECT_LOG.md` (read the tail before changing anything about results).

## 60-second orientation

| Path | What it is |
|---|---|
| `src/heartness/` | The approach. `model.py` (immutable revisions), `engine.py` (guarded admit/withdraw/rollback), `graph.py` (exposure closure incl. experience-mediated edges), `capture.py` (host exposure capture), `properties.py` (audit predicates P1-P10), `revalidation.py`, `monitor.py`, `checker.py` (finite BFS + Promela), `cli.py` |
| `tests/` | pytest suite (branch-coverage gate in `scripts/check_coverage.py`) |
| `benchmark/` | S2 synthetic generator (EvoTraceBench), `DATASHEET.md` |
| `experiments/` | `run.py` synthetic campaign, `process.py`, `realistic.py` (Voyager replay); `experiments/live/` = S1 live harness (`cell.py` one HPC cell, `process.py` analysis, `llm.py` cache, `harness.py`, `tasks.py`) |
| `formal/` | SPIN scope doc; SPIN built by `scripts/install_spin.sh` |
| `hpc/` | Slurm pipeline for one cluster (`slurm/submit.py`, `scripts/audit.py`, `config/experiments*.json`, `config/cluster.env`) |
| `hpc/multi/` | Drive four clusters from the workstation (`connect.sh`, `sync.sh`, `stage.sh`, `submit.sh`, `fetch.sh`, `status.py`, `clusters.tsv`, `runs.tsv` ledger) |
| `results/raw/` | **Immutable** raw campaigns and LLM caches. Never edit or delete. `results/raw/hpc/<cluster>/<RUN_ID>/` = fetched cluster runs; `live-fir*` are symlinks into them |
| `results/processed/` | Derived tables/summaries, regenerable |
| `docs/TSE/main.tex` | The paper. Single inline source + `references.bib` |
| `scripts/paper_macros.py` | Generates the `BEGIN/END GENERATED MACROS` block in `main.tex` from processed results |
| `design/`, `reviews/`, `FINAL_REPORT.md` | Rationale, automated review rounds, completion status |

## Setup and the standard loop

```bash
make setup                  # .venv, requirements.lock, editable install, SPIN
make test                   # ruff + mypy --strict + pytest with coverage gate (must pass)
make mutation               # all hand-seeded guard mutants must be killed
make experiments results    # synthetic campaign -> processed results (new immutable campaign each time)
make live-fir               # re-derive live tables from shipped records + caches (CPU only)
make validate macros paper  # -> build/paper/main.pdf
```

Use `.venv/bin/python` (the Makefile's `PYTHON`). Live code needs `PYTHONPATH=src`.
Python 3.11+, ruff line length 100, mypy strict on `src/heartness`.

## Rules that matter here

1. **Never hand-edit numbers in the paper.** Numbers come from `scripts/paper_macros.py`
   (`paper_macro_index.json` maps each to its source). Change data/analysis, rerun
   `make live-fir` (or `make results macros`), then `make paper`. Prose in `main.tex` outside
   the generated block is editable; keep claims consistent with the macros.
2. **Raw results are append-only.** Do not modify `results/raw/**`. Superseded campaigns stay.
   `make experiments` creates a new campaign instead of overwriting.
3. **Claims discipline.** Source IDs = recorded generation *exposure*, not causal effect.
   The study shows containment and traceability, not better agent task outcomes or production
   readiness. Smoke runs are never findings. Keep `README.md`, `FINAL_REPORT.md` and the paper
   consistent when scope changes. Do not cite or discuss review status of `docs/work/under-review-work`.
4. **Do not edit** `docs/PROMPT.md` (user prompt) or `design/input-template/`.
5. **Cluster actions cost allocation and are outward-facing.** `sync.sh` runs `rsync --delete`
   on the remote repo dir; `submit.sh --full` spends GPU hours. Ask the user before any
   `--full` submit, `scancel`, deleting remote state, or syncing to a cluster. Read-only
   commands (`connect.sh --check`, `status.py`, `stage.sh --check`, `submit.sh --dry-run`) are safe.
6. **Generated solutions execute code** (temp dir + timeout, no network isolation). Do not run
   live harness cells on a machine you care about; the cluster jobs are the intended place.
7. **Do not commit** unless asked. `build/`, `.venv/`, `hpc/logs/`, LaTeX aux files are gitignored.
   No secrets exist in the repo; never add credentials or print the SSH ControlPath sockets.

## Working with the HPC clusters

Clusters live in `hpc/multi/clusters.tsv` (nibi, narval, fir, rorqual). Remote user is
`$HPC_USER` (default `mbabaei`). **The paper's reported live study ran on Fir only** (two
slices: HumanEval+ x ExpeL `am-20261107-060101`, HumanEval+ x curate `am-20261107-080855`);
other clusters were smoke-tested. Run IDs are recorded in `hpc/multi/runs.tsv`.

Connections need MFA, so an agent usually **cannot** open them: if `status.py` says
"not connected", ask the user to run `bash hpc/multi/connect.sh <cluster>` and approve MFA.

Check status (read-only, safe to run any time):

```bash
bash hpc/multi/connect.sh --check
python3 hpc/multi/status.py --kind full --clusters fir   # latest full run on Fir
python3 hpc/multi/status.py --only failed                # failures with reasons/log tails
python3 hpc/multi/status.py --watch 300                  # minimum 120 s
```

Lifecycle (details with expected output in `README.md`, reference in `hpc/multi/README.md`):
`connect.sh` -> `sync.sh <c>` -> `stage.sh <c>` (+ `--check`) -> `submit.sh --dry-run <c>` ->
`submit.sh --smoke <c>` -> check smoke with `status.py --kind smoke` -> `submit.sh --full <c>`
(ask first) -> `status.py` -> repair with `submit.sh --full <c> -- --run-id <ID> --only <stage>` ->
`fetch.sh <c>` -> symlink `results/raw/live-fir[-curate]` to the fetched `live/` dir ->
`make live-fir validate macros paper`.

Pipeline stages: `setup` -> `gen` (array: model x benchmark x policy x seed, each cell = clean + F1/F2/F3
faulty runs) -> `oracle` (two judge models) -> `collect`. Per-cluster graphs:
`hpc/config/experiments.<cluster>.json`; `sync.sh` installs it as `experiments.json` remotely.
Edit the per-cluster file, not `experiments.json`.

Known failures: `OUT_OF_MEMORY` for the largest generator on a 20 GB slice (resubmit the cell);
Ollama silently running on CPU on a fresh MIG slice (hook retries until CUDA is reported, else
the cell fails; CPU-fallback cells that were kept are disclosed in `PROJECT_LOG.md`).
`status.txt`/`status.json` are local snapshots, not source of truth; the cluster audit is.

## Conventions when changing things

- Changing `src/heartness`: add/adjust tests; `make test` and `make mutation` must stay green.
  Guards can be disabled individually (that is how mutants/ablations are built); keep that.
- Changing the model or its Promela encoding: update both the Python BFS and SPIN encodings,
  `formal/SCOPE.md`, and rerun `make experiments results` (checking.csv must show agreement).
- Changing live analysis (`experiments/live/process.py`): rerun `make live-fir`, inspect
  `results/processed/live/*/live_summary.json`, then `make macros paper`; check text vs numbers.
- Pinned versions (Ollama v0.32.14, model tags, EvalPlus revisions, SPIN commit) are part of
  the protocol; do not bump them without recording why in `PROJECT_LOG.md`.
- Log notable decisions, failures and corrections in `PROJECT_LOG.md` (dated sections).

## Where to look for what

- "What does the paper claim and where is the evidence?" -> `experiments/EXPERIMENT_INDEX.md`, `docs/experiments/experiments-explained.md`
- "What is the protocol / hypotheses?" -> `experiments/PROTOCOL.md`
- "What does the model checker cover?" -> `formal/SCOPE.md`
- "How was the benchmark built?" -> `benchmark/DATASHEET.md`
- "Why was X decided?" -> `PROJECT_LOG.md`, `reviews/`
- "How does a job run?" -> `hpc/README.md`, `hpc/slurm/stage.sh`, `hpc/scripts/run_stage.py`
