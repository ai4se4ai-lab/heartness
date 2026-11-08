# Round 8 -- Reviewer 1 (novelty, soundness, positioning)

This is an internal automated review of a draft, not real IEEE TSE peer review.

Scope: `docs/TSE/main.tex` (2,535 lines; `main.tex` and `main.pdf` both dated 2026-11-07 19:18), `src/heartness/revalidation.py`, `src/heartness/engine.py` (experience withdrawal, ll. 158-170), and `tests/test_revalidation.py`. The full suite passes (59 tests, `.venv/bin/python -m pytest`). Line numbers refer to `main.tex` unless a file is named. I checked each round-7 item against the files, not against the response.

Probes:

- `/tmp/claude-1000/r7rev1/probes.py`: the round-7 probes A, C and D, rerun unchanged.
- `/tmp/claude-1000/r8rev1/probeE.py`: a new probe of experience withdrawal after revalidation (see N1).

## Summary

HEARTNESS controls the persistent state that self-evolving LLM harnesses write for themselves. It does this with the following parts:

- content-addressed revisions;
- host-recorded exposure, including experience-mediated exposure (EME);
- guarded admission;
- withdrawal of revisions or experiences across all deployments;
- closure-bounded revalidation through an attestation revision;
- Propositions 1 and 2;
- bounded checking of a finite projection, with witness replay;
- a 200-run live study with two policies, plus an oracle-free analysis of structural selectivity.

Round 7 asked for two required changes.

- **R1 (lineage).** The fix is correct in the engine, covered by tests, and described correctly in the paper.
- **R2 (window effect).** The selectivity result is now stated as a window effect, and the intro and Lessons carry the qualifier.

My probes C and D now fail to reproduce the loss of a clean ancestor. A new probe, E, finds one narrower residue of the same universal sentence. It concerns *experience* withdrawal, it is fixed by one word or one small code change, and it does not affect any proposition or any live-study number (N1). I consider the paper ready for acceptance.

## Scores

| Criterion | Score (1-5) | Justification |
|---|---:|---|
| (i) Novelty | 4 | Unchanged from round 7. EME, deployment-wide closure withdrawal with reactivation guards, and attestation-based revalidation together form a distinct contribution. The bound "never more than a rollback" (Proposition 1) is honestly paired with the finding that it is often tight. The selectivity analysis (ll. 2311-2329) now identifies the mechanism that makes closure cheaper than a time cut: closure spares the revisions that reach later contexts only through retrieval, between the fault and the next broadcast composition. That mechanism is a reusable design insight. |
| (ii) Rigor | 4 | The round-7 overclaim is fixed in code and in text (l. 2059, Algorithm 5 l. 2071), and probes C and D are now tests. The window effect is stated, with the horizon caveat (l. 2311). One residue remains: the l. 2059 claim "any clean ancestor" does not hold for a clean *experience* that motivated a dropped intermediate revision (N1, probe E). It is minor and outside both propositions. |
| (iii) Relevance | 4 | Unchanged. The Lessons paragraph (l. 2459) turns the result into concrete advice for harness designers: narrow the per-step and per-run inputs, and choose deliberately which runs count as exposure. |
| (iv) Verifiability and Transparency | 4 | The tests encode the reviewer probes. The macro values match my round-7 recomputation. The Threats section (l. 2448) discloses that the selectivity analysis was added late and that its definition was revised once. Revalidation and experience withdrawal remain outside the model-checked projection, which l. 2105 discloses. |
| (v) Presentation | 4 | The claims are calibrated, and the 0.46-0.61 range is quoted with its window qualifier everywhere it appears (ll. 1743, 2311, 2459). The attestation symbol is now $\alpha$ (ll. 2059, 2067, 2071), so the clash with "one revision" $a$ (l. 1835) is gone. Minor: the selectivity table is overfull by 9.3 pt (log, "lines 2317--2329"). |

## Status of round-7 issues

| Item | Status | Evidence |
|---|---|---|
| R1 (required): keep clean *inactive* ancestors in a copy's lineage | **Done, correct** | See R1 below. |
| R2 (required): state the window effect; qualify the intro and Lessons | **Done, correct** | See R2 below. |
| R2 (recommended): absolute sizes (5.6 of 11.9; 3.5 of 6.0) and robustness to roots ever created | Not done | Optional, so not held against the paper. The caption (l. 2312) now discloses that roots are the final active revisions and that the ExpeL-style 1-6 row rests on one root. This addresses the transparency concern. |
| R3 (optional): rename the attestation symbol | **Done** | The attestation is $\alpha$ at ll. 2059, 2067 and 2071. |

### R1: clean inactive ancestors

**Code.**

- `revalidation.py` l. 91 keeps every source `y not in forbidden`, with no activity condition.
- The frontier walk (l. 137, `elif y not in forbidden`) now stops at clean ancestors whether or not they are active.

**Probes rerun.**

| Probe | Copy's sources | After `Withdraw z` | Other |
|---|---|---|---|
| A | `('att~m7~j', 'z')` | `x~r` inactive | |
| C (retired source) | `('att~m7~j', 'z')` | `x~r` inactive | |
| D (replaced source) | `('att~m7~j', 'z')` | `x~r` inactive | `z2` is suspended too |

In round 7, probes C and D left the copy active.

**Tests.** `test_retired_clean_source_stays_in_the_copy_lineage` and `test_replaced_clean_source_stays_in_the_copy_lineage` (`tests/test_revalidation.py` ll. 144-169) both pass.

**Text.** l. 2059 now reads "the sources of $x$ outside $\Cl(F)$ (active or not)" and "clean frontier, the nearest ancestors outside $\Cl(F)$, active or not". Algorithm 5 l. 2071 reads "clean frontier", and the module docstring (ll. 10-17) is updated.

**Small leftover in the code.** The response says the frontier was renamed in the code, but the code still uses the old name in places:

- The function is still called `active_frontier` (l. 122, call at l. 101).
- The inline comment at ll. 95-97 still says "ACTIVE FRONTIER: the nearest clean, active ancestors".
- The comment at l. 88 still says "active sources stay".

These now contradict the behaviour (cosmetic; see M1).

### R2: window effect

l. 2311 now states three things:

- "The sparing is a window effect: both profiles composed at task 24 were in the closure of every such root, so after the next broadcast composition the closure would again reach the time cut."
- An explanation of why the 19-24 row is higher than the 13-18 row.
- "The low ratios therefore partly reflect the 24-task horizon."

This matches my round-7 `sel3.py` finding (1,200/1,200).

The qualifier also appears where the number is quoted:

- the intro, l. 1743: "until the next composition";
- Lessons, l. 2459: "but only until the next broadcast composition".

Both quote the full range 0.46-0.61 rather than only the best cell. The l. 2311 summary sentence now reads "nearly a time cut for early faults … markedly more selective for later faults under retrieval, which our planted faults did not cover", which is accurate.

## Remaining issues

### N1 (minor; a one-word or small code change). "Any clean ancestor" does not cover clean experiences of dropped intermediates

l. 2059 says: "A later withdrawal of any clean ancestor of $x$ therefore still reaches $x'$." This now holds for revision ancestors: kept sources, the clean frontier through sources, dependencies and EME contexts, kept experiences, and copied dependencies. It does not hold for an experience that motivated a dropped (forbidden) intermediate revision.

The frontier walk (`revalidation.py` ll. 139-142) descends into the *run contexts* of a forbidden revision's experiences, but it never records those experiences themselves, even when they are clean.

Probe E (`/tmp/claude-1000/r8rev1/probeE.py`) shows the effect:

- **Setup.** `m7` is faulty. A clean run `r9` loads only `z` and yields experience `e9`. `y` has sources (`m7`) and experiences (`e9`). `x` has sources (`y`).
- **Steps.** Withdraw `m7`, clear `x`, revalidate.
- **Result.** The copy `x~r` has sources `('att~m7~j','z')` and no experiences. After `Withdraw e9`, which the engine supports (`engine.py` ll. 158-170) and which the paper presents as a first-class operator (abstract; l. 2111), `x~r` stays active. The original `x` was in the closure of `e9`'s motivated revisions.

What this does and does not affect:

- **Not affected.** Proposition 2 concerns the recorded closure, so it is not violated. No live-study number changes, because no later withdrawal is evaluated.
- **Affected.** The sentence is still universal. "Ancestor" is not defined (Definition 4 relates revisions only), so a reader can reasonably include experiences, given that experiences are withdrawable.

**Required for camera-ready (either option):**

- **(a) Fix the code.** When the walk passes a forbidden revision, add each of its experiences that is untainted and whose run context avoids $\Cl(F)$ to the copy's experiences. Walk the context only for the experiences that are not clean. Add probe E as a test.
- **(b) Narrow the text.** Change l. 2059 to "any clean ancestor revision of $x$".

I do not hold acceptance on this item. It is the last instance of a claim that is now otherwise correct, and option (b) is one word.

### M1 (cosmetic)

- In `revalidation.py`, rename `active_frontier` to `clean_frontier` (ll. 101, 122) and fix the comments at l. 88 and ll. 95-97. They now describe the old behaviour.
- The selectivity table is overfull by 9.3 pt (the log reports lines 2317-2329). Reducing `\tabcolsep` to 2.5 pt or shortening "EME-fail" would fix it.
- l. 2448 says "added after the sixth internal review round". For an external reader, "added after the initial analysis, in response to review" is clearer. The disclosure itself is good.

No criterion is scored below 4, so no further changes are needed to reach 4.

## Recommendation

**Accept** (with the one-word clarification of N1(b), or the N1(a) code change, and the cosmetic M1 edits at camera-ready).

Both round-7 required changes were made correctly, and I verified them in the code, the tests, the reruns of probes A, C and D, and the text. The paper's claims are now calibrated to its evidence:

- Closure-based withdrawal is shown to be safe, never costlier than a rollback, and often as costly in broadcast-context harnesses.
- The selectivity analysis identifies precisely when, and for how long, closure is more selective than a rollback.
