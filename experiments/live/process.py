"""Aggregate live-study records. Never edits raw records.

python -m experiments.live.process tune  CAMPAIGN   # thresholds from dev seeds only
python -m experiments.live.process report CAMPAIGN  # metrics, statistics, tables
"""
from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from scipy.stats import wilcoxon

DEV_SEEDS = {100, 101}
REMEDIES = ("none", "R1_delete_root", "R2_tfidf", "R3_embed", "R4_judge",
            "H", "H_noEME", "H_noDeps", "H_local", "HS_judge", "HS_embed",
            "T_since_fault", "A_all_learned", "H_faulty_root", "H_EMEfail")
# Post-hoc conditions computed from the recorded final state only (no held-out evaluation):
#   T_since_fault  rollback to the last snapshot before the corrupted experience, i.e. suspend
#                  every revision created at or after the fault (needs only the fault time)
#   A_all_learned  suspend every learned (non-seed) revision
#   H_faulty_root  closure of only those roots the oracle labels contaminated (an operator who
#                  withdraws exactly the faulty revision; oracle-informed, a sensitivity bound)
#   H_EMEfail      closure in which EME edges come only from runs whose task FAILED (an EME
#                  policy variant: lessons are written from failures; passing runs add none)
POSTHOC = ("T_since_fault", "A_all_learned", "H_faulty_root", "H_EMEfail")
# Comparators whose difference from H is an empirical question; ablations and post-hoc variants
# are reported descriptively (several are identical to H by construction in some policies).
HOLM_FAMILY = ("none", "R1_delete_root", "R2_tfidf", "R3_embed", "R4_judge", "HS_judge",
               "HS_embed")


def created_at(rec: dict[str, Any]) -> dict[str, int]:
    """Task index at which each revision was created, from the evolution log."""
    when: dict[str, int] = {}
    for entry in rec["evolution"]:
        i = entry["i"]
        ids = [entry.get("memory"), (entry.get("skill") or {}).get("id")]
        ids += [p.get("id") for p in (entry.get("profiles") or {}).values()
                if isinstance(p, dict)]
        ids += [op.get("id") for op in (entry.get("extraction") or {}).get("ops", [])]
        for a in ids:
            if a and a not in when:
                when[a] = i
    return when


def closure(rec: dict[str, Any], roots: list[str], eme: bool = True) -> set[str]:
    from types import SimpleNamespace

    from heartness.graph import Graph
    arts = {k: SimpleNamespace(id=k, sources=tuple(a["sources"]),
                               dependencies=tuple(a["dependencies"]),
                               experiences=tuple(a["experiences"]))
            for k, a in rec["artifacts"].items()}
    runs = rec["loaded"] if eme else None
    graph = Graph(arts, run_context=runs,  # type: ignore[arg-type]
                  experience_run={f"e{i}": f"r{i}" for i in range(len(rec["evolution"]))})
    return graph.closure(roots, dependencies=True)


def posthoc(rec: dict[str, Any], lab: dict[str, str], targets: list[str]) -> dict[str, set[str]]:
    when = created_at(rec)
    fault = rec["fault_index"]
    seeds = {a for a, art in rec["artifacts"].items() if not art["experiences"]
             and not art["sources"]}
    bad_roots = [r for r in rec["roots"] if lab.get(r) == "c"]
    failed = {f"r{e['i']}" for e in rec["evolution"] if not e.get("passed")}
    return {"T_since_fault": {a for a in targets if when.get(a, -1) >= fault},
            "A_all_learned": {a for a in targets if a not in seeds},
            "H_faulty_root": closure(rec, bad_roots) if bad_roots else set(),
            "H_EMEfail": closure({**rec, "loaded": {k: v for k, v in rec["loaded"].items()
                                                    if k in failed}}, rec["roots"])}

def kind_of(rid: str) -> str:
    return "profile" if "-p" in rid else {"m": "memory", "k": "skill", "r": "insight"}.get(rid[0], "other")


def structure(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Where contamination lives, what detectors miss, and how closure relates to the time cut."""
    from collections import Counter
    cont: Counter[str] = Counter()
    missed: dict[str, Counter[str]] = {n: Counter() for n in ("R2_tfidf", "R3_embed", "R4_judge")}
    missed_runs: Counter[str] = Counter()
    missed_runs_composed: Counter[str] = Counter()
    strict = subset = profiles_in = 0
    gap: Counter[str] = Counter()
    gap_before_compose = 0
    eme_only: list[dict[str, Any]] = []
    strict_by_pos: dict[int, list[int]] = {}
    faulty_miss_root: Counter[str] = Counter()
    profile_runs = 0
    for rec in runs:
        lab = labels(rec, rec["config"]["fault"])
        targets = [a for a in rec["universe"] if a not in rec["roots"]]
        c = [a for a in targets if lab.get(a) == "c"]
        cont.update(kind_of(a) for a in c)
        for name in missed:
            m = [a for a in c if a not in set(rec["remedies"][name]["suspended"])]
            missed[name].update(kind_of(a) for a in m)
            missed_runs[name] += bool(m)
            missed_runs_composed[name] += any(kind_of(a) in ("skill", "profile") for a in m)
        when = created_at(rec)
        cut = {a for a in targets if when.get(a, -1) >= rec["fault_index"]}
        h = set(rec["remedies"]["H"]["suspended"]) & set(targets)
        subset += h <= cut
        strict += h < cut
        pos = strict_by_pos.setdefault(rec["fault_index"] + 1, [0, 0])  # 1-based task
        pos[0] += h < cut
        pos[1] += 1
        profile_runs += any(kind_of(a) == "profile" for a in c)
        bad_roots = [r for r in rec["roots"] if lab.get(r) == "c"]
        if c and not bad_roots:  # H_faulty withdraws nothing although derivatives are bad
            faulty_miss_root.update(lab.get(r, "?") for r in rec["roots"])
        gap.update(kind_of(a) for a in cut - h)
        compose = min(rec["config"].get("compose_at") or [10**9])
        gap_before_compose += sum(when[a] < compose for a in cut - h)
        post = [a for a in cut if kind_of(a) == "profile"]
        profiles_in += all(a in h for a in post)
        no_eme = set(rec["remedies"]["H_noEME"]["suspended"])
        lost = [a for a in c if a not in no_eme]
        if lost:
            eme_only.append({"run": str(Path(rec["_path"]).relative_to(Path(rec["_path"]).parents[3]))
                             if len(Path(rec["_path"]).parents) > 3 else rec["_path"],
                             "roots": rec["roots"], "missed": lost})
    return {"contaminated_by_kind": dict(cont),
            "missed_by_kind": {k: dict(v) for k, v in missed.items()},
            "missed_runs": dict(missed_runs),
            "missed_runs_composed": dict(missed_runs_composed),
            "closure_subset_of_cut": subset, "closure_strictly_smaller": strict,
            "cut_minus_closure_by_kind": dict(gap),
            "cut_minus_closure_before_first_compose": gap_before_compose,
            "runs_all_postfault_profiles_in_closure": profiles_in,
            "eme_only": eme_only,
            "closure_strictly_smaller_by_fault_task": {str(k): v for k, v in
                                                       sorted(strict_by_pos.items())},
            "faulty_root_misses_root_labels": dict(faulty_miss_root),
            "runs_with_contaminated_profile": profile_runs,
            "revalidation_rejected": reval_rejected(runs)}


def independent_noise(recs: list[dict[str, Any]]) -> dict[str, Any]:
    seen: dict[tuple[Any, ...], dict[str, bool]] = {}
    seed_only: set[tuple[Any, ...]] = set()
    for rec in recs:
        texts = {k: a["text"] for k, a in rec["artifacts"].items()}
        seeds = {k for k, a in rec["artifacts"].items() if not a["sources"] and not a["experiences"]}
        for name, items in rec["eval"].items():
            if name.startswith("HS_"):  # revalidation reads every cache file: not independent
                continue
            for it in items:
                key = (rec["config"]["model"], rec["config"]["seed"], it["task"],
                       it.get("deployment"), tuple(texts[a] for a in it["context"]))
                seen.setdefault(key, {}).setdefault(rec["_path"], bool(it["passed"]))
                if set(it["context"]) <= seeds:
                    seed_only.add(key)
    pairs = flips = flips_no_learned = 0
    for key, by_run in seen.items():
        vals = list(by_run.values())
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                pairs += 1
                flips += vals[i] != vals[j]
                flips_no_learned += vals[i] != vals[j] and key in seed_only  # no learned state
    return {"pairs": pairs, "flips": flips, "rate": flips / pairs if pairs else None,
            "flips_without_learned_state": flips_no_learned}


def reval_rejected(runs: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Algorithm 5 rejections: cleared members not re-admitted because a dependency stayed
    suspended; `contaminated` counts those the oracle labels contaminated (P3 kept them out)."""
    out: dict[str, dict[str, int]] = {}
    for name in ("HS_judge", "HS_embed"):
        total = runs_hit = cont = 0
        for rec in runs:
            rej = rec["remedies"].get(name, {}).get("rejected") or {}
            lab = labels(rec, rec["config"]["fault"])
            total += len(rej)
            runs_hit += bool(rej)
            cont += sum(lab.get(a) == "c" for a in rej)
        out[name] = {"rejected": total, "runs": runs_hit, "contaminated": cont}
    return out


def selectivity(recs: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Structural selectivity of closure versus the time cut, independent of the oracle: every
    revision active at the end of a run (faulty and clean runs) is taken as a hypothetical root;
    compare |Cl(root)| with the revisions accepted after it, by the root's task (blocks of 6)."""
    out: dict[str, dict[str, float]] = {}
    acc: dict[str, list[tuple[float, float, bool]]] = {}
    for rec in recs:
        when = created_at(rec)
        univ = set(rec["universe"])
        failed = {f"r{e['i']}" for e in rec["evolution"] if not e.get("passed")}
        rec_fail = {**rec, "loaded": {k: v for k, v in rec["loaded"].items() if k in failed}}
        for root in univ:
            if root not in when:
                continue
            # time cut restricted to revisions from LATER tasks: revisions written in the same
            # step as the root (e.g. sibling insights of one extraction) are never exposed to
            # it, so counting them would credit closure with a selectivity a step-level
            # rollback also has
            cut = {x for x in univ if when.get(x, -1) > when[root]}
            if not cut:
                continue
            cl = closure(rec, [root]) & cut
            cl_fail = closure(rec_fail, [root]) & cut
            block = f"{6 * (when[root] // 6) + 1}-{6 * (when[root] // 6) + 6}"
            last = max(when.values())  # final composition step: does the root reach it?
            finals = {x for x in rec["artifacts"] if when.get(x) == last
                      and rec["artifacts"][x]["kind"] == "agent"}
            acc.setdefault(block, []).append((len(cl) / len(cut), len(cl_fail) / len(cut),
                                              cl < cut, len(cut), len(cut - cl),
                                              bool(finals) and finals <= closure(rec, [root])))
    for block, vals in sorted(acc.items(), key=lambda kv: int(kv[0].split("-")[0])):
        out[block] = {"roots": len(vals), "ratio": mean(v[0] for v in vals),
                      "ratio_eme_fail": mean(v[1] for v in vals),
                      "strict": mean(float(v[2]) for v in vals),
                      "later": mean(v[3] for v in vals), "spared": mean(v[4] for v in vals),
                      "reach_final_profiles": sum(v[5] for v in vals)}
    return out

OUT_ROOT = Path("results/processed/live")


def records(campaign: Path, clean: bool = False) -> list[dict[str, Any]]:
    out = []
    for path in sorted(campaign.rglob("seed-*/record.json")):
        tag = path.parts[-3]
        if (tag == "clean") == clean:
            rec = json.loads(path.read_text())
            rec["_path"] = str(path)
            rec["config"].setdefault("benchmark", "humaneval")
            rec["config"].setdefault("policy", "curate")
            if "roots" not in rec and "root" in rec:
                rec["roots"] = [rec["root"]]
            labelled = path.with_name("oracle.json")
            if "oracle" not in rec:
                if not labelled.exists():
                    continue  # generation finished, oracle job pending: not yet analysable
                rec["oracle"] = json.loads(labelled.read_text())["oracle"]
            supplement = path.with_name("supplement.json")
            if supplement.exists() and rec.get("remedies"):  # post-review extension
                extra = json.loads(supplement.read_text())
                rec["remedies"].update(extra["remedies"])
                rec["eval"].update(extra["eval"])
            out.append(rec)
    return out


def labels(rec: dict[str, Any], fault: str) -> dict[str, str]:
    """unanimous YES -> 'c' (contaminated), unanimous NO -> 'n', otherwise 'a' (ambiguous)."""
    result = {}
    for key, per_fault in rec["oracle"].items():
        votes = list(per_fault[fault].values())
        result[key] = "c" if all(votes) else "n" if not any(votes) else "a"
    return result


def prf(suspended: set[str], lab: dict[str, str], targets: list[str],
        ambiguous_as: str = "skip") -> dict[str, float | None]:
    def cls(a: str) -> str:
        return lab[a] if lab[a] != "a" else ambiguous_as
    contaminated = {a for a in targets if cls(a) == "c"}
    clean = {a for a in targets if cls(a) == "n"}
    tp = len(suspended & contaminated)
    fp = len(suspended & clean)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / len(contaminated) if contaminated else None
    f1 = (2 * precision * recall / (precision + recall)
          if precision is not None and recall is not None and precision + recall else
          (0.0 if contaminated else None))
    return {"tp": tp, "fp": fp, "precision": precision, "recall": recall, "f1": f1,
            "residual": len(contaminated - suspended), "collateral": fp,
            "contaminated": len(contaminated)}


def tune(campaign: Path) -> dict[str, float]:
    OUT = OUT_ROOT / campaign.name
    dev = [r for r in records(campaign) if r["config"]["seed"] in DEV_SEEDS]
    if not dev:
        raise SystemExit("no dev records")
    best: dict[str, float] = {}
    for metric in ("tfidf", "embed"):
        grid = [round(0.05 * i, 2) for i in range(1, 20)]
        scored = []
        for tau in grid:
            f1s = []
            for rec in dev:
                lab = labels(rec, rec["config"]["fault"])
                if not rec.get("roots"):
                    continue
                targets = [a for a in rec["universe"] if a not in rec["roots"]]
                chosen = {a for a in targets if rec["scores"][a][metric] >= tau}
                f1 = prf(chosen, lab, targets)["f1"]
                if f1 is not None:
                    f1s.append(f1)
            scored.append((mean(f1s) if f1s else 0.0, -tau, tau))
        best[metric] = max(scored)[2]
        best[metric + "_dev_f1"] = max(scored)[0]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "thresholds.json").write_text(json.dumps({**best, "dev_runs": len(dev)}, indent=1))
    return best


def a12(x: list[float], y: list[float]) -> float:
    gt = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in x for b in y)
    return gt / (len(x) * len(y))


def boot(values: list[float], seed: int = 20261106, n: int = 2000) -> tuple[float, float]:
    rng = random.Random(seed)
    means = sorted(mean(rng.choices(values, k=len(values))) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    order = sorted(pvalues, key=pvalues.get)  # type: ignore[arg-type]
    adjusted, running = {}, 0.0
    for i, key in enumerate(order):
        running = max(running, min(1.0, (len(order) - i) * pvalues[key]))
        adjusted[key] = running
    return adjusted


def kappa(pairs: list[tuple[bool, bool]]) -> float:
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a for a, _ in pairs) / n
    pb = sum(b for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def report(campaign: Path) -> dict[str, Any]:
    OUT = OUT_ROOT / campaign.name
    runs = [r for r in records(campaign) if r["config"]["seed"] not in DEV_SEEDS]
    def key(r: dict[str, Any]) -> tuple[str, str, str, int]:
        c = r["config"]
        return c["model"], c["benchmark"], c["policy"], c["seed"]
    cleans = {key(r): r for r in records(campaign, True)}
    not_adopted = [r for r in runs if not r.get("roots")]
    runs = [r for r in runs if r.get("roots")]
    rows: list[dict[str, Any]] = []
    for rec in runs:
        fault, roots = rec["config"]["fault"], rec["roots"]
        lab = labels(rec, fault)
        targets = [a for a in rec["universe"] if a not in roots]
        clean = cleans.get(key(rec))
        base = {"model": rec["config"]["model"], "benchmark": rec["config"]["benchmark"],
                "policy": rec["config"]["policy"], "fault": fault, "seed": rec["config"]["seed"],
                "roots": len(roots),
                "root_label": "c" if any(lab[r] == "c" for r in roots) else
                              "a" if any(lab[r] == "a" for r in roots) else "n",
                "artifacts": len(targets),
                "contaminated": sum(lab[a] == "c" for a in targets),
                "ambiguous": sum(lab[a] == "a" for a in targets),
                "contaminated_kinds": "+".join(sorted(rec["artifacts"][a]["kind"]
                                                      for a in targets if lab[a] == "c")),
                "clean_pass": (mean(x["passed"] for x in clean["eval"]["clean"]) if clean else None),
                "seed_only_pass": (mean(x["passed"] for x in clean["eval"]["seed_only"])
                                   if clean else None)}
        extra = posthoc(rec, lab, targets)
        for name in REMEDIES:
            if name not in rec["remedies"] and name not in extra:
                continue
            chosen = extra[name] if name in extra else rec["remedies"][name]["suspended"]
            suspended = set(chosen) & set(targets)
            m = prf(suspended, lab, targets)
            m_amb = prf(suspended, lab, targets, ambiguous_as="c")
            ev = rec["eval"].get(name) or [{"passed": None, "fault_signature": None}]
            rows.append({**base, "remedy": name, **m, "recall_amb_c": m_amb["recall"],
                         "precision_amb_c": m_amb["precision"], "suspended": len(suspended),
                         "pass": (None if name in POSTHOC else mean(x["passed"] for x in ev)),
                         "signature": (None if name in POSTHOC else
                                       mean(bool(x["fault_signature"]) for x in ev)),
                         "seconds": rec["timing"].get(name if name.startswith("H") else
                                                      {"R2_tfidf": "R2_tfidf", "R3_embed": "R3_embed",
                                                       "R4_judge": "R4_judge"}.get(name, ""), 0.0)})
    OUT.mkdir(parents=True, exist_ok=True)
    if not rows:  # nothing analysable yet (e.g. a smoke run, or oracle jobs still pending)
        empty = {"runs": 0, "campaign": str(campaign), "not_adopted_runs": len(not_adopted),
                 "note": "no faulty run with both generation and oracle labels"}
        (OUT / "live_summary.json").write_text(json.dumps(empty, indent=1))
        return empty
    with (OUT / "live_runs.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    def col(name: str, key: str, cond: Any = None) -> list[float]:
        return [r[key] for r in rows if r["remedy"] == name and r[key] is not None
                and (cond is None or cond(r))]

    summary: dict[str, Any] = {"runs": len(runs), "campaign": str(campaign),
                               "not_adopted_runs": len(not_adopted),
                               "propagated_runs": sum(1 for r in rows if r["remedy"] == "none"
                                                      and r["contaminated"] > 0),
                               "root_adopted": sum(1 for r in rows if r["remedy"] == "none"
                                                   and r["root_label"] == "c"),
                               "remedies": {}}
    propagated = lambda r: r["contaminated"] > 0  # noqa: E731
    for name in REMEDIES:
        entry: dict[str, Any] = {}
        for key in ("precision", "recall", "f1", "residual", "collateral", "pass", "signature",
                    "suspended", "seconds", "recall_amb_c", "precision_amb_c"):
            values = col(name, key, propagated if key in ("recall", "f1", "recall_amb_c")
                         else None)
            if values:
                lo, hi = boot(values)
                entry[key] = {"mean": mean(values), "sd": pstdev(values), "lo": lo, "hi": hi,
                              "n": len(values)}
        # precision and suspension restricted to runs where contamination propagated, so that
        # precision, recall and F1 describe the same runs
        for key in ("precision", "suspended", "collateral", "pass", "signature"):
            values = col(name, key, propagated)
            if values:
                lo, hi = boot(values)
                entry[key + "_prop"] = {"mean": mean(values), "sd": pstdev(values), "lo": lo,
                                        "hi": hi, "n": len(values)}
        summary["remedies"][name] = entry
    tests: dict[str, Any] = {}
    for key in ("recall", "f1", "residual", "pass", "signature", "collateral", "pass_prop",
                "signature_prop"):
        field = key.removesuffix("_prop")
        only = (lambda r: r["contaminated"] > 0) if key.endswith("_prop") else (lambda r: True)
        pvals, detail = {}, {}
        for name in REMEDIES:
            if name == "H":
                continue
            pairs = [(h[field], o[field]) for h in rows if h["remedy"] == "H" and only(h)
                     for o in rows if o["remedy"] == name and o["seed"] == h["seed"]
                     and o["fault"] == h["fault"] and o["model"] == h["model"]
                     and o["benchmark"] == h["benchmark"] and o["policy"] == h["policy"]
                     and h[field] is not None and o[field] is not None]
            if not pairs:
                continue
            x, y = [p[0] for p in pairs], [p[1] for p in pairs]
            diffs = [a - b for a, b in pairs]
            p = 1.0 if all(d == 0 for d in diffs) else float(wilcoxon(x, y).pvalue)
            pvals[name] = p
            detail[name] = {"n": len(pairs), "p": p, "a12": a12(x, y),
                            "mean_diff": mean(diffs), "H_higher": sum(d > 0 for d in diffs),
                            "H_lower": sum(d < 0 for d in diffs),
                            "ties": sum(d == 0 for d in diffs)}
        family = {k: v for k, v in pvals.items() if k in HOLM_FAMILY}
        for name, adj in holm(family).items():
            detail[name]["p_holm"] = adj
        for name in detail:
            detail[name].setdefault("p_holm", None)
        tests[key] = detail
    summary["tests_H_vs"] = tests
    diffs = [h["pass"] - o["pass"] for h in rows if h["remedy"] == "H" and h["contaminated"] > 0
             for o in rows if o["remedy"] == "none" and (o["model"], o["fault"], o["seed"])
             == (h["model"], h["fault"], h["seed"])]
    summary["pass_prop_H_minus_none"] = {"n": len(diffs), "higher": sum(d > 0 for d in diffs),
                                         "lower": sum(d < 0 for d in diffs),
                                         "equal": sum(d == 0 for d in diffs),
                                         "values": sorted(round(d, 3) for d in diffs)}
    summary["roots_per_run"] = {k: sum(1 for r in rows if r["remedy"] == "none" and r["roots"] == k)
                                for k in sorted({r["roots"] for r in rows})}
    summary["fault_positions"] = {k: sum(1 for r in runs if r["fault_index"] == k)
                                  for k in sorted({r["fault_index"] for r in runs})}
    # Upper bound for the similarity baselines: the single threshold that maximizes mean F1
    # on the reporting runs themselves (oracle-tuned; never used for any other result).
    bound: dict[str, Any] = {}
    for metric in ("tfidf", "embed"):
        best: tuple[float, float, float, float] | None = None
        for tau in [round(0.05 * i, 2) for i in range(1, 20)]:
            f1s, recs = [], []
            for rec in runs:
                lab = labels(rec, rec["config"]["fault"])
                targets = [a for a in rec["universe"] if a not in rec["roots"]]
                m = prf({a for a in targets if rec["scores"][a][metric] >= tau}, lab, targets)
                if m["f1"] is not None:
                    f1s.append(m["f1"])
                    recs.append(m["recall"] or 0.0)
            if f1s and (best is None or mean(f1s) > best[0]):
                best = (mean(f1s), tau, mean(recs), len(f1s))
        if best:
            bound[metric] = {"f1": best[0], "tau": best[1], "recall": best[2], "n": best[3]}
    summary["oracle_tuned_bound"] = bound
    curve: dict[str, list[dict[str, float]]] = {"tfidf": [], "embed": []}
    for metric in curve:
        for tau in [round(0.05 * i, 2) for i in range(1, 20)]:
            f1s, recs, sus = [], [], []
            for rec in runs:
                lab = labels(rec, rec["config"]["fault"])
                targets = [a for a in rec["universe"] if a not in rec["roots"]]
                chosen = {a for a in targets if rec["scores"][a][metric] >= tau}
                m = prf(chosen, lab, targets)
                if m["f1"] is not None:
                    f1s.append(m["f1"])
                    recs.append(m["recall"] or 0.0)
                    sus.append(len(chosen))
            if f1s:
                curve[metric].append({"tau": tau, "f1": mean(f1s), "recall": mean(recs),
                                      "suspended": mean(sus), "n": len(f1s)})
    summary["threshold_curve"] = curve
    # Inference noise. Within one process a repeated prompt is answered from the response
    # cache, so it cannot differ; that is replay determinism, not inference determinism. The
    # four runs of a cell (clean, F1-F3) run as separate processes against one server, each
    # with its own cache, so a byte-identical evaluation prompt (same model, seed, task,
    # deployment and context TEXTS) occurring in two different runs was generated twice,
    # independently. Pass/fail differences between such pairs are non-determinism of batched
    # GPU inference.
    summary["noise_independent"] = independent_noise([*runs, *cleans.values()])
    adopted = [r for r in rows if r["root_label"] == "c"]
    summary["adopted"] = {name: {k: mean(r[k] for r in adopted if r["remedy"] == name)
                                 for k in ("suspended", "collateral", "residual")}
                          for name in REMEDIES if any(r["remedy"] == name for r in adopted)}
    summary["adopted_runs"] = len({(r["model"], r["fault"], r["seed"]) for r in adopted})
    summary["adopted_with_ambiguous"] = sum(1 for r in rows if r["remedy"] == "none"
                                            and r["root_label"] in ("c", "a"))
    pairs = [(v[j1], v[j2]) for rec in [*runs, *cleans.values()] for per in rec["oracle"].values()
             for v in per.values() for j1, j2 in [tuple(v)]]
    both_yes = sum(bool(a) and bool(b) for a, b in pairs)
    one_yes = sum(bool(a) != bool(b) for a, b in pairs)
    summary["judge_agreement"] = {"items": len(pairs), "raw": mean(a == b for a, b in pairs),
                                  "kappa": kappa(pairs), "yes_both": both_yes, "disagree": one_yes,
                                  # positive agreement: agreement on YES, robust to the many NOs
                                  "positive": (2 * both_yes / (2 * both_yes + one_yes)
                                               if both_yes + one_yes else None)}
    fp = {}
    for fault in ("F1", "F2", "F3"):
        votes = [labels(c, fault)[a] for c in cleans.values() for a in c["universe"]]
        fp[fault] = {"artifacts": len(votes), "contaminated": votes.count("c"),
                     "ambiguous": votes.count("a")}
    summary["clean_run_labels"] = fp
    summary["clean_pass"] = {"clean": mean(mean(x["passed"] for x in c["eval"]["clean"])
                                           for c in cleans.values()),
                             "seed_only": mean(mean(x["passed"] for x in c["eval"]["seed_only"])
                                               for c in cleans.values())} if cleans else {}
    summary["cost"] = {
        "evolve_seconds": mean(r["timing"]["evolve_total"] for r in runs),
        "engine_seconds": mean(r["timing"]["engine_total"] for r in runs),
        "engine_percent_max": max(100 * r["timing"]["engine_total"] / r["timing"]["evolve_total"]
                                  for r in runs),
        "history_events": mean(r["history_events"] for r in runs),
        "llm_calls": mean(r["llm"]["calls"] for r in runs),
        "tokens_in": mean(r["llm"]["tokens_in"] for r in runs),
        "tokens_out": mean(r["llm"]["tokens_out"] for r in runs)}
    summary["selectivity"] = selectivity([*runs, *cleans.values()])
    summary["structure"] = structure(runs)
    summary["structure"]["hs_judge_differs_from_r4_propagated"] = sum(
        1 for rec in runs if "HS_judge" in rec["remedies"]
        and any(labels(rec, rec["config"]["fault"]).get(a) == "c" for a in rec["universe"]
                if a not in rec["roots"])
        and set(rec["remedies"]["HS_judge"]["suspended"]) & set(rec["universe"])
        != set(rec["remedies"]["R4_judge"]["suspended"]) & set(rec["universe"]))
    (OUT / "live_summary.json").write_text(json.dumps(summary, indent=1))
    return summary


if __name__ == "__main__":
    command, target = sys.argv[1], Path(sys.argv[2])
    result = tune(target) if command == "tune" else report(target)
    print(json.dumps(result, indent=1)[:4000])
