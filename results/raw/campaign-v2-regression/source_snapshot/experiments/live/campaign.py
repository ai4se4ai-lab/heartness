"""Orchestrate a live campaign: dev runs -> threshold tuning -> clean + reporting runs.

python -m experiments.live.campaign --model qwen2.5:7b [--campaign DIR] [--jobs 6]
Each run is an independent process writing an exclusive record; failures are logged
in manifest.jsonl and never retried silently.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from experiments.live.process import tune

FAULTS = ("F1", "F2", "F3")


def run(campaign: Path, args: list[str]) -> dict[str, object]:
    cmd = [sys.executable, "-m", "experiments.live.run", "--campaign", str(campaign), *args]
    start = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    entry = {"cmd": cmd[2:], "returncode": proc.returncode, "seconds": round(time.time() - start, 1),
             "stdout": proc.stdout[-2000:], "stderr": proc.stderr[-3000:]}
    with (campaign / "manifest.jsonl").open("a") as handle:
        handle.write(json.dumps(entry) + "\n")
    print(json.dumps({k: entry[k] for k in ("cmd", "returncode", "seconds")}), flush=True)
    return entry


def batch(campaign: Path, jobs: list[list[str]], workers: int) -> None:
    with ThreadPoolExecutor(workers) as pool:
        list(pool.map(lambda a: run(campaign, a), jobs))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--campaign", type=Path)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--thresholds", type=Path, help="reuse thresholds tuned in another campaign")
    args = ap.parse_args()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    campaign = args.campaign or Path("results/raw") / f"live-{stamp}"
    campaign.mkdir(parents=True, exist_ok=True)
    m = ["--model", args.model]
    if args.thresholds:
        tau = json.loads(args.thresholds.read_text())
    else:
        batch(campaign, [[*m, "--seed", str(s), "--fault", f] for s in (100, 101) for f in FAULTS],
              args.jobs)
        tau = tune(campaign)
        (campaign / "thresholds.json").write_text(json.dumps(tau, indent=1))
    t = ["--tau-tfidf", str(tau["tfidf"]), "--tau-embed", str(tau["embed"])]
    jobs = [[*m, "--seed", str(s)] for s in args.seeds]
    jobs += [[*m, "--seed", str(s), "--fault", f, *t] for s in args.seeds for f in FAULTS]
    batch(campaign, jobs, args.jobs)
    print("campaign", campaign)


if __name__ == "__main__":
    main()
