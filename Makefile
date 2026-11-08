PYTHON := .venv/bin/python

.PHONY: live-fir setup test validate mutation experiments realistic live live-llama live-supplement live-results results macros paper all
setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.lock
	.venv/bin/pip install -e . --no-build-isolation
	bash scripts/install_spin.sh

test:
	.venv/bin/ruff check src benchmark experiments scripts tests
	.venv/bin/mypy
	$(PYTHON) -m pytest -q --cov=heartness --cov-branch --cov-report=term-missing --cov-report=json:build/coverage.json
	$(PYTHON) scripts/check_coverage.py

validate:
	$(PYTHON) scripts/validate.py

mutation:
	$(PYTHON) scripts/mutation.py

experiments:
	$(PYTHON) -m experiments.run

realistic:
	$(PYTHON) -m experiments.realistic --bundled

live:
	$(PYTHON) -m experiments.live.campaign --model qwen2.5:7b --campaign results/raw/live-qwen25-7b

live-llama:
	$(PYTHON) -m experiments.live.campaign --model llama3.1:8b --campaign results/raw/live-llama31-8b --jobs 5 --thresholds results/raw/live-qwen-thresholds.json

live-supplement:
	$(PYTHON) -m experiments.live.supplement $$(ls results/raw/live-*/*/F*/seed-[0-9]/record.json)

live-results:
	$(PYTHON) -m experiments.live.process report results/raw/live-qwen25-7b
	$(PYTHON) -m experiments.live.process report results/raw/live-llama31-8b

macros:
	$(PYTHON) scripts/paper_macros.py

results:
	$(PYTHON) -m experiments.process
	$(PYTHON) scripts/build_paper_results.py

paper:
	cd docs/TSE && latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=../../build/paper main.tex

all: validate mutation experiments realistic live live-llama live-supplement live-results results macros paper

# ── four-cluster HPC operation (hpc/multi/README.md) ──
hpc-connect:
	bash hpc/multi/connect.sh
hpc-status:
	python3 hpc/multi/status.py
hpc-sync:
	bash hpc/multi/sync.sh all
hpc-fetch:
	bash hpc/multi/fetch.sh all

live-fir:
	PYTHONPATH=src $(PYTHON) -m experiments.live.process report results/raw/live-fir
	test ! -d results/raw/live-fir-curate || PYTHONPATH=src $(PYTHON) -m experiments.live.process report results/raw/live-fir-curate
	test ! -d results/raw/live-fir-late || PYTHONPATH=src $(PYTHON) -m experiments.live.process report results/raw/live-fir-late
	$(PYTHON) scripts/paper_macros.py
