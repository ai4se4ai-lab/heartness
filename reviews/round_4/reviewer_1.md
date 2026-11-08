# Round 4 -- Reviewer 1 (novelty, soundness, positioning)

This is an internal automated review of a draft, not real IEEE TSE peer review.

Scope: the full manuscript `docs/TSE/main.tex` (compiles to 21 pages; the only log warnings are font-shape substitutions), with numbers read from the generated macro block (ll. 36-1569). I checked selected points against `src/heartness/{engine,graph}.py` and `experiments/live/run.py`. Line numbers below refer to `main.tex`.

## Summary

The paper presents HEARTNESS, a controller for the persistent state that self-evolving LLM agent harnesses write for themselves. It has the following parts:

- immutable revisions;
- host-recorded exposure (synthesis sources, use dependencies, and experience-mediated exposure, EME);
- guarded admission;
- closure-based withdrawal across deployments, with rollback admissibility;
- closure-bounded revalidation;
- two propositions: closure is bounded by a time cut, and P2/P8 are inductive;
- bounded model checking of a finite projection with two encodings and witness replay;
- a log-replay monitor.

The live study has 200 runs: five 7-16B open-weight generators, HumanEval+, and two policies (ExpeL-style insight lists and a layered curation policy). It shows the following:

- **Spread.** A single corrupted feedback message spreads beyond its root in 52/150 faulty runs (10/75 ExpeL, 42/75 curation).
- **Recall.** Closure-based withdrawal leaves zero residual contamination in every run.
- **Closure versus rollback.** Under ExpeL, closure is identical to a rollback to before the fault (T) in 75/75 runs. Under curation it is only slightly smaller: 20.79 vs 22.20 revisions per run, strictly smaller in 42 runs, 106 revisions spared in total.
- **Precision.** H's precision is 0.10 under curation, the same as T's.
- **Detectors.** Content detectors have much higher F1 under both policies. Their recall drops under curation for the embedding detector and the LLM judge, but not for TF-IDF at the frozen threshold.
- **EME.** EME edges are the only lineage of one contaminated revision in one run. They raise collateral in 55 runs.
- **Behaviour.** Held-out pass@1 cannot discriminate between remedies, because learned state never beats the seed-only harness.

This revision is a substantial improvement. My central round-3 objection was that the time-cut, rollback and reset baselines were missing. They are now in both tables, Proposition 1 explains the relation, and the paper states plainly that under ExpeL the closure equals the time cut. Proposition 2 closes most of my concern about formal coverage of dynamic EME edges, and writing it exposed a real engine bug that was fixed. The related-work section now covers IFC/taint, deletion propagation, unlearning, build systems and sagas. The body of Section IV-B is honest and well calibrated.

The remaining problems are concentrated in four places:

1. The summary sentences (abstract, introduction, RQ1 box, conclusion) describe the detector comparison more favourably to HEARTNESS than the tables do, and the unfavourable significant tests are not reported.
2. The advantages claimed over a rollback (enforcement against re-admission and against later rollbacks, deployment reach, no need for the fault time) are argued, not measured. One of them does not hold.
3. A headline guarantee ("refusing admissions ... that would reactivate it") has a semantic gap: the faulty experience itself can be re-learned from.
4. Revalidation's "attestation" lineage is described as a mechanism, but no operator or code implements it.

## Scores

| Criterion | Score (1-5) | Justification |
|---|---:|---|
| (i) Novelty | 3 | The positioning is now accurate and the contribution is clearer: lifecycle semantics (admission, deployment-wide suspension, rollback admissibility) on top of standard lineage, plus a careful two-policy measurement of non-adversarial fault spread and remedies. The mechanisms themselves are modest. Closure is forward reachability (taint, build invalidation). EME is PROV `used` plus `wasGeneratedBy`, applied to run contexts. The data now show that recorded closure gains little over a time cut in both policies (0 and about 6% of the cut). Two related-work sentences still overstate novelty (major 5). |
| (ii) Rigor | 3 | Major gains: the T/A/H_faulty baselines, Proposition 1, the inductive Proposition 2, by-construction ablations removed from the test family, and per-run win/loss counts. Remaining gaps: (a) the significant tests that go against H under curation (F1 vs. R4: 6 higher, 36 lower, p<0.001; collateral vs. R4: worse in 75/75) are computed but not reported; (b) the guarantees that distinguish H from T are never exercised in the live study, because withdrawal is applied only after the last evolution task (`run.py` l. 294); (c) re-derivation from the withdrawn root's own experience is admitted; (d) the revalidation attestation is unimplemented. |
| (iii) Relevance | 4 | Withdrawing faulty state from self-modifying harnesses is a real SE maintenance problem. The lessons "report adoption", "the policy decides what closure costs" and "measure behaviour with signatures" are useful to the community. |
| (iv) Verifiability and Transparency | 4 | Exemplary replication package: cached responses, generated macros, `make live-fir`, and disclosure of superseded campaigns and post-hoc conditions. Points off: revalidation is evaluated by set restoration rather than through the controller, and its attestation exists only in prose; results on adopted runs are computed (`\LiveCAdopt*`) but never shown. |
| (v) Presentation | 3 | The body is clear and the running example now matches a real run. But the abstract, introduction and conclusion characterize the detectors under curation in a way the tables contradict (major 1). Some long result paragraphs (ll. 2143-2162) would read better with one small "closure vs. T vs. H_noEME" table. |

## Status of round-3 issues

| R3 issue | Status | Comment |
|---|---|---|
| 1. Chronological cut / pre-fault rollback / reset baselines; lemma | **Resolved** | T and A appear in both tables. Proposition 1 (l. 1904) is proved. Text at l. 2090 states H = T in 75/75 ExpeL runs, and l. 2160 reports the curation gap. One residual: T is defined relative to the corrupted *experience* (l. 2036) but Proposition 1 relative to the earliest *root* (l. 1905). See minor 3. |
| 2. Ablations identical by construction | **Mostly resolved** | They are out of the Holm family (l. 2051) and the text says "by construction" (l. 2110). Table V rows (ll. 1527-1529 of the macro block) are still unmarked. H_local is still a design tautology of this harness (l. 2088, l. 2295). See minor 9. |
| 3. Behavioural overstatement; seed-only reference | **Resolved in text; underlying limitation stands** | The seed-only references (0.63 and 0.62) are reported, "consistent direction" is gone, and per-run counts are given. The consequence (no remedy's cost can be priced) feeds major 3. |
| 4. Roots; who identifies the root | **Partially resolved** | Roots are described (l. 2007) and H_faulty added. The judge still receives the concatenated text of all roots (`run.py`, `root_text`). Withdrawal of an *experience* was not formalized, which is now the source of a soundness gap (major 2). Root localization was declined, which is acceptable as scoped (l. 2356). |
| 5. Thresholds | **Resolved** | Full F1-threshold curves are given (Figs. 3-4), and the oracle bound is stated correctly (l. 2106). |
| 6. Novelty / PROV / missing literatures | **Mostly resolved** | New subsection at l. 2321 and EVOMAL softened (l. 1611). Two overstatements remain: PROV "records what a generator was given, not the indirect channel" (l. 1601), and capture alone does not give "the experience-mediated channel" (l. 2316). Two new ones were introduced: "exact removal" (l. 2322) and "contributes the missing remedy" (l. 2313). See major 5. |
| 7. Formal coverage of new parts | **Largely resolved** | Proposition 2 is sound as sketched (I checked the Accept, Withdraw and Load cases against `engine.py`). Def. 8 now lists Retire and Quarantine, and the scopes are stated (ll. 2205, 2240). Two gaps remain: the Load precondition the proof relies on appears only in Lessons (l. 2299), not in the semantics or Algorithm 1; and the rollback/deployment interaction is still unstated. See minor 1 and minor 2. |
| 8. Revalidation unspecified | **Partially resolved** | Algorithm 5 and Section III-F are added, and the post-hoc evaluation is disclosed (l. 1933, l. 2280). The attestation-based re-withdrawal (l. 1915) has no operator, property or implementation, and `src/heartness` contains no attestation concept (major 4). The recommendation was correctly softened (l. 2108, l. 2293). |
| 9. Placeholder content | **Partially resolved** | The RQ1 box separates the policies and the abstract states the precision cost. The adoption rate (74/150 roots adopted) is missing from the abstract. The summary sentences about detectors are miscalibrated (major 1). |
| Minors 1-28 | Mostly fixed | Still open: minor 26 (the "model-driven" title; l. 1573) and minor 25 (E-G near-definitional; l. 2202). |

## Major issues

### M1. The summary sentences misstate the detector comparison under curation, and the unfavourable significant tests are omitted

The curation table (macro block, ll. 1541-1556) gives, on propagated runs:

| Remedy | F1 | Precision | Recall | Suspended per run |
|---|---:|---:|---:|---:|
| H | 0.18 | 0.10 | 1.00 | 20.79 |
| R2 TF-IDF (frozen threshold) | 0.36 | 0.24 | 0.99 | 11.27 |
| R4 LLM judge | 0.69 | 0.78 | 0.79 | -- |

TF-IDF at the frozen threshold missed contamination in only 2 of 42 runs. The paired tests the paper computes show H's F1 lower than R4's in 36 runs and higher in 6 (`\LiveCTestFoneRfourP` = <0.001). H also has more collateral than R4 in 75/75 runs (p<0.001). Neither result appears in the text: of the curation test macros, only the recall comparisons, which favour H, are cited (l. 2143).

Against these numbers:

- the introduction (l. 1605) says detectors were "the worse one when [advice] was folded into larger artifacts";
- the abstract (l. 1588) says they "missed it in up to 22 of 42 runs", which is the embedding detector, the weakest, with oracle-best F1 0.21;
- the conclusion (l. 2354) says they "fail exactly where synthesis dilutes or rewrites it".

The accurate statement is narrower. Under curation, two of three detectors lost recall, but every detector had higher F1 and lower collateral than closure, and TF-IDF at a low threshold kept recall 0.99 with about half the suspensions. The RQ1 box (l. 2193) and the "both policies" paragraph (l. 2168) have the same slant. The latter also says "only closure-based withdrawal ... never left a contaminated derivative loadable", although T and A also never did; to its credit, that paragraph says so in the next clause, but the conclusion (l. 2354) drops the qualifier.

**Requested changes.**

- Report the H-vs-R4 and H-vs-R2 F1 and collateral tests for curation alongside the recall tests at l. 2143.
- Rewrite the abstract, l. 1605, the RQ1 box and l. 2354 to say "lower recall" rather than "worse"/"fail". Name which detector missed how often (R3 22, R4 13, R2 2 of 42), and state that every detector had higher F1 than H under both policies.
- In l. 2354, add "as did rollback and reset" after "only closure-based withdrawal removed every contaminated derivative".

### M2. "Refusing admissions that would reactivate it" does not cover re-derivation from the faulty experience

The admission guard (Alg. 2 l. 12; `engine.py::_safe`) rejects a candidate only if it lies in Cl(W ∪ K). The closure starts at *revisions*. An experience e enters the closure only through EME edges from the context of the run that produced e. Consider a new revision b whose only motivation is the corrupted experience e_c (the experience that motivated the withdrawn root), where the run behind e_c did not load anything in the closure. Then b is not in Cl(W ∪ K), so b is admitted. This is exactly what happens if a policy re-reads its experience pool, as the original ExpeL does across extraction passes, or if a periodic consolidation re-summarizes old experiences. The same faulty lesson is then re-learned from the same corrupted feedback and passes every guard.

In this live study the policies consume each experience once, so the gap was not hit. But the abstract (l. 1588) and contribution (iv) (l. 1603) state the guarantee without this qualification. In round 3 (concern 4) I asked for withdrawal of an experience as a first-class operation. The response declined it as part of root localization, but these are separate issues.

**Requested changes.** Either:

- (a) add an operator that withdraws or taints an experience, so that later revisions with that experience in expr(·) fall under the guard; include it in Proposition 2 (the proof extends directly) and in the projection's property set; or
- (b) scope the claim explicitly in the abstract, contribution (iv), Section III-E and Limitations ("refuses derivatives of withdrawn lineage; it does not prevent the policy from re-deriving the same content from the same experience or from new evidence").

Whichever you choose, note that re-learning from *new* evidence (a second corrupted message) is out of scope for any lineage-based guard.

### M3. Beyond a rollback, the value of HEARTNESS is argued but not measured

Proposition 1 plus the data establish that closure is at most a time cut, and in practice almost equal to it:

- **ExpeL:** 0 revisions spared in 75 runs.
- **Curation:** 1.41 revisions per run of 22.2 (about 6%), all of them memories written before the first profile composition (l. 2160).
- **Behaviour:** pass@1 cannot price the spared revisions under either policy (seed-only 0.63/0.62 ≥ clean 0.61/0.61). Reset (A) therefore matches H on every measured outcome except a structural count of clean revisions whose usefulness is not shown.

The paper then rests H's advantage over T on three properties (l. 1910, l. 2036, l. 2090):

1. **"Needs no fault time."** This does not hold as stated. Withdrawal requires the root revision, and the root's acceptance event (and its motivating experience) are in Λ, so T is computable from the same input the operator gives H. The argument needs an actual case in which the root is known but its time is not, or it should be dropped.
2. **"Reaches every deployment."** This is a property of the harness's deployment model, not of closure. A snapshot rollback that is redeployed reaches every deployment equally. H_local (l. 2088) shows only that this harness keeps separate deployment copies.
3. **"Enforced against later re-admission and rollback."** This is the genuine difference, but the live study never exercises it. `run.py` (ll. 287-296) applies Withdraw to a deep copy after the last evolution task and does not continue evolution. The only evidence is the synthetic E-G/E-R scenarios on the running example (ll. 2202, 2273).

**Requested changes.**

- Add a continuation experiment. Withdraw at a mid-run point (e.g., after task 12 or when the oracle first labels a derivative), keep evolving to task 24 under H and under T, and report: rejected admissions and rollbacks under H; re-contamination under T (does the next profile composition or extraction re-derive the fault from state T kept or from re-exposure?); and spared useful work. The response caching and 6-minute runs (`\LiveCEvolveMinutes`) make this inexpensive.
- Drop or substantiate argument 1, and restate argument 2 as a harness-design requirement rather than an advantage over rollback.
- Discuss a fourth baseline that the unlearning and build-system analogies (l. 2322) imply: **rollback and re-evolve** (replay post-fault experiences without the corrupted one, i.e., SISA-style retraining or a build-system rebuild). The paired clean run is precisely this counterfactual and is already recorded (pass@1 0.61 under both policies), at a cost of about one evolution run. The paper should say when re-evolution is impossible (non-replayable tasks, external effects, user-specific experiences), because that is where suspension without recomputation earns its place.

### M4. EME is presented as a key contribution, but in the data it is the main cause of closure's imprecision; the trade-off appears only deep in Section IV-B

Under curation, removing EME edges reduces suspension from 20.79 to 14.39 per run, raises F1 from 0.18 to 0.31, and leaves one contaminated revision loadable in one run (l. 2162). Since T suspends 22.20, without EME the closure is about 35% below the time cut, against about 6% with it. So it is EME, not the policy alone, that turns "every task loads its profile" (l. 2160) into "every later memory is in the closure". The text at l. 2160 and the lesson at l. 2291 attribute the time-cut behaviour to how the harness broadcasts context ("not by the containment mechanism"). Strictly, it is the interaction of broadcast contexts with the EME rule, which *is* part of the containment mechanism. Meanwhile the abstract and introduction (ll. 1588, 1603, 1605) present EME as a headline mechanism and mention only its one-run benefit.

**Requested changes.**

- In the abstract and introduction, state the measured trade-off once: EME captured one contaminated revision that no other edge reached, at the cost of more collateral in 55 of 75 runs and of pulling closure up to the time cut.
- Rephrase l. 2160 and l. 2291 so that the cause is the EME rule applied to broadcast contexts.
- Discuss EME as an operator-configurable policy. Options include: off; only for experiences with a failing outcome; only for contexts whose revisions the run's output demonstrably used; or bounded by hop count. Report at least one such variant from the recorded data. This is cheap, because closure is recomputed from the recorded state.

### M5. A few positioning sentences still overstate novelty

- **l. 1601 and l. 2316.** PROV-style capture is said not to record "the indirect channel" (l. 1601), and capture alone is said not to give "the experience-mediated channel, which requires joining run contexts with experiences" (l. 2316). Under PROV, a run is an activity that `used` its context entities, the experience `wasGeneratedBy` it, and the lesson `wasDerivedFrom` the experience. Transitive lineage already contains the EME path, and PROV-AGENT records model-call inputs. The defensible claim is that existing self-evolving harnesses do not record run contexts as inputs, and that HEARTNESS makes this mandatory and uses it in admission.
- **l. 2313.** "Contributes the missing remedy" relative to EVOMAL. HEARTNESS was not evaluated on adversarial or executable-skill poisoning, and an adversary who controls an experience can also exploit M2. Say "a candidate remedy, evaluated on non-adversarial faults".
- **l. 2322, "where recorded lineage makes exact removal possible".** Withdrawal is an over-approximate *suspension* without recomputation. Exact unlearning in the SISA sense produces the counterfactual state, which corresponds to rollback-and-re-evolve (M3).
- **l. 2322, deletion propagation.** Calling withdrawal "the opposite direction" of deletion propagation is right for Buneman-Khanna-Tan. But forward propagation of source deletions to derived data is the classic subject of view maintenance under deletion (the counting algorithm) and of how-provenance and provenance semirings. These distinguish a derivation that *requires* a source from one that has alternatives, which is exactly the over-approximation discussed at l. 1902 (k1 suspended although only one of three sources was faulty). Cite this line of work and say why the all-sources (disjunctive) semantics is the only sound choice for LLM synthesis.

### M6. Revalidation's attestation lineage is described but does not exist

Section III-F (l. 1915) states that the lineage of a re-admitted x' "is retained in the attestation, not in ⇝, so a later withdrawal of the attestation (for example, when the screen is found faulty) withdraws all its re-admissions." The attestation has no class in the metamodel (l. 1776), no operator in Def. 8 (l. 1678), no property in Table II, and no implementation: there is no attestation concept in `src/heartness`, and `experiments/live/supplement.py` restores sets directly. As written, a re-admitted x' has src = ∅ and is admitted as a seed. If the screen missed contamination, which happens under curation in 13 runs (l. 2164), x' becomes untraceable from the root and escapes any later withdrawal. This is the concern I raised in round 3 (concern 8), and it is still not addressed in the semantics.

**Requested change.** Either:

- add a `reattestedFrom(x', x, r, φ)` relation to the metamodel, an operator that withdraws an attestation (and by closure its re-admissions), and a P2-style property, implemented and tested; or
- delete the sentence and list in Limitations that re-admitted revisions lose their lineage.

## Minor issues

1. **Load precondition (ll. 1806-1824, 1962).** Proposition 1's EME case and Proposition 2's Load case both rely on the guard that a run's context must be loaded before the run produces an experience (`engine.py`: "run already produced an experience"). This appears only in Lessons (l. 2299). Add it to Section III-C and Algorithm 1, and cite it explicitly in both proofs.
2. **Rollback and deployments (l. 1895, Table II P5).** `Rollback` sets Act but leaves Dpl unchanged (`engine.py`). State this, and say whether a rollback to before the fault (T as a *remedy*) must be followed by a Deploy to affect agents. This also bears on M3, argument 2.
3. **Cut definition (l. 1905 vs. l. 2036).** Proposition 1 cuts at the earliest root's acceptance. T cuts before the corrupted experience. State that T's cut is at or before Proposition 1's, so H ⊆ T still holds. Also state that "suspends exactly the same set when every revision accepted after the root is exposed to it" (l. 1910) refers to Proposition 1's cut.
4. **"We prove that withdrawal never suspends more than a rollback" (abstract, l. 1588; contributions, l. 1610).** This is a one-line monotonicity lemma (lineage edges point forward in time). It is useful, but presenting it as a headline theorem oversells it. Consider "we show" in the abstract.
5. **Proposition 2 naming (l. 1958).** "Containment is inductive" may be read as containment of contamination. It is containment of the *recorded* closure. Rename it (e.g., "Suspension invariant") or add the qualifier in the statement.
6. **Fault positions and composition schedule (l. 2007, l. 2160).** All spared revisions under curation lie between the fault (tasks 2, 8, 9) and the first composition (task 12). The size of the H-T gap is therefore a function of this schedule. Report or discuss the expected gap for a fault after task 12.
7. **H_faulty argument (l. 2160).** The three runs in which the root was "not labelled contaminated but its derivatives were" may be oracle misses on the root: curation has 24 ambiguous labels and adoption rises from 53 to 59 when they are counted. Check these three runs against ambiguous root labels before using them as "an argument for withdrawing every revision motivated by a suspicious experience".
8. **Adopted-run results.** `\LiveCAdopt*` macros (e.g., H suspends 21.19 vs. R4 2.70 on adopted runs) are computed but unused. Either report them (one sentence or a table column) or drop them from the package summary.
9. **By-construction rows (Table V; macro block ll. 1527-1529).** Mark H_¬EME, H_¬dep and H_local as "identical/null by construction" in the table itself, not only at l. 2110. The "Withdrawal must reach deployments" lesson (l. 2295) follows from this harness's separate deployment copies; phrase it as a design requirement, not a finding.
10. **LLM judge prompt.** The judge still receives the concatenated text of all roots (`run.py`, `root_text`). Under ExpeL most roots are clean co-batched insights (l. 2007). State this at l. 2035, because it may depress R4's precision under ExpeL.
11. **Abstract adoption rate.** Add that the root adopted the fault in 74 of 150 runs (21 + 53), so readers can see how much of the study had anything to contain (round-3 concern 9).
12. **E-G (l. 2202).** As in round 3: 10/10 guard necessity is close to definitional. One sentence on what it adds beyond the 14/14 mutant kills (l. 1992) would suffice.
13. **E-S (Table VII, l. 2238).** The claim "exhaustive checking finds ordering-dependent withdrawal faults that equal-budget random testing misses" (also in the abstract) rests on n = 2, depth 9 and seeded guard removals. Qualify it in the abstract ("on seeded guard faults at small scope").
14. **Title (l. 1573).** As in round 3: "Model-Driven Approach". The metamodel is Python dataclasses, with no metamodelling language, OCL or transformations. Either justify the term in Section III-B (e.g., an Ecore/OCL rendering with P1-P9 as invariants) or drop it from the title.
15. **Line counts (l. 1994).** `experiments/live` has 1,680 lines, not "about 1,500". Use the exact count.
16. **Table VIII (l. 2345).** For HEARTNESS, "Behaviour flow ✓ (across tasks)" would be more accurate as "✓ (recorded run contexts; observed once)". For "Withdrawal ✓", add the M2 qualifier, or keep the cell and footnote it.

## Recommendation

**Major revision.**

This is close to an acceptable TSE paper. The problem is relevant, the artifact is exemplary, and the body of the evaluation now reports honestly that closure is close to a rollback in precision. What remains is not cosmetic, though:

- The headline guarantee has a semantic gap: re-derivation from the faulty experience is admitted (M2).
- Revalidation describes a lineage mechanism that does not exist (M6).
- The only property that truly separates HEARTNESS from a rollback, enforcement after withdrawal, has not been exercised on live self-evolution (M3).
- The abstract, introduction and conclusion describe the detector comparison more favourably to HEARTNESS than the tables do, and the unfavourable tests are omitted (M1).

M1, M4 and M5 are text changes. M2 and M6 can be resolved either by small engine additions or by explicit scoping. M3 needs one inexpensive continuation experiment on the existing infrastructure, or a corresponding narrowing of the claims about the advantages over rollback. If these are done, I expect to recommend acceptance.
