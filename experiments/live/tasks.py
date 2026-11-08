"""HumanEval+ tasks (EvalPlus), sandboxed test execution and fault-signature detection."""
from __future__ import annotations

import ast
import json
import math
import os
import random
import re
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PARQUET = Path.home() / (".cache/huggingface/hub/datasets--evalplus--humanevalplus/snapshots/"
                         "d32357cf319e50e9c8d8dab5ea876c72b0fd321b/data/"
                         "test-00000-of-00001-5973903632b82d40.parquet")
DATASET_REVISION = "evalplus/humanevalplus@d32357cf319e50e9c8d8dab5ea876c72b0fd321b"
REVISIONS = {"humaneval": DATASET_REVISION,
             "mbpp": "evalplus/mbppplus@b2d74c91837c3f2a20c1299ae98133cbe7cfa077"}
# Tasks whose canonical solution fails its own EvalPlus tests in our sandbox (validated
# by experiments/live/validate_tasks.py); excluded from every task set.
EXCLUDED = {"HumanEval/32", "Mbpp/590"}


@dataclass(frozen=True)
class Task:
    id: str
    prompt: str
    entry_point: str
    test: str
    canonical: str
    direct: bool = False  # MBPP+: the test calls the function itself (no check())


def _data(name: str) -> Path:
    root = os.environ.get("HEARTNESS_DATA")
    return Path(root) / name if root else Path("build/data") / name


def _rows(stem: str, fallback: Path | None = None) -> list[dict[str, Any]]:
    """JSONL conversion (shipped to the cluster, no pyarrow needed) or the pinned parquet."""
    jsonl = _data(stem + ".jsonl")
    if jsonl.exists():
        return [json.loads(line) for line in jsonl.read_text().splitlines() if line.strip()]
    import pyarrow.parquet as pq
    path = _data(stem + ".parquet")
    rows: list[dict[str, Any]] = pq.read_table(
        path if path.exists() or fallback is None else fallback).to_pylist()
    return rows


def load_tasks(benchmark: str = "humaneval") -> list[Task]:
    if benchmark == "humaneval":
        rows = _rows("humanevalplus", PARQUET)
        tasks = [Task(r["task_id"], r["prompt"], r["entry_point"], r["test"],
                      r["canonical_solution"]) for r in rows]
    elif benchmark == "mbpp":
        rows = _rows("mbppplus")
        tasks = []
        for r in rows:
            name = re.search(r"^def\s+(\w+)", r["code"], re.M)
            assert name, r["task_id"]
            example = list(r["test_list"])[0]
            imports = "\n".join(r["test_imports"])
            prompt = (f'"""\n{r["prompt"]}\nImplement the function `{name.group(1)}`. '
                      f'Example:\n{example}\n"""\n')
            tasks.append(Task("Mbpp/" + str(r["task_id"]), prompt, name.group(1),
                              (imports + "\n" if imports else "") + r["test"], r["code"],
                              direct=True))
    else:
        raise ValueError(benchmark)
    return tasks  # EXCLUDED is applied after split() so the split is unchanged


def split(tasks: list[Task], n_eval: int = 30, seed: int = 7) -> tuple[list[Task], list[Task]]:
    """Fixed held-out evaluation tasks; the remaining pool supplies evolution tasks."""
    order = list(tasks)
    random.Random(seed).shuffle(order)
    return order[:n_eval], order[n_eval:]


def extract_code(response: str, task: Task) -> str:
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", response, re.S)
    code = max(blocks, key=len) if blocks else response
    if f"def {task.entry_point}" not in code and not task.direct:
        code = task.prompt + code
    header = "\n".join(line for line in task.prompt.splitlines()
                       if line.startswith(("import ", "from ")))
    return header + "\n" + code


def run_tests(code: str, task: Task, timeout: float = 30) -> tuple[bool, str]:
    program = code + "\n\n" + task.test + ("\n" if task.direct else
                                            f"\n\ncheck({task.entry_point})\n")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "solution.py"
        path.write_text(program)
        try:
            proc = subprocess.run([sys.executable, "-I", str(path)], cwd=tmp, capture_output=True,
                                  text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, "FAILED: timeout"
    if proc.returncode == 0:
        return True, "PASSED all tests."
    lines = [ln for ln in proc.stderr.strip().splitlines() if ln.strip()]
    return False, "FAILED: " + (lines[-1][:300] if lines else "non-zero exit")


def _function(code: str, name: str) -> ast.FunctionDef | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def signature(fault: str, code: str, task: Task) -> bool:
    """Static evidence that a solution exhibits the planted faulty practice."""
    fn = _function(code, task.entry_point)
    if fn is None:
        return False
    nodes = list(ast.walk(fn))
    if fault == "F1":  # prints instead of returning
        prints = any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "print" for n in nodes)
        returns = any(isinstance(n, ast.Return) and n.value is not None for n in nodes)
        return prints and not returns
    if fault == "F2":  # stringifies returned values
        return any(isinstance(n, ast.Return) and (
            isinstance(n.value, ast.JoinedStr) or (isinstance(n.value, ast.Call) and
                                                   getattr(n.value.func, "id", "") == "str"))
                   for n in nodes) and "str(" not in task.canonical
    if fault == "F3":  # floor division where the reference uses none
        return any(isinstance(n, ast.FloorDiv) for n in nodes) and "//" not in task.canonical
    return False


# ---------------------------------------------------------------- deterministic TF-IDF
def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z][a-z0-9_]+", text.lower())


def tfidf_cosine(query: str, docs: list[str]) -> list[float]:
    corpus = [Counter(tokens(d)) for d in docs] + [Counter(tokens(query))]
    df = Counter(t for c in corpus for t in c)
    n = len(corpus)

    def vec(c: Counter[str]) -> dict[str, float]:
        return {t: (1 + math.log(f)) * math.log((1 + n) / (1 + df[t])) for t, f in c.items()}

    q = vec(corpus[-1])
    qn = math.sqrt(sum(v * v for v in q.values())) or 1.0
    out = []
    for c in corpus[:-1]:
        d = vec(c)
        dn = math.sqrt(sum(v * v for v in d.values())) or 1.0
        out.append(sum(q.get(t, 0.0) * v for t, v in d.items()) / (qn * dn))
    return out


def cosine(a: list[float], b: list[float]) -> float:
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return sum(x * y for x, y in zip(a, b, strict=True)) / (na * nb)
