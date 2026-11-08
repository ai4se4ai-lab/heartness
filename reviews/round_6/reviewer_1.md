# Round 6 -- Reviewer 1 (novelty, soundness, positioning)

This is an internal automated review of a draft, not real IEEE TSE peer review.

Scope: the full manuscript `docs/TSE/main.tex` (23 pages in `main.pdf`; the log shows only font-shape warnings and no undefined references). Numbers come from the generated macro block (ll. 36-1661). I also checked `src/heartness/revalidation.py` and `engine.py` and the tests. The suite passes: 54 tests with `.venv/bin/python -m pytest`. I ran two extra engine probes, described under R1 below. Line numbers refer to `main.tex`. I checked every claim of the authors' response against the files rather than taking it on trust.

## Summary

HEARTNESS is a controller for the persistent state that self-evolving LLM harnesses write for themselves: memories, skills and profiles. It has the following parts:

- immutable, content-addressed revisions;
- host-recorded exposure: synthesis sources, use dependencies, and experience-mediated exposure (EME) through recorded run contexts;
- guarded admission;
- withdrawal of a revision or an experience, which suspends the exposure closure in every deployment and constrains later admissions, deployments and rollbacks;
- closure-bounded revalidation, built from ordinary operators under an attestation revision;
- two propositions: closure is bounded by a time cut, and P2/P8 form a suspension invariant (proof sketch);
- bounded checking of a finite projection with two encodings and witness replay;
- a log-replay monitor;
- a 200-run live study with five 7-16B generators, HumanEval+, and ExpeL-style and curation policies.

This round fixes the three major issues I raised in round 5:

- The F1 claims are now correct.
- Re-admitted copies keep their clean direct lineage. I re-ran my round-5 scenario and it now behaves correctly, and a test covers it.
- The late-fault sentence is corrected.

Most minor issues are also fixed. What remains is:

- a narrower lineage loss in revalidation, together with a sentence describing the copy's lineage that is stronger than what the code does;
- one notation fix in Definition 8 that the response reports as done but that is not in the file;
- two small wording leftovers.

## Scores

| Criterion | Score (1-5) | Justification |
|---|---:|---|
| (i) Novelty | 3 | See "Novelty justification" below. The paper's new contributions are lifecycle semantics on top of standard forward lineage: EME as a recorded edge type, deployment-wide suspension, admission and rollback admissibility against withdrawn lineage and evidence, and attested re-admission. It also contributes a careful two-policy measurement of non-adversarial fault spread. The underlying operator is forward reachability, and in both policies it is barely more selective than a time cut. |
| (ii) Rigor | 4 | Raised from 3. The summary claims now match the tables. Revalidation is implemented, tested and placed under Proposition 2. Fault-position strata and post-hoc conditions are disclosed. Prop. 1 is a real proof, and Prop. 2 is an honest proof sketch whose scope (the *recorded* closure, l. 2068) is stated. What remains is local: a residual lineage loss in revalidation (R1), and a Definition 8 tuple that still conflicts with the symbols used everywhere else (R2). |
| (iii) Relevance | 4 | Withdrawing faulty self-written state is a real maintenance problem for agent harnesses. Three lessons are useful to harness designers: "the policy decides what closure costs", "closure is a bound, detection is a filter", and "withdrawal must reach deployments" (ll. 2399-2403). |
| (iv) Verifiability and Transparency | 4 | Strong package: cached responses, generated macros (now including `\SrcLines` = 1,161, which matches `wc -l`), superseded results kept, and post-hoc conditions marked. The adopted-run macros are now used (l. 2269). One point off: the taint guard and revalidation are still outside the projection and the mutation campaign; the authors disclose this (ll. 2063, 2411). |
| (v) Presentation | 4 | The abstract (l. 1680) and the RQ1 box (l. 2301) are calibrated. The exposure direction is consistent (Definition 4, l. 1755; Table I, l. 1802). The running example is fixed (l. 1931). Remaining problems: Definition 8's state tuple (R2), the symbol $a$ used for both revisions and the attestation, and two leftover sentences (R3, R4). |

### Novelty justification

What is new relative to the closest prior work:

- **Provenance (PROV-DM/OPM, noWorkflow, PROV-AGENT).** PROV can express every edge HEARTNESS records, including the EME path, as the paper now concedes (l. 2424). New here: making a run's *loaded context* a mandatory recorded input, so that behaviour-mediated inheritance is in the record at all. Also new: using the record operationally, to refuse admissions, rollbacks and deployments that would reactivate withdrawn lineage. Provenance systems describe; they do not gate a lifecycle.
- **Taint and information-flow control (TaintDroid, CaMeL, FIDES).** These label values within one execution or task. HEARTNESS carries "taint" across tasks and deployments in persistent, LLM-synthesized state, and supports *retroactive* labelling, that is, withdrawal after the fact. The closure is, as the paper says (l. 2430), persistent-state taint propagation with its usual over-tainting. Conceptually this is a transfer, not a new mechanism.
- **Deletion propagation, view maintenance, provenance semirings.** These solve the backward problem or the finer forward problem when the dependency semantics are known. The paper's argument is that an LLM synthesis step reveals no such semantics, so every input must be treated as possibly necessary (l. 2430). The argument is correct and well placed. But it means the forward rule is the coarsest member of a known family, not a new one.
- **Machine unlearning; build invalidation.** Rollback-and-re-evolve is the exact counterpart of unlearning. Build systems invalidate transitively over *declared* dependencies. HEARTNESS's increment is (a) obtaining the dependencies by host recording, because generators do not declare them, and (b) suspension with enforcement where re-execution is impossible.
- **EVOMAL, AgentSpec, VASO.** EVOMAL measures adversarial skill poisoning and gates new skills, but it has no lineage-based withdrawal. AgentSpec and VASO constrain individual actions or skills. HEARTNESS governs how persistent state changes and is undone, and the comparison table (ll. 2436-2456) shows this fairly. The live study complements EVOMAL by measuring non-adversarial spread and adoption rates under two policies. That measurement is new and useful.

The paper therefore offers a coherent and new *combination*: lifecycle semantics plus enforcement plus measurement. No single mechanism is fundamentally new, and the paper's own evidence shows that the headline mechanism (closure) gives little selectivity over a rollback in both studied policies. The contribution beyond rollback is enforcement, and enforcement was not exercised live (l. 2411).

**A score of 4 would require at least one of the following:**

1. **Show the selectivity advantage where it should exist.** Evidence that closure is materially more selective than a time cut, at equal recall, in a harness or policy with selective context assembly. Examples: late faults (after task 12, which the paper itself predicts would widen the gap, l. 2269), or a retrieval-only policy. This would turn "the policy decides what closure costs" from a hypothesis into a demonstrated design lever.
2. **Exercise enforcement under live evolution.** Withdraw mid-evolution, continue evolving, and measure re-admissions, unsafe rollbacks or re-derivations that the guards refuse, against rollback-and-continue. That is the advantage the paper claims over rollback.
3. **A sharper formal contribution.** For example, a mechanized invariant proof that includes EME and experience withdrawal, or a characterisation of which policies make closure strictly cheaper than any time cut.

## Status of round-5 issues

| Issue | Status | Evidence |
|---|---|---|
| **M1** "Every detector had higher F1" | **Resolved** | Abstract (l. 1680): "Every detector was more precise and TF-IDF and the LLM judge had clearly higher F1"; misses range from `\LiveCMissRunsRtwo` (2) to `\LiveCMissRunsRthree` (22) of 42. RQ1 box (l. 2301) has the same calibrated wording. l. 2269: "below every detector's, by a large margin for R2 and R4 and narrowly for R3". Intro (l. 1705): "lost recall mainly where" (was "only"). The R3 precision claim holds (0.12 vs 0.10 on curation propagated runs, macros l. 911/939). |
| **M2** Re-admitted copies lose lineage | **Resolved for direct lineage; narrower gap remains** | `revalidation.py` keeps active non-forbidden sources, maps re-admitted sources to their copies, and keeps experiences whose run context avoided Cl(F). Algorithm 5 (ll. 2023-2037) matches. The new test `test_copy_keeps_clean_lineage_so_a_later_withdrawal_reaches_it` (`tests/test_revalidation.py` l. 80) reproduces my scenario, and it passes. Two transitive cases are still lost (see R1). |
| **M3** Late-fault extrapolation | **Resolved** | l. 2269: "faults after the first composition (task 12) were not sampled; there the next composition is at task 24, so later tasks would be exposed only through memory retrieval and the gap could be larger." Correct. |
| m1 "Evidenced in RQ2" | **Resolved** | l. 2411: re-admission and unsafe rollback "evidenced by the controlled scenarios of RQ2, and refused re-derivation, evidenced by unit tests only". |
| m2 Formal presentation of tainted evidence | **Mostly resolved** | $\Theta$ and $F=W\cup K\cup\{b\mid\expr(b)\cap\Theta\neq\emptyset\}$ are defined (l. 1881). Table II P2/P8 use Cl(F). Algorithm 4 has the experience branch (l. 1990) and uses Cl(F) in Rollback. Table I lists $\Theta$, F (l. 1803). The proof covers experience withdrawal (l. 2071). **Not done:** Definition 8 (l. 1778); see R2. The projection limits (l. 2063) list EME but not experience withdrawal. |
| m3 Scope of "refusing re-derivations" | **Resolved** | The abstract now says "refusing admissions and rollbacks that would reactivate it" (l. 1680). The contribution bullet speaks of "motivated by withdrawn evidence" (l. 1699). |
| m4 H_EME-fail post hoc, n=1 | **Resolved** | Intro l. 1705 ("a variant we defined after seeing the data ... rests on that single run"); Internal validity l. 2388; Lessons l. 2399; conclusion l. 2465. |
| m5 Direction of "exposed to" | **Resolved** | Definition 4 (l. 1755), l. 1757, Table I (l. 1802), l. 1766, l. 2006 are now consistent. |
| m6 H_local / ExpeL caption | **Resolved** | Table VII caption: "ineffective by construction, because agents load only deployed copies" (l. 2239); Lessons l. 2403. The ExpeL by-construction ablation rows are explained in the text (l. 2219) rather than in the Table VI caption (l. 2186), which is acceptable. |
| m7 Running example off-by-one | **Resolved** | l. 1931: "For task 9 (run $r_8$)". |
| m8 Notation clash on T | **Partial** | The tainted set is renamed $\Theta$, and the effects are "$X$" in Algorithm 4. Definition 8 still binds $X$ to accepted proposals and $F$ to external effects (R2). New, small: $a$ is both "one revision" (Table I, l. 1797) and the attestation (l. 2021). |
| m9 Revalidation evaluation wording | **Open** | l. 2388 still says revalidation "was evaluated on the recorded state in a separate process rather than through the controller's admission operators". l. 2041 says the plan equals the engine's execution. Neither says that `plan()` omits the admission guards that `revalidate()` applies afterwards (`_admit` may raise `Rejected`); see R3. |
| m10 Unused adopted-run macros | **Resolved** | Used at l. 2269 (21.19 vs 22.49 for T vs 2.70 for R4). |
| m11 Abstract adoption | **Resolved** | l. 1680: adopted in `\LiveRootAdoptedAll` (74) runs. |
| m12 Implementation size | **Resolved** | `\SrcLines` = 1,161 (l. 55), which matches `wc -l src/heartness/*.py`. |
| m13 Load precondition | **Resolved** | Running example l. 1931; Proposition 1 proof l. 2014; Proposition 2 proof l. 2071. |

## Remaining issues

### R1 (moderate). Revalidated copies still lose transitive and mixed-context lineage, and l. 2021 overstates what is kept

l. 2021 says: "Its lineage is $x$'s lineage with the withdrawn part replaced by $a$ ... A later withdrawal of a clean source of $x$ therefore still reaches $x'$." The second sentence holds for **direct** sources. The first sentence does not hold, because the dropped part of the lineage includes clean ancestry. I ran two probes on the engine, using the `admit` helper from `tests/test_revalidation.py`.

**Probe A: clean ancestry through an uncleared member.**

- Setup: `z` (clean seed) and `m7` (faulty) feed skill `y`; profile `x` derives from `y`.
- Steps: withdraw `m7`; the screen clears `x` but not `y`; revalidate. Then `x~r` has sources `{a}` only.
- Result: withdrawing `z` leaves `x~r` active, and `properties.violations` reports nothing. The original `x` was in Cl({z}).

**Probe B: mixed run context.**

- Setup: run `r2` loaded `{z, m7}`, and its experience `e2` motivated memory `x`.
- Steps: withdraw `m7`; clear `x`; revalidate. `e2` is dropped, because its context met Cl(F), and with it the EME edge from `z`.
- Result: withdrawing `z` leaves `x~r` active.

Both cases are the code's documented behaviour: a source must be active, and an experience must have a context fully outside Cl(F). Neither violates Proposition 2, which is about the recorded closure. But in both, revalidation turns clean ancestry into missing lineage, which is the kind of gap my round-5 M2 was about. In a curation harness, case A is the common one: a cleared profile whose skill stays quarantined.

**Required (either option):**

- **(a) Fix it in the engine.** Also attach to $x'$ the *active frontier* of the dropped lineage. For case A, these are the active, non-forbidden revisions reachable backwards from $x$ through quarantined members. For case B, these are the active, non-forbidden members of the dropped experiences' contexts. Attach them as sources, or as a dedicated `readmittedFrom` edge kind that the closure follows. Add the two probes as tests.
- **(b) Narrow the claim.** Replace "Its lineage is $x$'s lineage with the withdrawn part replaced by $a$" with an exact statement: direct active sources and fully clean experiences are kept, and ancestry that runs through still-quarantined members or through contexts that met Cl(F) is represented only by $a$. Add this to the Limitations (l. 2411) and to the module docstring in `revalidation.py`.

### R2 (minor). Definition 8 still conflicts with the notation used everywhere else

The response says "effects renamed X (no clash with F)" and "Θ, F in Table I". Definition 8 (l. 1778) still reads $\sigma=(\mathcal{E},\mathcal{A},Q,V,X,W,K,\Act,\mathit{Ver},\Dpl,L,F,\Lambda)$. Its gloss is "... validation records, accepted proposals, withdrawn ... external effects, ...". So:

- $X$ = accepted proposals;
- $F$ = external effects;
- $\Theta$ is absent.

Meanwhile, l. 1881 defines $F$ as the forbidden roots, Algorithm 4 returns "external effects $X$", and the proof (l. 2071) treats $\Theta$ as part of the state. **Required:** rename the accepted-proposal component, use $X$ for effects, add $\Theta$, and keep $F$ only as a derived set (it is not a state component). Optionally, rename the attestation (e.g. $\alpha$) to avoid the conflict with "$a$, one revision" (Table I, l. 1797).

### R3 (minor). `plan()` versus the engine's admission guards

Two sentences contradict each other:

- l. 2388: revalidation was evaluated "in a separate process rather than through the controller's admission operators";
- l. 2041: "a test checks that the plan equals the engine's execution".

In the code, `revalidate()` passes each copy through `_admit`, which applies the guards and may reject a copy. `plan()` checks only dependency availability. The two agree in the live data only because no copy is rejected there, presumably because no contracts are declared. **Required:** add one clause saying that `plan()` checks dependency availability only, that the engine additionally applies the admission guards, and why the guards do not bind in the live harness.

### R4 (minor). Projection limits

l. 2063 says the projection "omits text, ... effects, EME edges and multiple deployment identities". Add **experience withdrawal (the taint guard)** and **revalidation**. Neither is covered by the projection or the mutation campaign. Both are covered by Proposition 2 and by unit tests only.

### R5 (observation, no change required). Positioning of the headline

Under the ExpeL-style policy, closure is identical to the time cut. Under curation, closure is strictly smaller in 42 of 75 runs, by about 1.4 revisions per run on average (20.79 vs 22.20). Its advantage over rollback is therefore currently the *enforcement* semantics, which the live study does not exercise (l. 2411). The paper now says this plainly (ll. 1705, 2016, 2399, 2463), and I consider the positioning honest. I list it only because it is what limits the novelty score (see the justification above).

## Recommendation

**Minor revision.**

All three round-5 major issues are resolved:

- the F1 claims match the tables;
- re-admitted copies keep their direct clean lineage, with a test;
- the late-fault sentence is now correct.

The minors are almost all done.

Before acceptance:

- **R1:** close the residual transitive and mixed-context lineage loss in revalidation, or state it precisely. This is a small engine change plus two tests, or a two-sentence scoping.
- **R2:** fix Definition 8, which the response reports as fixed but is not.
- **R3, R4:** add two one-clause scope statements.

None of these needs new experiments. Once they are done, I would recommend acceptance.
