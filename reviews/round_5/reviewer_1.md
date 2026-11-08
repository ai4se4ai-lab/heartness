# Round 5 -- Reviewer 1 (novelty, soundness, positioning)

This is an internal automated review of a draft, not real IEEE TSE peer review.

Scope: the full manuscript `docs/TSE/main.tex` (22 pages; the log has only font-shape warnings). Numbers are taken from the generated macro block (ll. 36-1653). I checked the new code in `src/heartness/{revalidation,engine,model,graph,properties}.py`, the tests (`tests/test_revalidation.py`, `tests/test_eme.py`; 53 tests pass), `scripts/mutation.py`, `experiments/live/harness.py` and `experiments/live/supplement.py`. Line numbers refer to `main.tex`.

## Summary

HEARTNESS is a controller for the persistent state (memories, skills, profiles) that self-evolving LLM harnesses write for themselves. It has the following parts:

- immutable revisions;
- host-recorded exposure (synthesis sources, use dependencies, and experience-mediated exposure, EME);
- guarded admission;
- withdrawal of a revision **or, new in this round, of an experience**, which suspends the exposure closure in every deployment and constrains later admissions and rollbacks;
- closure-bounded revalidation, **now implemented** as a composition of ordinary operators under an attestation revision;
- two propositions: closure is bounded by a time cut, and P2/P8 form an inductive suspension invariant;
- bounded model checking of a finite projection with two encodings and witness replay;
- a log-replay monitor.

The live study (200 runs, five 7-16B generators, HumanEval+, ExpeL-style and curation policies) is unchanged in design. Revalidation was re-evaluated through the shared `plan()` function, and a post-hoc condition H_EME-fail was added.

This round addressed my round-4 concerns seriously. Experience withdrawal closes the re-derivation gap I raised (M2). The attestation is no longer prose: it exists in the metamodel, the engine and the tests (M6). The unfavourable significance tests are reported (M1). The EME trade-off is in the abstract and has a configurable variant (M4). The positioning sentences are now accurate (M5).

Three problems remain, and one of them goes back to my own round-4 wording:

1. **The F1 comparison is overstated.** The new summary claim that "every content detector had higher F1" under both policies is false for the embedding detector. I suggested that phrasing in round 4, and I was wrong.
2. **Re-admitted copies lose lineage.** Revalidation drops every lineage edge of a re-admitted copy except the attestation, so a later withdrawal of one of the copy's other, clean-looking sources does not reach it. I reproduced this on the engine.
3. **The late-fault extrapolation is wrong.** The new sentence on faults after the first composition predicts the opposite of what this harness would do.

All three can be fixed without new experiments.

## Scores

| Criterion | Score (1-5) | Justification |
|---|---:|---|
| (i) Novelty | 3 | Unchanged in substance. The contribution is lifecycle semantics on top of standard lineage: admission against withdrawn lineage, deployment-wide suspension, rollback admissibility, and now evidence (experience) withdrawal and attested re-admission. It also includes a careful two-policy measurement of non-adversarial fault spread. The closure itself is forward reachability, and the paper now says so accurately (ll. 1685, 2413, 2419). The data show closure equal to or slightly below a time cut. |
| (ii) Rigor | 3 | Improved: experience withdrawal is implemented, tested and folded into Proposition 2. The revalidation evaluated is now the one the engine executes. Unfavourable tests are reported, and closure vs. cut is stratified by fault position. Remaining issues: an F1 claim the tables contradict (major 1); a lineage gap in revalidation that the invariant does not see, because it concerns lineage that is no longer recorded (major 2); an incorrect analytical extrapolation (major 3); and an "evidenced in RQ2" claim for re-derivation refusal that RQ2 does not contain (minor 1). |
| (iii) Relevance | 4 | Withdrawing faulty self-written state is a real SE maintenance problem. The lessons "report adoption", "the policy decides what closure costs" and "closure is a bound, detection is a filter" are useful. |
| (iv) Verifiability and Transparency | 4 | Exemplary package: cached responses, generated macros, `make live-fir`, and disclosure of superseded campaigns and post-hoc conditions. Revalidation now shares `plan()` with the engine, and a test checks that they agree. Points off: the new taint guard is outside the mutation campaign, E-G and the projection; and the adopted-run macros (`\LiveCAdopt*`) are still generated but unused. |
| (v) Presentation | 4 | Much improved. The abstract is 249 words and calibrated except for the F1 clause. The intro components are listed, and the running example is aligned with the code. Remaining problems are local: notation clashes (T), the direction of "exposed to", a task/run off-by-one in one running-example paragraph, and Algorithm 2/4 and Table II not reflecting tainted evidence. |

## Status of round-4 issues

| Issue | Status | Evidence |
|---|---|---|
| **M1** Summary sentences misstate the detector comparison; unfavourable tests omitted | **Partial** | The tests are now reported (l. 2241): F1 vs R2 lower in all 42 runs, p<0.001; vs R4 lower in 36, higher in 6, p<0.001; collateral vs R2 73 runs, vs R4 75 runs. Per-detector misses are named (abstract l. 1672, RQ1 box l. 2290: R3 22, R4 13, R2 2). "As rollback and reset did" was added (l. 2290, l. 2452). **However**, the abstract (l. 1672), the RQ1 box (l. 2290) and l. 2241 now say that *every* detector had higher F1 under both policies. The frozen embedding detector R3 has F1 0.16 vs H 0.18 under curation (Table VII rows, l. 1631/1634; H higher in 27 runs, lower in 14, p=0.091) and 0.50 vs 0.48 under ExpeL (H higher in 5, lower in 3). My round-4 text proposed this wording; it was my error, and it now needs correcting (major 1). |
| **M2** Re-derivation from the faulty experience passes every guard | **Resolved** | `engine.py` Withdraw branch for experiences adds `s.tainted`, withdraws motivated revisions with their closure, and `State.forbidden_roots()` makes future motivated revisions forbidden. Tests: `test_withdrawing_an_experience_blocks_relearning_from_it` and `test_withdrawing_only_the_revision_still_admits_relearning` (`tests/test_eme.py`). Proposition 2 uses F including tainted motivation (l. 2057), and new evidence is scoped out (l. 1959, l. 2400). The formal presentation is incomplete (minor 2), and the abstract's "refusing ... re-derivations" holds only when the experience, not the root revision, is withdrawn (minor 3). |
| **M3** Value over rollback argued, not measured | **Resolved by scoping** | The continuation experiment was not run. The authors' reason is plausible: both policies filter suspended state themselves, so the guards would not fire (`harness.py`, merge uses `b in s.active`). "Needs no fault time" is dropped (l. 2006, l. 2134). Deployment reach is restated as a requirement any remedy must meet (l. 2006, l. 2392). Enforcement after the fact is scoped to controlled scenarios (l. 2188, l. 2400, l. 2454), and rollback-and-re-evolve is discussed with its precondition (l. 2188, l. 2419). Acceptable. The "evidenced in RQ2" wording overclaims for re-derivation (minor 1). |
| **M4** EME trade-off only deep in IV-B | **Resolved** | Abstract (l. 1672: "at a large cost in collateral"); intro (l. 1697); cause attributed to "the EME rule applied to a broadcast context" (l. 2258) and in Lessons (l. 2388). H_EME-fail added (Table VII l. 1642: 17.24 suspended, recall 1.00, F1 0.22). One caveat on how it is reported is in minor 4. |
| **M5** Positioning overstatements | **Resolved** | PROV can express the EME path; the claim is narrowed to recording and use in admission (l. 1685, l. 2413). EVOMAL: "a candidate remedy for the non-adversarial case" (l. 2410). Deletion propagation is related to view maintenance and semirings (l. 2419; `gupta1993views` and `green2007semirings` checked in `references.bib`, ll. 329-345), with the all-inputs argument. "Exact removal" is replaced by rollback-and-re-evolve. |
| **M6** Attestation lineage does not exist | **Resolved, with a new soundness gap** | `src/heartness/revalidation.py` admits an `attestation` revision (new kind in `model.py` `KINDS`) as an authorized seed and re-admits copies with `sources=(attestation.id,)`. `test_withdrawing_the_attestation_withdraws_every_readmission` passes. Algorithm 5 (ll. 2013-2027) matches the code. The supplement uses the same `plan()` (`supplement.py` l. 53). The fix introduces a lineage loss for the copy's *other* sources (major 2). |
| m1 Load precondition | **Partial** | It is cited in the Proposition 2 proof (l. 2060) and in Lessons (l. 2396). It is not in Section III-C or Algorithm 1 (ll. 1902-1920), and Proposition 1's proof (l. 2004) still says only "the run precedes its experience". |
| m2 Rollback and deployments | Resolved | l. 1996: "Rollback changes Act only ... reaches agents only when it is redeployed." |
| m3 Cut definitions | Resolved | l. 2006. |
| m4 "prove" | Resolved | Abstract: "We show"; Prop. 2 is a "proof sketch" (l. 1702, l. 2059). |
| m5 Proposition 2 name | Resolved | "Suspension invariant", stated as about the *recorded* closure (l. 2057). |
| m6 Fault position vs composition schedule | **Partial / new error** | Stratified (l. 2258: 0/15, 33/45, 9/15), but the added extrapolation "for a fault after the first composition we would expect no gap at all" is incorrect for this harness (major 3). |
| m7 H_faulty misses vs ambiguous root labels | Resolved | l. 2258: in all 3 runs the judges disagreed on the root. |
| m8 Adopted-run results | **Open** | `\LiveCAdopt*` macros are still generated in the macro block, and none is used in the body (only `\LiveCAdoptedAmb`/`\LiveEAdoptedAmb`). Report or drop. |
| m9 By-construction rows | **Mostly resolved** | The Table VII caption marks H_¬dep and H_local (l. 2228), and Lessons phrases deployment reach as a design requirement (l. 2392). The Table VI (ExpeL) caption (l. 2175) does not mark H_¬EME/H_¬dep/H_local. "H_local is null by construction" is inaccurate under curation: its row shows 15.59 suspended and recall 0.03 (l. 1640), because memories are loaded from Act, not from deployments (`harness.py` `context()`). See minor 6. |
| m10 Judge receives all roots | Resolved | l. 2133. |
| m11 Abstract adoption rate | **Open** | The abstract (l. 1672) still gives spread (52/150) but not adoption (21+53 = 74/150 roots adopted). |
| m12 E-G near-definitional | Resolved | l. 2299. |
| m13 E-S claim qualified | Resolved | Removed from the abstract; qualified in the RQ2 box (l. 2339). |
| m14 "Model-driven" title | Resolved | Justified as models@run.time with citation (l. 1872). Acceptable. |
| m15 Line counts | Resolved for `experiments/live` | Macro `\LiveHarnessLines` = 1,732, matching `wc -l`. New, small: "about 1,000 lines in `src/heartness`" (l. 2090) is 1,146 now that `revalidation.py` was added. |
| m16 Table VIII qualifiers | Resolved | l. 2443: "(recorded run contexts)", "(recorded lineage)"; version-control row added (l. 2434). |

## Remaining major issues

### M1. "Every content detector had higher F1" is contradicted by the tables for the embedding detector

The claim appears in the abstract (l. 1672: "every content detector had higher F1"), the RQ1 box (l. 2290: "Content detectors had higher F1 under both policies") and l. 2241 ("every detector had higher F1 than \sys{}"). The tables say otherwise for R3 at its frozen threshold:

| Policy | H F1 | R3 F1 | Paired H vs R3 (higher / lower) | Holm p |
|---|---:|---:|---|---|
| ExpeL (l. 1602, 1605) | 0.48 | 0.50 | 5 / 3 | 0.945 |
| Curation (l. 1631, 1634) | 0.18 | 0.16 | 27 / 14 | 0.091 |

Under curation, collateral against R3 is also nearly balanced (H worse in 41, better in 31; `\LiveCTestCollRthreeP` = 0.048). I proposed the "every detector" wording in round 4 without checking R3; that was my error, and I apologise to the authors for it. The correct statement is the following:

- TF-IDF and the LLM judge had substantially higher F1 than closure under both policies.
- The embedding detector was comparable in F1 under both policies, with lower recall under curation.
- Every detector was *more precise*. That part holds (R3 precision 0.12 vs 0.10 under curation; 0.39 vs 0.33 under ExpeL).

A related point: the intro (l. 1697) says that detectors "lost recall *only* where faulty advice was folded into larger artifacts". R4 also missed contaminated *insights* under ExpeL (recall 0.90, l. 1603; l. 2204), so drop "only" or add the exception.

**Required:** fix the abstract, the intro sentence, l. 2241 and the RQ1 box.

### M2. Revalidated copies sever all lineage except the attestation, so later withdrawals of their other sources miss them

Algorithm 5 (l. 2022) and `revalidation.py` give a re-admitted copy x' the following:

- `sources=(attestation.id,)`;
- no experiences;
- dependencies remapped.

The original x keeps its lineage but stays quarantined, and no edge leads from x (or its sources) to x'. As a result, x' is a verbatim copy of content synthesized from src(x), but it is no longer reachable from src(x) or expr(x). Suppose a *different* source or experience of x is later withdrawn: a second faulty memory, or the screen's own root later found to be wider than thought. The copy then stays active and deployed. I reproduced this on the test harness of `tests/test_revalidation.py`:

1. withdraw `m7`;
2. revalidate with `k1` cleared;
3. then withdraw `m6`, the other source of `k1`.

Result: `k1~r` stays active and in `D1`, and `properties.violations()` reports nothing. The same holds after withdrawing experience `e7`, which is arguably intended in that case.

Proposition 2 is not violated, because it concerns the *recorded* closure (l. 2057). But revalidation is the step that makes the record lossy. The statement at l. 2011 ("the lineage of x' is kept in the graph rather than outside it") is true only for the attestation edge. In a harness where revalidation is routine, every re-admitted skill or profile becomes a lineage root for all purposes except the attestation. This undercuts the paper's main argument that recorded lineage, unlike detection, gives guarantees.

**Required (either):**

- **(a) Fix it in the engine.** Keep the non-withdrawn lineage on the copy, e.g. src(x') = {a} ∪ (src(x) \ Cl(R)) and expr(x') = expr(x) \ T, while not re-creating edges from Cl(R). Alternatively, add a `readmits(x', x)` edge that the closure follows for every root set that does not already contain x via R. Add a test for the scenario above.
- **(b) State the limitation explicitly.** Put it in Section III-F and Limitations: a re-admitted revision is protected against later withdrawal only through its attestation, not through its original sources or experiences.

Option (a) is preferable and appears small.

### M3. The new extrapolation for faults after the first composition is incorrect for this harness

l. 2258 says that "for a fault after the first composition we would expect no gap at all" between closure and the time cut. In `experiments/live/harness.py`:

- skills enter deployments only at composition (`compose()`, l. 271: `Deploy` with `[pid, *chosen]` at tasks 12 and 24);
- every task loads its deployment's profile;
- memories are retrieved from Act by similarity (`context()`).

For a fault at, say, task 14, the deployed profile p12 and skills k0/k1 are *not* in the closure. The root's merged skill (task 18) is not deployed until the task-24 composition, which happens after the last task. Exposure after the fault therefore runs only through memory retrieval and reflection sources, which is exactly the regime of tasks 8/9 that produced the gap. The time cut, by contrast, suspends every later memory, k2, k3 and both p24 profiles. One would therefore expect a *larger* relative gap for late faults, not none. This is also what the threats section implies (l. 2377: "early faults ... inflate closure sizes relative to late faults").

This matters for positioning. The headline "closure is barely more precise than rollback" partly reflects the three fault positions (2, 8, 9), all before the first composition. The text currently suggests that the result would only get stronger with later faults.

**Required:** remove or correct the sentence. State that fault positions after task 12 were not sampled and that, in this harness, they would likely widen the closure-cut gap. If feasible, report even a small set of late-fault runs; the response cache makes the analysis side cheap, but generation is needed, so I do not make this a condition.

## Minor issues

1. **"Evidenced in RQ2" (ll. 2188, 2400, 2454).** RQ2's E-G challenges, E-M projection, E-R scenarios and the mutation campaign (`scripts/mutation.py`) contain no experience withdrawal or re-derivation case; the only evidence is two unit tests in `tests/test_eme.py`. Either add a re-derivation challenge to E-G and a taint-guard mutant (e.g., `forbidden_roots` returning `withdrawn | quarantined`) or say "unit tests and controlled scenarios".
2. **Formal presentation of tainted evidence.** Definition 8 (l. 1770) omits T from σ. Table II P2/P8 (ll. 1882, 1888), Algorithm 2 line 12 (l. 1945) and Algorithm 4 line 3 (l. 1988) still use Cl(W∪K), whereas the engine (`_safe` → `forbidden_roots()`) and Proposition 2 (l. 2057) use Cl(F). Algorithm 4 has no experience branch. The notation table (ll. 1785-1803) lacks T. The projection's omissions (l. 2054) should also list experience withdrawal.
3. **Scope of "refusing ... re-derivations" (abstract l. 1672; contribution l. 1692).** This holds only when the operator withdraws the *experience*. Withdrawing the root revision, which is what H does in the live study, still admits re-learning (`test_withdrawing_only_the_revision_still_admits_relearning`). Say "when the experience is withdrawn".
4. **H_EME-fail is post hoc with n=1 for recall.** "Kept full recall" (intro l. 1697; Lessons l. 2388) rests on the single EME-only run, whose task had failed, and the condition was designed after seeing it. Under curation the corrupted experience is a failure by construction (`harness.py`: `passed, feedback = False, ...`). Add "in the one run where EME mattered; post hoc" in both places.
5. **Direction of "exposed to".** Definition 4 (l. 1747) reads x ⇝ b as "x is directly exposed to b" (x was shown to b's generator), and l. 1749 says "m9 is exposed to k1". Elsewhere "b is exposed to x" is used (l. 1996 "any revision later exposed to these", l. 2258 "every later experience ... is exposed", l. 2188). Pick one direction; "b is exposed to x" is the natural reading.
6. **H_local "null by construction" (caption l. 2228; Lessons l. 2392).** Under curation H_local suspends 15.59 revisions per run with recall 0.03 (l. 1640), because memories are loaded from Act. It is null for profiles and skills, not overall. Under ExpeL it is null (l. 1611). Also mark the ExpeL by-construction rows in the Table VI caption (l. 2175).
7. **Running example off-by-one (l. 1922).** "For task 8, ... Load(r_8, {..., m_7, ...})" contradicts the code indexing stated at l. 1732 and l. 1738: m_7 is written after task 8, and run r_8 is task 9. It should be "For task 9".
8. **Notation clash.** T denotes the tainted-experience set (l. 1872, l. 2057), the time-cut baseline (l. 2134 onward) and the frozen texts in Algorithm 1 (l. 1914). Rename one or two of these.
9. **Revalidation evaluation wording (l. 2377).** "Rather than through the controller's admission operators" is now half-true: the plan is the engine's, but contract checks in `Accept` are not in `plan()`. Add one clause saying that `plan()` omits the capability-contract check, which does not bind in the live harness (no contracts declared).
10. **Unused macros (m8 of round 4).** Report the adopted-run results in one sentence or drop `\LiveCAdopt*` from the generator.
11. **Abstract adoption (m11 of round 4).** Add "the root adopted the fault in 74 of 150 runs".
12. **Implementation size (l. 2090).** `src/heartness` is 1,146 lines; generate it as a macro as was done for the harness.
13. **Load precondition (m1 of round 4).** Add it to Section III-C / Algorithm 1 and to Proposition 1's proof (l. 2004).

## Recommendation

**Minor revision.**

The round-4 major issues are resolved in substance: experience withdrawal and the attestation exist, and they are tested and covered by Proposition 2; the summary sentences report unfavourable results; and the claims about advantages over rollback are scoped. What remains is local but must be fixed before acceptance:

- the F1 claim for the embedding detector (M1, text only; the error originated in my round-4 suggestion);
- the lineage loss of revalidated copies (M2, a small engine change plus a test, or an explicit limitation);
- the incorrect late-fault extrapolation (M3, text only).

The minors are editorial or small consistency fixes. With these done, I would recommend acceptance.
