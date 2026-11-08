# Heartness

Heartness investigates traceable state evolution and withdrawal in AI harnesses
(self-evolving agents whose memories, skills and prompts change by themselves). It
records on the host side what every generation step and run was exposed to, withdraws
a faulty revision together with its exposure closure in every deployment, and refuses
admissions and rollbacks that would reactivate it.

The repository contains an executable research prototype, a live self-evolution study
on open-weight LLMs, a construction-labeled synthetic benchmark, an independent finite
SPIN encoding, reproducible experiments, an HPC pipeline for four Alliance Canada
clusters, and the TSE manuscript (`docs/TSE/main.tex`). It does not claim production
readiness or better agent task outcomes.

**Agents and new contributors:** read [AGENTS.md](AGENTS.md) first.

## What the paper evaluates

| Subject | What | Where it runs | RQs |
|---|---|---|---|
| S1 live harness | 5 open-weight generators (`qwen2.5-coder:7b`, `llama3.1:8b`, `deepseek-coder-v2:16b`, `gemma2:9b`, `granite3.3:8b`) x 2 policies (ExpeL-style insights, curation) x 5 seeds x (3 planted faults + clean) = **200 runs** on HumanEval+; two judge models (`mistral-small:24b`, `phi4:14b`) label contamination; `nomic-embed-text` for the embedding baseline | GPU cluster (Fir, H100 20 GB slice) | RQ1, RQ3 |
| S2 synthetic | EvoTraceBench 1.1: 1,905 raw records, 810 traceability scenarios; SPIN + Python BFS model checking; runtime monitor | any machine, no GPU | RQ1, RQ2, RQ3 |
| S3 Voyager replay | 12 public skill revisions replayed as 36 controller events | any machine | RQ3 |

Every number in the paper is generated from raw records by `scripts/paper_macros.py`
(the `BEGIN GENERATED MACROS` block in `main.tex`); `results/processed/paper_macro_index.json`
maps each number to its source file. Never edit those macros by hand.

## Which reproduction path do I need?

| Goal | Needs | Command |
|---|---|---|
| Rebuild the PDF and every live table/figure from shipped raw data | CPU only | `make live-fir macros paper` |
| Re-run tests, mutation checks, synthetic experiments, model checking | CPU, SPIN | `make setup test mutation experiments results` |
| Re-run the live study from scratch (new LLM generations) | Alliance GPU cluster account | [HPC section](#running-the-live-study-on-the-hpc-clusters) below |
| Re-run the old local pilot (threshold tuning) | one GPU + Ollama | `make live live-llama` |

## Reproduce without a GPU

Prerequisites: Python 3.11+, GCC, make, git, yacc/bison, and a LaTeX installation
with IEEEtran, TikZ, PGFPlots, algorithmicx and latexmk.

```bash
make setup         # venv, pinned deps, editable install, SPIN built from a pinned commit
make test          # ruff, mypy (strict), pytest with branch coverage gate
make mutation      # hand-seeded guard mutants must all be killed
make experiments   # new immutable synthetic campaign under results/raw/campaign-*
make results       # processed CSVs, statistics, summary
make live-fir      # re-derive all live (S1) tables from shipped records + LLM caches; no GPU
make macros        # regenerate the paper's numbers
make paper         # build/paper/main.pdf
```

`make experiments` always creates a new immutable campaign. `make results` selects the
most recent completed **main** campaign, excluding public-replay supplements. Semantic
results are deterministic for fixed seeds; timings, environment records, and
wall-clock-budget search discovery counts are not byte-identical.

The PDF is `build/paper/main.pdf`. All paper text, tables and graphics are inline in
`docs/TSE/main.tex`; the only other paper source is `references.bib`. Original template
inputs are preserved in `design/input-template/`. The user research prompt
(`docs/PROMPT.md`) remains unchanged.

## Running the live study on the HPC clusters

The live study (S1) needs GPU inference for several 7-24B models. `hpc/` runs it as a
graph of Slurm jobs; `hpc/multi/` drives four Alliance clusters from your workstation
over SSH with one interface:

| cluster | GPU slice | compute-node internet | matrix slice in `hpc/multi/clusters.tsv` |
|---|---|---|---|
| nibi | H100 `h100_2g.20gb` | yes | HumanEval+ x curate |
| narval | A100 `a100_3g.20gb` | no (models staged from login node) | MBPP+ x curate |
| fir | H100 `h100_2g.20gb` | throttled, so staged from login node | HumanEval+ x ExpeL |
| rorqual | H100 `h100_2g.20gb` | no (models staged from login node) | MBPP+ x ExpeL |

**What the paper reports.** All four clusters were prepared and smoke-tested. Nibi's GPU
nodes were unavailable, so the reported study ran on **Fir only** (two slices:
HumanEval+ x ExpeL run `am-20261107-060101`, HumanEval+ x curate run
`am-20261107-080855`). The platform is not an experimental factor; every remedy is
compared inside one cell (one cluster, one GPU type) and each record stores host,
cluster, GPU and model digests. Narval/Rorqual/Nibi slices exist for MBPP+ or
replication and are not reported as findings. Smoke runs only find deployment faults.

Prerequisites: an Alliance account with GPU allocation on the cluster(s) and MFA set up;
`ssh`, `rsync` locally. Remote user defaults to `mbabaei`; override with
`export HPC_USER=<your-alliance-username>`. Edit `hpc/multi/clusters.tsv` (host,
`repo_dir`) and `hpc/config/cluster.env` (`ACCOUNT`, storage paths) for your own
allocation. Commands run from the repository root.

### Step by step

**1. Open the connections (once per session).** One MFA prompt per cluster; the SSH
master sockets are reused by every other command for up to 12 h of inactivity.

```bash
bash hpc/multi/connect.sh                 # all clusters
bash hpc/multi/connect.sh fir             # only Fir
bash hpc/multi/connect.sh --check         # which connections are alive (no prompts)
bash hpc/multi/connect.sh --close         # close them
```

**2. Check the data shipped with the repo.** `build/data/*.jsonl` (HumanEval+ and MBPP+
JSONL, checksummed in `build/data/MANIFEST.json`) is gitignored but synced to the
clusters, because compute nodes have no pyarrow. Make sure it exists locally.

**3. Sync code and install each cluster's experiment graph.** Pushes code (never
results; `rsync --delete` on the remote repo dir), copies
`hpc/config/experiments.<cluster>.json` to `experiments.json` there, and runs the selftest.

```bash
bash hpc/multi/sync.sh fir                # or: all
```

**4. Stage Ollama and models (clusters without compute-node internet: fir, narval,
rorqual).** Downloads run on the login node in the background.

```bash
bash hpc/multi/stage.sh fir
bash hpc/multi/stage.sh --check fir       # repeat until all pinned models are present
```

**5. Dry run, then smoke test.** The smoke test runs every stage end to end on GPU
nodes with 8 evolution tasks and one seed. Do not start the full run until it passes.

```bash
bash hpc/multi/submit.sh --dry-run fir    # job graph and sbatch commands, nothing submitted
bash hpc/multi/submit.sh --smoke fir      # records RUN_ID in hpc/multi/runs.tsv
python3 hpc/multi/status.py --kind smoke --clusters fir
```

**6. Submit the full run.** This spends GPU allocation (about 25 gen + 25 oracle cells per
slice, up to 3 h each); submit deliberately.

```bash
bash hpc/multi/submit.sh --full fir       # or: all
```

**7. Watch the status.** Read-only: one `squeue` + one `sacct` per cluster per refresh,
via each cluster's own `hpc/scripts/audit.py`. Writes `hpc/multi/status.txt` and
`status.json`.

```bash
python3 hpc/multi/status.py --kind full --clusters fir   # latest full run on Fir
python3 hpc/multi/status.py                               # all clusters (full, else smoke)
python3 hpc/multi/status.py --kind smoke                 # latest smoke runs
python3 hpc/multi/status.py --run fir=am-20261107-060101 # a specific run
python3 hpc/multi/status.py --full                       # + each cluster's complete audit table
python3 hpc/multi/status.py --only failed                # failed rows with reasons and log tails
python3 hpc/multi/status.py --watch 300                  # refresh (minimum 120 s)
```

Stages are `setup` (pinned Ollama, model digests, dataset checksums, canonical-solution
validation) -> `gen` (array: model x benchmark x policy x seed; each cell runs the clean
run and three faulty runs) -> `oracle` (two judge models label artifacts, `aftercorr`
pipelined) -> `collect`. States: OK, RUNNING, PENDING, REQUEUED, NOT_SUBMITTED, and the
failure states FAILED, TIMEOUT, CANCELLED, OUT_OF_MEMORY, NODE_FAIL, PARTIAL.

**8. Repair failures without redoing finished work.** Finished cells are skipped.

```bash
bash hpc/multi/submit.sh --full fir -- --run-id <RUN_ID> --only gen,oracle,collect
bash hpc/multi/submit.sh --full fir -- --run-id <RUN_ID> --only oracle
```

Known failure modes from the Fir runs: `OUT_OF_MEMORY` on a 20 GB slice for the
largest generator (resubmit the cell), and Ollama silently falling back to CPU on a
fresh MIG slice (`hpc/slurm/hooks/ollama_common.sh` restarts the server until it reports
a CUDA device, otherwise the cell fails). Details: `PROJECT_LOG.md`.

**9. Fetch results.** Copies raw records, oracle labels, LLM caches and collected
outputs to `results/raw/hpc/<cluster>/<RUN_ID>/` and logs to `hpc/logs/<cluster>/<RUN_ID>/`.

```bash
bash hpc/multi/fetch.sh fir               # latest full run per cluster
RUN_KIND=smoke bash hpc/multi/fetch.sh fir
```

**10. Link and process locally (no GPU).** The Makefile expects the run's `live`
directory under these names (the shipped repo uses symlinks):

```bash
ln -sfn hpc/fir/<EXPEL_RUN_ID>/live  results/raw/live-fir          # HumanEval+ x ExpeL
ln -sfn hpc/fir/<CURATE_RUN_ID>/live results/raw/live-fir-curate   # HumanEval+ x curate
make live-fir      # processes live-fir, live-fir-curate and, if present, live-fir-late
make validate macros paper
```

`make live-fir` writes `results/processed/live/<campaign>/{live_runs.csv,live_summary.json}`
and refreshes the paper macros. `hpc/config/experiments.fir-late.json` is the optional
late-fault slice (fault planted after the first profile composition).

Makefile shortcuts: `make hpc-connect`, `make hpc-status`, `make hpc-sync`, `make hpc-fetch`.

### Single-cluster tools (run on a login node)

`hpc/README.md` documents the per-cluster pipeline that `hpc/multi/` wraps:
`bash hpc/scripts/selftest.sh`, `python3 hpc/slurm/submit.py --dry-run|--smoke|...`,
`bash hpc/status.sh <RUN_ID> --only failed`. `hpc/multi/README.md` has the multi-cluster
reference.

### Replay guarantees

Every LLM response is cached in `results/raw/live-*/llm_cache/` by a digest of model,
prompt and options (temperature 0, fixed per-request seeds, 8,192-token context). Re-running
analysis against an existing cache replays it without a model server. Batched GPU decoding
is not guaranteed bit-identical, so a fresh cache reproduces the protocol, not necessarily
identical texts. Generated solutions are executed in a temporary directory with a timeout
(no network isolation); run them on a disposable machine or a cluster job.

## Local pilot (optional)

The detector thresholds (`TAU_TFIDF=0.05`, `TAU_EMBED=0.55`) were tuned on a local pilot
with `qwen2.5:7b` and the curation policy before any reported run. To repeat it you need
a local Ollama server (`HEARTNESS_OLLAMA`, default `http://127.0.0.1:11435`):

```bash
make live              # dev seeds -> threshold tuning -> clean + faulty runs
make live-llama        # replication with the qwen-tuned thresholds
make live-supplement   # closure-bounded revalidation on the pilot records
make live-results
```

## Inspect the approach

```bash
.venv/bin/heartness example
.venv/bin/heartness trace --artifact s1
.venv/bin/heartness withdraw --artifact m1 --dry-run
.venv/bin/heartness rollback-plan --version 0
.venv/bin/heartness check --scope 3 --depth 10
.venv/bin/heartness monitor
.venv/bin/heartness export-model --scope 3 --depth 10
```

The default commands use the running example. Supply `--events path.json` for a
JSON event list. Source IDs mean recorded generation exposure, not causal effect.
Withdrawal plans include unreversed external effects. Exact rollback into withdrawn
lineage is rejected. Deployments are logical connected sets; running task cancellation,
authentication and distributed consistency are not implemented.

Each CLI invocation is stateless unless its resulting history is explicitly saved
and supplied to the next command. Demonstrate withdrawal and rollback in one history:

```bash
.venv/bin/heartness withdraw --artifact m1 --save-events build/withdrawn-events.json
.venv/bin/heartness rollback-plan --version 5 --events build/withdrawn-events.json
.venv/bin/python -m examples.recovery
```

The second command reports `admissible: false`. Use a fresh output filename when
repeating the first command. The recovery example retains quarantine permanently,
rejects unsafe rollback, restores the empty local snapshot, then derives a new skill
from independently observed corrective feedback and explicitly redeploys it. It
does not clear quarantine by editing a revoked descendant. Plans conservatively
list **all** recorded external effects, without attributing each to the revoked source.

`capture.py` demonstrates an explicit generation boundary: the host selects source
IDs and freezes their texts before a policy generates content; the host attaches
those IDs to the proposal. Declared untracked inputs remain visible in the exposure
record. Ambient context, model-internal knowledge, policy side channels and actual
autonomous synthesis in a production harness have not been validated.

## Public artifact replay

The bundled `results/processed/realistic.json` identifies the pinned Voyager head,
two source commits and raw replay record. To regenerate from that public snapshot:

```bash
git clone https://github.com/MineDojo/Voyager.git build/Voyager
git -C build/Voyager checkout 55e45a880755d0c8c66ca7fb5fe7962ac8974f89
make realistic
```

The exact bundled replay input is the raw record's imported content and commit list.
Run `.venv/bin/python -m experiments.realistic --bundled` to replay it offline.
The historical result used a shallow clone, so a full clone may expose
more primitive-history commits. Exact reproduction uses bundled content; cloning
is a broader-history extension. `make realistic` uses the bundled input.
Imported JavaScript is stored, never executed. This is
file revision replay, not reconstruction of autonomous skill derivation.

## Evidence and limits

- `design/problem_analysis.md`, `metamodel.md`, `traceability_matrix.md`: problem,
  model, assumptions and idea-to-evidence mapping.
- `design/research_reading.md`: primary literature and evidence-design lessons.
- `formal/SCOPE.md`: exact independent-checker scope and omitted properties.
- `benchmark/DATASHEET.md`: generation, oracle construction and limitations.
- `experiments/PROTOCOL.md`: hypotheses, factors, seeds and analysis rules.
- `experiments/EXPERIMENT_INDEX.md`: raw-to-paper evidence mapping.
- `docs/experiments/experiments-explained.md`: plain-language walk-through of the experiments.
- `results/raw/`: untouched campaigns, including superseded ones; `results/raw/hpc/` holds fetched cluster runs.
- `results/processed/`: tidy metrics, statistical tests, summary and macro mapping.
- `results/validation/`: tests, coverage and targeted mutation output (`make validate`).
- `hpc/`, `hpc/multi/README.md`: batch pipeline and multi-cluster operation.
- `PROJECT_LOG.md`: chronological decisions, failures and corrections (read before changing results).
- `reviews/`: automated reviewer rounds, actions and unresolved concerns.

Limits stated in the paper: for the planted early faults, closure-based withdrawal
removes every contaminated derivative but is nearly as conservative as a rollback to
before the fault, because both policies broadcast synthesized state into later
contexts. Content detectors are more precise but miss contamination folded into skills
and profiles. Root identification is given to every remedy, not evaluated. Full captured
lineage ties capture-only graph queries by design; incomplete capture loses true
impacts. Finite verdict agreement does not prove implementation refinement; replay found
a shared abstract-model error in the first campaign. Hidden actions evade an
observation-based monitor. The live study ran on one cluster and one benchmark
(HumanEval+); synthetic data and limited public file replay do not establish real
deployment utility, causal diagnosis or safe natural-language content. Review
`FINAL_REPORT.md` for completion status.
