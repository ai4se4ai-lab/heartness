# Round 7 -- Reviewer 1 (novelty, soundness, positioning)

This is an internal automated review of a draft, not real IEEE TSE peer review.

Scope: `docs/TSE/main.tex` (2,535 lines; `main.pdf` rebuilt 2026-11-07 19:11; the log has only font-shape warnings), `src/heartness/revalidation.py`, `engine.py`, `tests/test_revalidation.py`, and `experiments/live/process.py` (`selectivity`, ll. 189-219). The test suite passes (57 tests, `.venv/bin/python -m pytest`). Line numbers refer to `main.tex`. I checked each item of the round-6 response against the files, not against the response. My probes are in `/tmp/claude-1000/r7rev1/`:

- `probes.py`: revalidation lineage;
- `sel.py`, `sel2.py`, `sel3.py`, `sel4.py`: re-analysis of the selectivity table from the raw records in `results/raw/live-fir` and `results/raw/live-fir-curate`.

## Summary

HEARTNESS controls the persistent state that self-evolving LLM harnesses write for themselves. It does this with the following parts:

- content-addressed revisions;
- host-recorded exposure, including experience-mediated exposure (EME);
- guarded admission;
- deployment-wide withdrawal of revisions or experiences, with admission and rollback admissibility checked against withdrawn lineage;
- closure-bounded revalidation through an attestation revision;
- Propositions 1 and 2;
- bounded checking of a finite projection, with witness replay;
- a 200-run live study with two policies.

This round makes three main changes:

- **Active frontier in revalidation.** Revalidation now replaces dropped lineage by its "active frontier". My two round-6 probes are now tests, and both pass.
- **Notation and scope.** Definition 8, the plan-versus-guards clause and the projection limits are fixed.
- **Selectivity table.** An oracle-free structural selectivity analysis (Table "Structural selectivity", ll. 2311-2329) answers my round-6 novelty option 1.

I re-derived that table from the raw records. It is correct and robust, but it reflects a window effect that the summary sentences do not state (R2 below). The frontier fix closes the cases I reported but not the general claim made at l. 2059: clean ancestors that are no longer active are still lost (R1 below).

## Scores

| Criterion | Score (1-5) | Justification |
|---|---:|---|
| (i) Novelty | 4 | Raised from 3; see the justification below. Round-6 option 1 is met in substance, narrowly and with a qualification the paper must add (R2). |
| (ii) Rigor | 4 | Definition 8, the plan-versus-guards clause (l. 2082) and the projection limits (l. 2105) are now right. The selectivity code is correct, and I reproduced every curation number. One remaining overclaim in the revalidation lineage sentence (R1, shown by two engine probes). The selectivity summary sentences omit a horizon effect (R2). |
| (iii) Relevance | 4 | Unchanged. The selectivity result gives harness designers a concrete lever: closure sparing is bounded by the next broadcast composition. |
| (iv) Verifiability and Transparency | 4 | `selectivity` is short, readable and run over faulty and clean records (l. 541 of `process.py`). The same-step exclusion and its reason are documented both in code (ll. 203-206) and in the paper (l. 2311). The macro values match my recomputation (0.92/0.94/0.46/0.61; 43/56/97/95%). Revalidation and experience withdrawal remain outside the projection and the mutation campaign, which is disclosed (l. 2105). |
| (v) Presentation | 4 | Calibrated throughout. The RQ1 box (l. 2361) and the conclusion (l. 2523) word the new result carefully ("only for curation roots after the first composition", "only for later faults in a retrieval-based harness"). Minor: the intro (l. 1743) and Lessons (l. 2459) say "of the later state" without the window qualifier (R2). The attestation and "one revision" both use $a$ (l. 1835 vs. l. 2059), as noted last round. |

### Novelty justification (re-scored)

In round 6 I wrote that a 4 would require, as option 1, "evidence that closure is materially more selective than a time cut, at equal recall, in a harness or policy with selective context assembly; for example late faults (after task 12)". I assess the new analysis against that bar.

**What it shows, verified.**

- **Curation roots after the first composition.** For hypothetical roots created at tasks 13-18 in curation runs, closure covers on average 0.46 of the later revisions. In absolute terms that is 5.6 of 11.9 (my recomputation, `sel.py`), and closure is strictly smaller than the cut for 97% of roots.
- **Earlier roots.** For roots at tasks 1-12 the coverage is 0.92-0.94.
- **ExpeL-style.** Coverage is 1.00 for every root.
- **Robustness to root selection.** I re-ran the analysis using every revision ever created as a root, not only the final active ones (`sel4.py`). This rules out survivorship bias, which matters because ExpeL has only one surviving root at tasks 1-6. The results are unchanged: curation 0.93/0.92/0.46/0.61; ExpeL 1.00 in all blocks over 1,044 roots.
- **Equal recall.** Recall is equal in the structural sense the paper uses. Closure and the cut are both complete with respect to recorded exposure, and closure is a subset of the cut by Proposition 1.

So the "late fault" example I named is now answered with real recorded structure across all 100 curation runs, not with an extrapolation.

**What limits it.**

1. **Counterfactual roots, not faults.** The roots are hypothetical, and the sparing is not shown to be clean. The paper says this (l. 2311: "measures only how much closure spares, not whether what it spares is clean").
2. **A window effect.** The sparing does not persist. All 1,200 curation roots created at tasks 13-23 are in the closure of *both* deployed profiles composed at task 24 (`sel3.py`: 700/700 and 500/500). Every later task loads those profiles. So for any detection after the next broadcast composition, closure returns to the time cut. The 0.46 therefore measures sparing within a 12-task composition window, which here coincides with the end of the run. This also explains why the 19-24 block (0.61) is *less* selective than 13-18. The task-24 composition outputs (one skill and two profiles) form half of a late root's 6-revision cut, and the root always reaches the profiles. Excluding the task-24 composition, the coverage of memories written later is 0.09-0.21 for roots at tasks 19-22.
3. **No new policy.** The analysis reuses the two existing policies. No retrieval-only policy is run.

**Why 4 nonetheless.** The paper's headline argument was weak because of the evidence, not because of the design. I asked for the evidence that would show closure buys something over a rollback in a realistic regime, and the authors have supplied it for the regime I named.

The window finding also sharpens the contribution. It turns "the policy decides what closure costs" (l. 2459) from a hypothesis into a measured, mechanistic statement: closure spares exactly the writes, between the fault and the next broadcast that includes it, whose contexts avoided the fault. That is a usable design rule for harness builders, and none of the related work (provenance, IFC, build invalidation, EVOMAL) provides it.

The individual mechanisms are still transfers; the paper says so (l. 2430). The novelty lies in the combination and in this characterisation.

The 4 is earned narrowly. It depends on the paper stating the window qualification (R2). Without it, the intro and Lessons sentences would over-sell what the table supports.

## Status of round-6 issues

| Issue | Status | Evidence |
|---|---|---|
| **R1** Revalidated copies lose transitive and mixed-context lineage | **Resolved for the reported cases; a residual remains (new R1)** | `revalidation.py` ll. 99-107 add `active_frontier` (ll. 124-145), which walks back over sources, dependencies and EME contexts to the nearest active revisions outside Cl(F). Tests `test_frontier_keeps_clean_ancestor_reached_through_a_quarantined_source` and `test_frontier_keeps_clean_context_of_a_dropped_experience` (`tests/test_revalidation.py`) are my probes A and B, and both pass. My probe A also passes (`probes.py`: `x~r` sources `('att~m7~j', 'z')`, suspended when `z` is withdrawn). Algorithm 5 l. 2071 and the docstring describe the frontier. But the frontier, and the direct-source rule, keep only *active* ancestors, so clean but inactive ancestors are still lost (new R1). |
| **R2** Definition 8 notation | **Resolved** | l. 1816: $\sigma=(\mathcal{E},\mathcal{A},Q,V,Q_{\mathrm{acc}},W,K,\Theta,\Act,\mathit{Ver},\Dpl,L,X,\Lambda)$. $X$ is the external effects, $\Theta$ is present, and $F$ is no longer a component. Withdraw "of a revision or an experience". The copy map is renamed $\nu$ (l. 2066). The optional renaming of the attestation $a$ was not done (l. 1835 vs. l. 2059); this is cosmetic. |
| **R3** `plan()` versus admission guards | **Resolved** | l. 2082: "The plan checks only dependency availability; in the engine every copy also passes the ordinary admission guards ... in the live records they cannot bind", with the reason. This matches the code (`revalidate` wraps `_admit` in `try/except Rejected`, ll. 111-115). The older sentence at l. 2448 ("rather than through the controller's admission operators") is now consistent with l. 2082. |
| **R4** Projection limits | **Resolved** | l. 2105: the list now includes "experience withdrawal and revalidation", and the text adds that the mutation campaign does not cover them either and that unit tests do. |
| **R5** (observation) Positioning of the headline | **Addressed by new analysis** | See the novelty justification. The RQ1 box (l. 2361) and the conclusion (l. 2523) are worded correctly. |
| Novelty option 1 | **Met in substance, with a qualification needed** | Table at ll. 2314-2329. I verified the code and numbers. The window effect is not yet stated (R2). |

## Remaining issues

### R1 (minor-moderate). Clean but inactive ancestors are still dropped from a revalidated copy; l. 2059 overstates

l. 2059 now says: "every source or experience that cannot be kept is replaced by its *active frontier*, the nearest active ancestors outside $\Cl(F)$ ... A later withdrawal of any clean ancestor of $x$ therefore still reaches $x'$." The `revalidation.py` docstring makes the same claim (ll. 10-17). The second sentence is false for clean ancestors that are no longer active. Both the direct-source rule (l. 96: `y in s.active and y not in forbidden`) and `active_frontier` (l. 138: `elif y in s.active and y not in forbidden`) skip them, and the walk continues *past* them to their ancestors.

The engine allows a proposal to cite an inactive source: `Propose` requires only `sources <= s.artifacts.keys()` (`engine.py` l. 109). So there is no reason to skip these ancestors. Two probes (`/tmp/claude-1000/r7rev1/probes.py`) show the loss:

- **Probe C (retired source).** Setup: `z` (clean seed) and `m7` (faulty) are the sources of `x`; `z` is retired (a curation or ExpeL REMOVE), and `x` is in Cl({z}). Steps: withdraw `m7`, clear `x`, revalidate. Result: `x~r` has sources `('att~m7~j',)` only. A later `Withdraw z` leaves `x~r` active.
- **Probe D (superseded source).** Setup: as above, but `z` is replaced by an edit `z2` (`replaces="z"`). Steps: revalidate as above, then `Withdraw z`. Result: `z2` is suspended, but `x~r` stays active.

Proposition 2 is not violated, because it concerns the recorded closure, and the live data are not affected, because no later withdrawal is evaluated. But the paper's sentence is a universal claim, and ExpeL-style EDIT/REMOVE makes superseded sources common.

**Required (either option):**

- **(a) Fix the engine.** Use "outside $\Cl(F)$" instead of "active and outside $\Cl(F)$" both for kept sources and as the frontier stopping condition. The admission guards do not require active sources. Update l. 2059 ("nearest ancestors outside $\Cl(F)$") and the docstring. Add probes C and D as tests.
- **(b) Narrow the claim.** Narrow the sentence to "any clean ancestor that is active at revalidation time".

Option (a) is a two-token code change and is clearly preferable.

### R2 (minor, but it conditions the novelty score). State the window effect of the selectivity result

l. 2311 says, correctly, that a memory written after task 12 "reaches later contexts only through retrieval until the next composition". The consequence is not drawn, and the intro (l. 1743, "a fault after the first composition would have a closure covering on average 0.46 of the later state") and Lessons (l. 2459, "closures covered on average 0.46 of the later state") present the number without qualification.

In the records, every root created at tasks 13-23 is in the closure of both profiles composed at task 24, which every later task loads (`sel3.py`: 1,200/1,200). The analysis horizon ends exactly there. **The sparing therefore holds only for faults detected before the next broadcast composition that includes the faulty revision. After it, closure returns to the time cut.** This is also why the 19-24 row (0.61) is higher than the 13-18 row (0.46), which the text does not explain.

**Required:**

- Add one sentence to l. 2311 stating that the sparing lasts until the next broadcast composition, which included every late root, so the advantage depends on detection latency relative to the composition period. Explain the 19-24 row by this.
- Qualify l. 1743 and l. 2459 accordingly, e.g. "of the state written before the next composition".

**Recommended:**

- Report the absolute sizes: for roots at tasks 13-18 the closure covers 5.6 of 11.9 later revisions; for roots at tasks 19-24 it covers 3.5 of 6.0.
- Report that the result is unchanged when all revisions ever created are used as roots (my `sel4.py`: curation 0.93/0.92/0.46/0.61, ExpeL 1.00 everywhere). This addresses the obvious survivorship question, given that ExpeL's 1-6 row has a single root (l. 2323, `\LiveESelOneRoots` = 1).

This framing helps the paper. "Closure spares exactly the retrieval-only writes between the fault and the next broadcast" is a sharper, mechanistic version of "the policy decides what closure costs".

### R3 (cosmetic, optional). Symbol $a$

Table I (l. 1835) uses $a$ for "one revision", and l. 2059 and Algorithm 5 use $a$ for the attestation. Renaming the attestation (e.g. $\alpha$) would remove the clash.

## Recommendation

**Minor revision (close to accept).**

All four round-6 required changes are in the files, and the frontier fix handles the cases I reported. The new selectivity analysis is correct, robust to root selection, and answers my novelty condition for late faults. I raise Novelty to 4 on that basis.

Two changes remain before acceptance; neither needs new experiments:

- **R1:** keep clean *inactive* ancestors in a revalidated copy's lineage (or narrow the l. 2059 claim), with two tests.
- **R2:** state that the measured sparing lasts only until the next broadcast composition, and qualify the 0.46 sentences in the intro and Lessons accordingly.
