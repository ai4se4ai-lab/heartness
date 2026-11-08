#!/usr/bin/env python3
"""Federated audit across clusters: one dashboard built from each cluster's own use-hpc audit.

    python3 hpc/multi/status.py                    latest recorded run per cluster (full, else smoke)
    python3 hpc/multi/status.py --kind smoke       latest smoke runs
    python3 hpc/multi/status.py --run nibi=<ID>    a specific run on one cluster (repeatable)
    python3 hpc/multi/status.py --full             also print every cluster's complete audit table
    python3 hpc/multi/status.py --only failed      cluster tables filtered (implies --full)
    python3 hpc/multi/status.py --watch 300        refresh (minimum 120 s: 4 clusters x 1 squeue+sacct each)

For every cluster it runs `python3 hpc/scripts/audit.py <RUN_ID> --no-color` remotely over the
existing SSH master connection (hpc/multi/connect.sh), which refreshes logs/<RUN_ID>/audit.json
on that cluster, then reads that JSON. Nothing is submitted or modified. The combined snapshot is
saved locally as hpc/multi/status.txt and status.json.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

MULTI = Path(__file__).resolve().parent
USER = os.environ.get("HPC_USER", "mbabaei")
SOCK = Path.home() / ".ssh/controlmasters"
BAD = {"FAILED", "TIMEOUT", "CANCELLED", "OUT_OF_MEMORY", "NODE_FAIL", "PARTIAL"}
ORDER = ["OK", "RUNNING", "REQUEUED", "PENDING", "NOT_SUBMITTED", *sorted(BAD)]
SYM = {"OK": "✔", "RUNNING": "▶", "PENDING": "○", "REQUEUED": "↻", "NOT_SUBMITTED": "–"}


def clusters() -> list[dict[str, str]]:
    rows = []
    for line in (MULTI / "clusters.tsv").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            name, host, repo, slice_, offline = line.split("\t")
            rows.append({"name": name, "host": host, "repo": repo, "slice": slice_,
                         "offline": offline})
    return rows


def ledger_run(name: str, kind: str) -> str:
    path = MULTI / "runs.tsv"
    if not path.exists():
        return ""
    runs = [r.split("\t") for r in path.read_text().splitlines()[1:] if r.strip()]
    for want in ([kind] if kind != "auto" else ["full", "smoke"]):
        chosen = [r[2] for r in runs if r[1] == name and r[3] == want]
        if chosen:
            return chosen[-1]
    return ""


def ssh(c: dict[str, str], cmd: str, timeout: int = 120) -> tuple[int, str]:
    sock = SOCK / f"{USER}@{c['host']}:22"
    try:
        p = subprocess.run(["ssh", "-o", f"ControlPath={sock}", "-o", "BatchMode=yes",
                            f"{USER}@{c['host']}", cmd], capture_output=True, text=True,
                           timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def snapshot(c: dict[str, str], run: str, full: bool, only: str) -> dict:
    out: dict = {"cluster": c["name"], "slice": c["slice"], "run": run}
    sock = SOCK / f"{USER}@{c['host']}:22"
    if subprocess.run(["ssh", "-o", f"ControlPath={sock}", "-O", "check", f"{USER}@{c['host']}"],
                      capture_output=True).returncode != 0:
        out["error"] = f"not connected — bash hpc/multi/connect.sh {c['name']}"
        return out
    if not run:
        out["error"] = "no run recorded in hpc/multi/runs.tsv"
        return out
    opts = "--no-color" + (" --steps" if full and not only else "") + (f" --only {only}" if only else "")
    cmd = (f"cd {c['repo']} && python3 hpc/scripts/audit.py {run} {opts} > /tmp/.hm_audit_$$.txt; "
           f"rc=$?; cat hpc/logs/{run}/audit.json; echo '@@AUDIT_TEXT@@'; cat /tmp/.hm_audit_$$.txt; "
           f"rm -f /tmp/.hm_audit_$$.txt; exit $rc")
    rc, text = ssh(c, cmd)
    raw, _, table = text.partition("@@AUDIT_TEXT@@")
    try:
        data = json.loads(raw[raw.index("{"):])
    except ValueError:
        out["error"] = f"audit failed (rc={rc}): {text.strip()[:200]}"
        return out
    out["rows"] = data.get("rows", [])
    out["table"] = table.strip()
    return out


def summarize(snap: dict) -> list[str]:
    name = f"{snap['cluster']:<8}"
    if "error" in snap:
        return [f"  ✘ {name} {snap['error']}"]
    rows = snap["rows"]
    lines = [f"  ■ {name} {snap['slice']:<20} run {snap['run']}"]
    stages: dict[str, list[dict]] = {}
    for r in rows:
        stages.setdefault(r.get("stage", "?"), []).append(r)
    for stage, rs in stages.items():
        cnt = Counter(r.get("state", "?") for r in rs)
        parts = [f"{SYM.get(k, '✘')}{cnt[k]} {k.lower()}" for k in ORDER if cnt.get(k)]
        running = [r for r in rs if r.get("state") == "RUNNING"]
        pend = Counter((r.get("reason") or "-") for r in rs if r.get("state") == "PENDING")
        extra = ""
        if running:
            extra += f"  nodes {','.join(sorted({str(r.get('node', '-')) for r in running}))[:30]}"
        if pend:
            extra += "  waiting: " + ", ".join(f"{k}×{v}" for k, v in pend.most_common(2))
        lines.append(f"      {stage:<8} {len(rs):>3} cells  " + "  ".join(parts) + extra)
    for r in rows:
        if r.get("state") in BAD or r.get("failed"):
            failed = r.get("failed") or []
            note = next((s.get("note", "") for s in r.get("steps", []) if s.get("status") == "FAILED"),
                        "")
            lines.append(f"      ✘ {r.get('stage')}[{r.get('cell_id')}] {r.get('cell', '')[:40]} "
                         f"{r.get('state')} {','.join(failed)} {note[:60]}")
    return lines


def render(snaps: list[dict], full: bool) -> str:
    total = Counter(r.get("state") for s in snaps for r in s.get("rows", []))
    head = (f"HEARTNESS multi-cluster audit — {datetime.now():%Y-%m-%d %H:%M:%S}   "
            + "  ".join(f"{k.lower()} {total[k]}" for k in ORDER if total.get(k)))
    lines = [head, "─" * len(head)]
    for s in snaps:
        lines += summarize(s)
    if full:
        for s in snaps:
            if s.get("table"):
                lines += ["", f"══ {s['cluster']} ({s['run']}) " + "═" * 40, s["table"]]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kind", default="auto", choices=("auto", "full", "smoke"))
    ap.add_argument("--run", action="append", default=[], help="cluster=RUN_ID")
    ap.add_argument("--clusters", default="", help="comma list (default: all)")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--watch", type=int, nargs="?", const=300, default=0)
    a = ap.parse_args()
    chosen = clusters()
    if a.clusters:
        keep = set(a.clusters.split(","))
        chosen = [c for c in chosen if c["name"] in keep]
    explicit = dict(x.split("=", 1) for x in a.run)
    full = a.full or bool(a.only)
    period = max(a.watch, 120) if a.watch else 0
    while True:
        with ThreadPoolExecutor(len(chosen)) as pool:
            snaps = list(pool.map(lambda c: snapshot(c, explicit.get(c["name"]) or
                                                     ledger_run(c["name"], a.kind), full, a.only),
                                  chosen))
        text = render(snaps, full)
        (MULTI / "status.txt").write_text(text + "\n")
        (MULTI / "status.json").write_text(json.dumps(
            [{k: v for k, v in s.items() if k != "table"} for s in snaps], indent=1, default=str))
        if period:
            print("\033[2J\033[H", end="")
        print(text)
        active = any(r.get("state") in ("RUNNING", "PENDING", "REQUEUED")
                     for s in snaps for r in s.get("rows", []))
        if not period or not active:
            return 0
        print(f"\n refreshing every {period} s (Ctrl-C leaves; jobs keep running)")
        try:
            time.sleep(period)
        except KeyboardInterrupt:
            return 0


if __name__ == "__main__":
    sys.exit(main())
