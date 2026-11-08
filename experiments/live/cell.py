"""One HPC matrix cell: model x benchmark x policy x seed.

phase gen   : clean + F1 + F2 + F3 runs concurrently against one inference server,
              then closure-bounded revalidation (supplement) for the faulty runs.
phase oracle: content-oracle labels for the same four runs (judge models).
Finished runs are skipped (record.json / oracle.json / supplement.json exist), so a
requeued job resumes. Writes <campaign>/cells/<cell>.<phase>.json as the step output.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

FAULTS = (None, "F1", "F2", "F3")


def run_dir(campaign: Path, model: str, benchmark: str, policy: str, fault: str | None,
            seed: int) -> Path:
    base = campaign / model.replace(":", "_")
    if benchmark != "humaneval" or policy != "curate":
        base = base / f"{benchmark}_{policy}"
    return base / (fault or "clean") / f"seed-{seed}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", type=Path, required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--benchmark", required=True)
    ap.add_argument("--policy", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--phase", choices=("gen", "oracle"), required=True)
    ap.add_argument("--n-evolve", type=int, default=24)
    ap.add_argument("--tau-tfidf", type=float, required=True)
    ap.add_argument("--tau-embed", type=float, required=True)
    ap.add_argument("--fault-index", type=int, default=None, help="fixed fault position (run.py)")
    ap.add_argument("--cell", default="", help="output key (the HPC pipeline passes {CELL})")
    args = ap.parse_args()
    start = time.time()
    base = [sys.executable, "-m", "experiments.live.run", "--campaign", str(args.campaign),
            "--model", args.model, "--seed", str(args.seed), "--benchmark", args.benchmark,
            "--policy", args.policy, "--n-evolve", str(args.n_evolve),
            "--tau-tfidf", str(args.tau_tfidf), "--tau-embed", str(args.tau_embed),
            "--phase", args.phase]
    if args.fault_index is not None:
        base += ["--fault-index", str(args.fault_index)]

    def one(fault: str | None) -> dict[str, object]:
        cmd = base + (["--fault", fault] if fault else [])
        t = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return {"fault": fault or "clean", "rc": proc.returncode, "seconds": round(time.time() - t, 1),
                "stdout": proc.stdout[-800:], "stderr": proc.stderr[-2500:]}

    # gen: runs share one server concurrently; oracle: sequential, one judge model resident
    with ThreadPoolExecutor(len(FAULTS) if args.phase == "gen" else 1) as pool:
        runs = list(pool.map(one, FAULTS))
    supplement = []
    if args.phase == "gen":
        for fault in FAULTS[1:]:
            record = run_dir(args.campaign, args.model, args.benchmark, args.policy, fault,
                             args.seed) / "record.json"
            if record.exists():
                proc = subprocess.run([sys.executable, "-m", "experiments.live.supplement",
                                       str(record)], capture_output=True, text=True)
                supplement.append({"fault": fault, "rc": proc.returncode,
                                   "stderr": proc.stderr[-1500:]})
    cell = args.cell or f"{args.model.replace(':', '_')}__{args.benchmark}__{args.policy}__{args.seed}"
    out = args.campaign / "cells" / f"{cell}.{args.phase}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    ok = all(r["rc"] == 0 for r in runs) and all(r["rc"] == 0 for r in supplement)
    out.write_text(json.dumps({"cell": cell, "phase": args.phase, "ok": ok, "runs": runs,
                               "supplement": supplement,
                               "seconds": round(time.time() - start, 1)}, indent=1))
    print(json.dumps({"cell": cell, "ok": ok, "seconds": round(time.time() - start, 1)}))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
