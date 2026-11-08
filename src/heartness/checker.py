"""Finite lifecycle projection, explicit BFS, and independent SPIN encoding.

The projection has static derivation/dependency edges and Boolean validation.
It does not encode arbitrary text, the event ledger, or effects. See formal/SCOPE.md.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import time
from collections import deque
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SmallState:
    proposed: int = 0
    validated: int = 0
    installed: int = 0
    active: int = 0
    withdrawn: int = 0
    deployed: int = 0
    epoch: int = 0
    bases: tuple[int, ...] = ()
    snapshots: tuple[int, ...] = (0,)


def masks(n: int, topology: str = "chain") -> tuple[tuple[int, ...], tuple[int, ...]]:
    parents = tuple(0 if i == 0 or topology == "independent" else
                    (1 if topology == "star" else 1 << (i - 1)) for i in range(n))
    cones: list[int] = []
    for root in range(n):
        cone = 1 << root
        for i in range(root + 1, n):
            if parents[i] & cone:
                cone |= 1 << i
        cones.append(cone)
    return parents, tuple(cones)


def initial(n: int) -> SmallState:
    if not 1 <= n <= 8:
        raise ValueError("finite projection supports 1 to 8 revision identities")
    return SmallState(bases=tuple(-1 for _ in range(n)))


def actions(n: int) -> list[tuple[str, int]]:
    return [(op, i) for op in ("propose", "validate", "accept", "withdraw", "deploy", "rollback")
            for i in range(n)]


def step(s: SmallState, action: tuple[str, int], n: int, mutant: str = "",
         topology: str = "chain") -> SmallState | None:
    op, i = action
    bit = 1 << i
    parents, cones = masks(n, topology)
    if op == "propose" and not s.proposed & bit and parents[i] & s.installed == parents[i]:
        bases = list(s.bases)
        bases[i] = s.epoch
        return replace(s, proposed=s.proposed | bit, bases=tuple(bases))
    if op == "validate" and s.proposed & bit and not s.validated & bit:
        return replace(s, validated=s.validated | bit)
    if op == "accept" and s.proposed & bit and not s.installed & bit:
        if not s.validated & bit and mutant != "P4":
            return None
        if s.bases[i] != s.epoch and mutant != "P9":
            return None
        if parents[i] & s.active != parents[i] and mutant != "P3":
            return None
        forbidden = any(s.withdrawn & (1 << j) and cones[j] & bit for j in range(n))
        if forbidden and mutant != "P2":
            return None
        active = s.active | bit
        return replace(s, installed=s.installed | bit, active=active, epoch=s.epoch + 1,
                       snapshots=s.snapshots + (active,))
    if op == "withdraw" and s.installed & bit:
        active = s.active & ~(bit if mutant == "P2" else cones[i])
        deployed = s.deployed if mutant == "P8" else s.deployed & ~cones[i]
        return replace(s, active=active, withdrawn=s.withdrawn | bit, deployed=deployed,
                       epoch=s.epoch + 1, snapshots=s.snapshots + (active,))
    if op == "deploy" and s.active != s.deployed:
        return replace(s, deployed=s.active)
    if op == "rollback" and i < len(s.snapshots):
        active = s.snapshots[i]
        if any(s.withdrawn & (1 << j) and cones[j] & active for j in range(n)):
            return None
        return replace(s, active=active, epoch=s.epoch + 1, snapshots=s.snapshots + (active,))
    return None


def bad(s: SmallState, n: int, previous: SmallState | None = None,
        action: tuple[str, int] | None = None, topology: str = "chain") -> list[str]:
    parents, cones = masks(n, topology)
    found: set[str] = set()
    for i in range(n):
        bit = 1 << i
        if s.withdrawn & bit:
            if s.active & cones[i]:
                found.add("P2")
            if s.deployed & cones[i]:
                found.add("P8")
        if s.active & bit and parents[i] & s.active != parents[i]:
            found.add("P3")
        if s.installed & bit and not s.validated & bit:
            found.add("P4")
    if previous is not None and action is not None and action[0] == "accept":
        if previous.bases[action[1]] != previous.epoch:
            found.add("P9")
    return sorted(found)


def bfs(n: int, depth: int, mutant: str = "", topology: str = "chain",
        state_limit: int = 250_000, seconds: float | None = None) -> dict[str, Any]:
    if not 1 <= depth <= 200:
        raise ValueError("operation bound must be between 1 and 200")
    start = initial(n)
    todo: deque[tuple[SmallState, tuple[tuple[str, int], ...]]] = deque([(start, ())])
    seen = {start}
    transitions = 0
    started = time.perf_counter()
    while todo:
        if seconds is not None and time.perf_counter() - started >= seconds:
            return {"safe": None, "complete": False, "states": len(seen),
                    "transitions": transitions, "trace": (), "properties": [],
                    "depth": depth, "termination": "time budget"}
        state, path = todo.popleft()
        if len(path) == depth:
            continue
        for action in actions(n):
            nxt = step(state, action, n, mutant, topology)
            if nxt is None:
                continue
            transitions += 1
            trace = path + (action,)
            verdict = bad(nxt, n, state, action, topology)
            if verdict:
                return {"safe": False, "complete": True, "states": len(seen),
                        "transitions": transitions, "trace": trace, "properties": verdict,
                        "depth": len(trace)}
            if nxt not in seen:
                if len(seen) >= state_limit:
                    return {"safe": None, "complete": False, "states": len(seen),
                            "transitions": transitions, "trace": (), "properties": [],
                            "depth": depth}
                seen.add(nxt)
                todo.append((nxt, trace))
    return {"safe": True, "complete": True, "states": len(seen),
            "transitions": transitions, "trace": (), "properties": [], "depth": depth}


def replay(trace: list[list[Any]] | tuple[tuple[str, int], ...], n: int,
           mutant: str = "", topology: str = "chain") -> list[str]:
    s = initial(n)
    result: list[str] = []
    for op, i in trace:
        action = (str(op), int(i))
        nxt = step(s, action, n, mutant, topology)
        if nxt is None:
            raise ValueError("non-executable counterexample")
        result.extend(bad(nxt, n, s, action, topology))
        s = nxt
    return sorted(set(result))


def promela(n: int, depth: int, mutant: str = "", topology: str = "chain") -> str:
    """Independent imperative transition encoding; no Python successors exported."""
    initial(n)
    if not 1 <= depth <= 200:
        raise ValueError("SPIN byte counters support bounds 1 to 200")
    parents, cones = masks(n, topology)
    lines = [f"byte base[{n}]; byte snap[{depth + 1}];",
             "byte p; byte v; byte h; byte a; byte w; byte d; byte epoch; byte k;",
             "init { atomic {", *[f"base[{i}]=255;" for i in range(n)], "} do"]
    for i in range(n):
        b = 1 << i
        forbidden = " && ".join(f"(!((w & {1 << j}) != 0) || (({cones[j]} & {b}) == 0))"
                                 for j in range(n))
        guard = f"(p & {b}) != 0 && (h & {b}) == 0"
        if mutant != "P4":
            guard += f" && (v & {b}) != 0"
        if mutant != "P9":
            guard += f" && base[{i}]==epoch"
        if mutant != "P3":
            guard += f" && (a & {parents[i]})=={parents[i]}"
        if mutant != "P2":
            guard += " && " + forbidden
        options = [
            (f"(p & {b})==0 && (h & {parents[i]})=={parents[i]}",
             f"p=p|{b}; base[{i}]=epoch;"),
            (f"(p & {b})!=0 && (v & {b})==0", f"v=v|{b};"),
            (guard, (f"assert(base[{i}]==epoch); " if mutant == "P9" else "") +
             f"h=h|{b}; a=a|{b}; epoch++; snap[epoch]=a;"),
            (f"(h & {b})!=0",
             f"w=w|{b}; a=a&{((1 << n) - 1) ^ (b if mutant == 'P2' else cones[i])}; " +
             ("" if mutant == "P8" else f"d=d&{((1 << n) - 1) ^ cones[i]}; ") +
             "epoch++; snap[epoch]=a;"),
            ("a!=d", "d=a;"),
        ]
        roll_guard = " && ".join(f"((w & {1 << j})==0 || (snap[{i}] & {cones[j]})==0)"
                                  for j in range(n))
        options.append((f"{i}<=epoch && " + roll_guard,
                        f"a=snap[{i}]; epoch++; snap[epoch]=a;"))
        for condition, body in options:
            checks = []
            for j in range(n):
                checks.extend([
                    f"assert((w & {1 << j})==0 || (a & {cones[j]})==0);",
                    f"assert((w & {1 << j})==0 || (d & {cones[j]})==0);",
                    f"assert((a & {1 << j})==0 || (a & {parents[j]})=={parents[j]});",
                    f"assert((h & {1 << j})==0 || (v & {1 << j})!=0);",
                ])
            lines.append(f":: atomic {{ k<{depth} && ({condition}) -> {body} k++; " +
                         " ".join(checks) + " }")
    lines.extend([":: else -> break", "od }"])
    return "\n".join(lines) + "\n"


def spin_check(n: int, depth: int, mutant: str = "", topology: str = "chain",
               timeout: float = 60) -> dict[str, Any]:
    binary = shutil.which("spin") or str(Path("build/tools/spin").resolve())
    with tempfile.TemporaryDirectory(prefix="heartness-spin-") as tmp:
        path = Path(tmp)
        model = promela(n, depth, mutant, topology)
        (path / "model.pml").write_text(model)
        subprocess.run([binary, "-a", "model.pml"], cwd=path, check=True, capture_output=True)
        subprocess.run(["gcc", "-O2", "-DBFS", "-DSAFETY", "-DNOREDUCE", "-o", "pan", "pan.c"],
                       cwd=path, check=True, capture_output=True)
        run = subprocess.run([str(path / "pan"), "-m10000", "-w20"], cwd=path,
                             capture_output=True, text=True, timeout=timeout)
        output = run.stdout + run.stderr
        errors = re.search(r"errors:\s*(\d+)", output)
        states = re.search(r"([\d.e+]+) states, stored", output)
        trail = ""
        if (path / "model.pml.trail").exists():
            trail_run = subprocess.run([binary, "-t", "-p", "model.pml"], cwd=path,
                                       capture_output=True, text=True, check=False)
            trail = trail_run.stdout + trail_run.stderr
        complete = errors is not None and "max search depth too small" not in output
        return {"safe": int(errors[1]) == 0 if complete and errors else None,
                "complete": complete, "states": float(states[1]) if states else None,
                "log": output, "trail": trail, "model": model}
