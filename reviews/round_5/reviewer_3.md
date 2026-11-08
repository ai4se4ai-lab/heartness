# Round 5 -- Reviewer 3 (presentation, clarity, relevance)

This is an internal, automated review of a draft. It is not independent peer review. Scores run from 1 (poor) to 5 (excellent). Line numbers refer to `docs/TSE/main.tex` as of this round (2,464 lines; body starts at l.1655). Page numbers refer to the compiled `main.pdf` (22 pages, one more than in round 4). I read the PDF text in full and rendered pp. 5–8 and 21 to check layout. I checked the numbers quoted below against the generated macro block.

I also checked the new code:
- `src/heartness/revalidation.py`
- experience withdrawal in `engine.py`/`model.py`
- `experiments/live/supplement.py`
- `tests/test_revalidation.py` and `tests/test_eme.py`

For the central round-4 issue I re-ran `heartness.revalidation.plan` on all 150 recorded supplements of both Fir campaigns (`am-20261107-060101`, `am-20261107-080855`). I recomputed the screens from the scores stored in each `record.json` and compared the result with the stored `restored` sets. I edited no file other than this review.

## Summary

Heartness is a model-driven controller for self-evolving agent harnesses. Its parts are:
- immutable revisions;
- host-side capture of exposure, including experience-mediated exposure (EME);
- guarded admission;
- closure-based withdrawal of a revision *or an experience*, across all deployments, with rollback admissibility;
- closure-bounded revalidation under an attestation (Algorithm 5, now implemented as `heartness.revalidation`);
- bounded model checking with two encodings and witness replay;
- a conformance monitor.

Proposition 1 bounds the closure by a time cut. Proposition 2, the suspension invariant, now covers experience withdrawal.

The live study has 5 generators × 2 policies × 5 seeds × (3 faults + clean) = 200 runs. Contamination spread in 10/75 ExpeL-style and 42/75 curation runs. Closure had recall 1.00 in all 52 propagated runs. Its precision is close to the time cut (curation: 20.79 vs 22.20 suspended per run, precision 0.10, F1 0.18). Detectors were more precise but missed contamination folded into skills and profiles (R3 22/42, R4 13/42). Since round 4, the revalidation rows have been recomputed with Algorithm 5's dependency rule. HS_emb recall rose from 0.68 to 0.86 because P3 rejected 20 contaminated revisions that the screen had cleared. HS_judge is now essentially R4. A new post-hoc condition, H_EME-fail, keeps recall 1.00 at 17.24 suspended revisions per run.

The paper is clearly better again:
- The main round-4 consistency problem, evaluated revalidation ≠ Algorithm 5, is genuinely fixed, and I could verify it independently.
- The summaries now state the EME trade-off on both sides.
- The running example now shows the broadcast mechanism that drives closure cost.
- The abstract is at IEEE length.

What remains is mostly editorial, but some of it matters for correctness of the text:
- a factual overstatement repeated in the abstract, the RQ1 box and E-L (R3's F1 is *below* Heartness's under curation);
- pseudo-code that was not updated for experience withdrawal;
- an inverted definition of the paper's central term ("exposed to");
- several leftover inconsistencies, including one claim that the response says was withdrawn.

## Scores

| Criterion | Score | Justification |
|---|---:|---|
| (i) Novelty | 3/5 | Unchanged. The novelty lies in the integration and in the measurement: recording run contexts so that the EME path enters admission and withdrawal; deployment-wide suspension with rollback admissibility; a time-cut bound; a two-policy measurement of non-adversarial fault spread. The individual techniques (taint, provenance, build invalidation, view maintenance) are well positioned in V-E (l.2419). |
| (ii) Rigor | 4/5 | Up from 3. Revalidation is now evaluated with exactly the planning function the engine executes: I reproduced `plan()` = recorded `restored` in 150/150 supplements. Experience withdrawal closes the re-derivation gap and is tested. The noise estimate now uses independent generations rather than cache hits. H_faulty misses are traced to ambiguous root labels. The closure-vs-cut gap is stratified by fault position (l.2258). It is held below 5 by the false "every detector had higher F1" claim (Major 1), and by pseudo-code that no longer matches the guard the engine checks (Major 2). |
| (iii) Relevance | 4/5 | Clearly software engineering: change impact, traceability and rollback for self-modifying software. Three findings are directly actionable for harness designers: "the policy decides what closure costs" (l.2388), the broadcast-profile mechanism (l.2258), and the operator-configurable EME policy. The setting is still a prototype on function-level tasks, with no maintainer study (a study design is now sketched, l.2400). |
| (iv) Verifiability and Transparency | 4/5 | Strong. Numbers are generated macros, LLM responses are cached, superseded campaigns and `supplement_v1.json` are retained, CPU fallback is disclosed, and the device table is shipped. It is not 5 for three reasons. There is still no anonymized artifact link (l.2457). The plan = execution test runs only on a five-revision fixture (`tests/test_revalidation.py:69`), not on live states. The ExpeL supplements were produced by the pre-revision `restore` code. I verified that they coincide with `plan()`, but the paper does not say so. |
| (v) Presentation | 4/5 | Good for TSE. Every component follows the motivation/design/algorithm/example/limits pattern. The running example is grounded in quoted runs. The RQ boxes are short. The abstract is 249 words. Weaknesses: the inverted "exposed to" definition (Def. 4 vs. all later uses); notation collisions (T, F, A, C, D, μ each carry two or three meanings); two wrong algorithm line references; very long result paragraphs (l.2258: 320 words, l.2241: 287, l.2419: 406); a ⑩ label in Fig. 1 that is barely legible; and Table XI is still shrunk by `\resizebox`. |

**Overall recommendation: minor revision.**

## Status of round-4 issues

| Round-4 item | Status | Evidence / remaining gap |
|---|---|---|
| **M1** evaluated revalidation ≠ Algorithm 5; dependency remapping; attestation | **Resolved** | `supplement.py:52–58` now calls `heartness.revalidation.plan` with the history order, the dependencies, the active set after H, and the cleared set. I recomputed the screens from `record.json` and re-ran `plan()` for all 75 ExpeL and 75 curation supplements: 0 mismatches with the stored `restored` sets. Algorithm 5 l.4 remaps dependencies to copies (`D ← {μ(y) …}`), and the code matches (`plan`: `d not in active and d not in result.admitted`; `revalidate`: `done.get(d, d)`). Attestation is now a first-class seed revision that is the sole source of every copy. `test_withdrawing_the_attestation_withdraws_every_readmission` passes by construction. Residual discrepancies between the algorithm, the engine and the live evaluation are listed under Major 2(c); none affects a reported number. |
| **M2** summaries more favourable than tables | **Mostly resolved; one new overclaim** | EME is now stated on both sides (abstract l.1672, intro l.1697, RQ1 box l.2290). "For all five generators" is gone. The conclusion says "like rollback and reset". "Precision" is no longer garbled. "Both of our policies broadcast". "Proof sketch" / "argued". **New:** "every content detector had higher F1" (abstract l.1672), "Content detectors had higher F1 under both policies" (RQ1 box l.2290) and "every detector had higher F1 than Heartness" (l.2241) are false for R3 under curation (F1 0.16 vs 0.18; Heartness higher in 27 of 42 runs). See Major 1. |
| **M3** running example hides closure cost | **Resolved** | l.1996 states that every memory after the first rewrite is EME-exposed and that only memories between the fault and the rewrite are spared. This matches l.2258 (all 106 spared revisions are such memories). Indices are aligned with the code (l.1732, "m_i is written after task i+1"), except for one slip at l.1922 (see Major 4). |
| **M4** length and density | **Partially resolved** | Done: abstract 249 words; intro components as a list (l.1688); intro results paragraph qualitative; RQ1 box five sentences; duplicate paragraph removed. Not done: the paper grew from 21 to 22 pages; the ExpeL subsection was not shortened; the compute-platform paragraph (l.2111, 204 words) is unchanged (the author declined; see Minor); E-L result paragraphs got longer. |
| l.1640 "exactly this loop" / "periodically" | Resolved | l.1732: "The curation policy of our live study"; "after tasks 12 and 24". |
| Task/memory indexing | Mostly resolved | One remaining slip at l.1922 (Major 4). |
| "merged with m6, m9" vs whole batch | Resolved | l.1736: "the other lessons of its batch (abbreviated here to m6, m9)". |
| Fig. 1 lacks revalidation | Resolved, legibility weak | ⑩ added (l.1850, caption l.1863). On p.5 the rotated `\scriptsize` label "⑩ revalidate (§III-F)" is squeezed against the group border and hard to read at 100%. The Overview text (l.1811) explains ①–⑨ but not ⑩. |
| Base-profile fallback after withdrawal | Resolved | l.2157. |
| Which root the screen compares against | Resolved | Algorithm 5 l.1: φ(text(x), text(R)). l.2133: the judge sees all roots. |
| Dpl_before undefined | Resolved | Algorithm 5 Require line. |
| Prop. 1: seeds, T vs experience cut | Resolved | l.2001, l.2006. |
| Acronym at l.1716 | Not done | l.1808 still does not show how "Harness Evolution through Auditable Records, Typed dependencies, and Explicit State Semantics" yields HEARTNESS. The initials give H-E-A-R-T-D-E-S-S. Drop the expansion or make it work. |
| Table III "14 conditions" | Resolved | "11 evaluated conditions per faulty run (15 conditions in total)". |
| τ_t = 0.05 at grid boundary | Not done | l.2139 still does not say that the pilot optimum is the lowest grid value. This matters for l.2241 ("only because that threshold is low"). |
| H withdraws all roots: rationale | Resolved | l.2258, last two sentences. |
| Fig. 3 caption "only conditions" | Resolved | "among the plotted conditions" (l.2255). |
| Table VII HS_judge ≈ R4 | Resolved | l.2262. |
| EME price into RQ1 box | Resolved | l.2290. |
| "withdrawal guard" unnamed | Resolved | l.2299, "(the P2 suspension)". |
| E-C has no own objective | Not done | Still a sentence inside E-M's Procedure (l.2302) with results at the end of l.2316. Either label it "E-M(b)" or give it its own Objective/Procedure. |
| Projection description consistency | Resolved | l.2054, l.2337. |
| RQ3 box "about a second" | Resolved | "1–3 s" (l.2372). |
| Conclusion validity: curation effective n | Resolved | l.2383. |
| Limitations mention revalidation | Resolved | l.1998, l.2400. |
| Compute-platform paragraph | Not done (author decision) | l.2111, 204 words. I accept the authors' decision. I note that the four numbered justifications duplicate the Platform-validity threat (l.2379). |
| R4 uncited "skill-library screening" clause | Resolved | Clause removed. |
| Fig. 4 caption wording | Not done | l.2285, "falls below lexical recovery when between one half and three quarters of the edges, or fewer, are captured", is still awkward. |
| Table XI: git row; registries rollback; font | Partially | Version-control row added (l.2434). "Rollback --" for model registries is unchanged. `\resizebox` still makes p.21's table text about 5 pt. |
| Organization paragraph (Threats/Lessons) | Resolved | l.1714. |
| CPU-fallback remark in Lessons | Not done (minor) | l.2398 still repeats l.2377. |
| Maintainer-study sketch | Resolved | l.2400. |
| Anonymized artifact URL | Not done (acknowledged) | l.2457. |
| Long sentences / paragraphs | Not done | See Major 4 and Minor. |
| Round-3 carry-over: collateral per propagated run not in tables | Not done | l.2188 quotes "3.30 of them clean" (`\LiveEHCollProp`); no table column has it. |

## Remaining major issues

### 1. "Every content detector had higher F1" is false under curation (abstract, RQ1 box, E-L)

Table VII (p.14) gives R3 embedding F1 = **0.16** and Heartness F1 = **0.18** under curation. The paired test macros give Heartness higher F1 than R3 in **27** of 42 propagated runs and lower in 14 (`\LiveCTestFoneRthreeHi`/`Lo`, Holm p = 0.091). Three places nevertheless say the opposite:
- **Abstract (l.1672):** "every content detector had higher F1".
- **RQ1 box (l.2290):** "Content detectors had higher F1 under both policies".
- **E-L (l.2241):** "every detector had higher F1 than Heartness, R2 in all 42 … and R4 in 36". R3 is silently dropped from the list that follows.

What is true is *precision*: R3 0.12 vs 0.10. l.2258 ("below every detector's [precision], … narrowly for R3"), the intro (l.1697, "consistently more precise") and Lessons (l.2390) say this correctly.

This is a small numerical point but a visible one. A reader checking the abstract against Table VII finds an error in the paper's most-read sentence. It also misstates the result: under curation the embedding detector is *worse* than closure on both recall and F1, which supports the paper's "detectors fail on composed artifacts" message.

*Required.* Replace "higher F1" with "higher precision" in all three places, or write "R2 and R4 had higher F1; R3 had lower recall and lower F1". Add R3 to the paired counts in l.2241 (27 higher / 14 lower for Heartness).

### 2. The pseudo-code and the property table were not updated for experience withdrawal, and Algorithm 5 differs in details from the engine

**(a) The guard that the paper prints is not the guard the engine checks.** With experience withdrawal, the forbidden set is F = W ∪ K ∪ {b | exp(b) ∩ T ≠ ∅}. Proposition 2 (l.2057) says so, and so does the code (`engine.py:55` uses `closure(s.forbidden_roots())`; `model.py:137–140`). However:
- Algorithm 2 l.10 (Accept), Algorithm 4 l.8 (Rollback), and Table II's P2 and P8 (l.1882, l.1888) still use Cl(W ∪ K).
- The running example at l.1952, "The same holds for a candidate motivated by an experience whose run loaded m7", relies on the EME edge, not on T. No algorithm shows how a *future* revision motivated by a withdrawn experience is refused.

*Required.* Use Cl(F) in Algorithm 2 l.10, Algorithm 4 l.8 and Table II, and define F once (Section III-B, l.1872).

**(b) Algorithm 4 has no experience branch.** `Withdraw(r)` takes only a revision. The experience case exists only in prose (l.1959). For pseudo-code that the paper says it implements, add two lines:
- `if r ∈ ℰ: T ← T ∪ {r}; R ← {b | r ∈ exp(b)}`
- `A ← Cl(R)`

Also add T to Table I.

**(c) Algorithm 5 vs `revalidation.py` vs `supplement.py`.** None of the following changes a reported number: I checked that no superseded revision was ever cleared in the 150 supplements. Each is still a place where the paper's claim "the same loadable state" depends on a property that is unstated.
- **What "A" means.** Algorithm 5 takes the "affected set A" (Definition 5: closure ∩ (Act ∪ Dpl), so superseded revisions are excluded). Algorithm 4 l.2 uses A for the *full* closure Cl({r}). `revalidate()` screens `cleared & s.quarantined`, which is the full closure minus the root and includes superseded revisions. `supplement.py` uses H's suspended *live* set. Copies are created without `replaces`. So if the engine re-admitted a cleared copy of a superseded profile or an edited ExpeL insight, it would become active alongside its successor. The live evaluation avoids this only through `active = h.active | (back & rec["active"])` (`supplement.py:55`), and Algorithm 5 does not contain that filter. Fix this by renaming Algorithm 4's A to Cl, and either restricting `revalidate()` to the affected set or stating the restriction in Algorithm 5 l.1.
- **Roots.** Algorithm 5 takes a root set R. `revalidate()` takes one `root: str`. Under ExpeL there are up to four roots (l.2105).
- **The attestation.** Algorithm 5 l.2 always admits a = ⟨R, φ, C⟩ with C the *cleared* set, and the Design text (l.2011) writes ⟨r, φ, cleared set⟩ with a lower-case r. The code admits the attestation only if something is planned, and records only the planned-admitted subset. State one version.
- **Plan vs execution.** l.2031 says "a test checks that the plan equals the engine's execution". The test (`tests/test_revalidation.py:69`) uses a five-revision fixture without contracts, while the engine also checks `req ⊆ prov`, which `plan()` ignores. Say "on a fixture". Better, replay a sample of live records through `revalidate()` and report agreement.
- **The ExpeL supplements** (`am-20261107-060101`) carry no `cleared`/`rejected` fields. They were produced by the previous `restore` code. They coincide with `plan()` because insights have no dependencies (I verified 75/75). One sentence in the package README would make that auditable.

**(d) Wrong line references.** l.1952 ("is rejected by line 12") and l.1954 ("Line 12 recomputes a closure") point to Algorithm 2 l.12 (`Act ← S; append snapshot`). The closure check is l.10 (p.6).

### 3. The paper's central term is defined in one direction and used in the other; notation collisions

**Direction.** Definition 4 (l.1747) reads: "Revision x is *directly exposed to* revision b, written x ⇝ b, iff x ∈ src(b) …". On this definition the *source* is "exposed to" its derivative. The example (l.1749, "m9 is exposed to k1") follows it. Table I (l.1794) repeats it. Every later use reads the other way, which is also the natural reading (b was shown x):
- l.1758: "plus any later revisions exposed to these";
- l.1996: "every memory … is EME-exposed to p¹₁₂";
- l.1998: "Revisions that are not exposed to m7";
- l.2006: "every revision accepted after the root is exposed to it";
- l.2009, l.2388: "every later lesson exposed".

For the paper's key concept this is a real readability defect. *Required.* Redefine it as "b is directly exposed to x, written x ⇝ b, iff …". Fix l.1749 and Table I accordingly.

**Collisions.** Symbols are reused in ways that collide inside single pages:
- **T**: tainted experiences (l.1872, Prop. 2); the time-cut baseline (l.2134, Tables V/VII); frozen texts (Algorithm 1 l.7).
- **F**: external effects (Def. 8, Algorithm 4 l.5/l.9); forbidden roots (Prop. 2).
- **A**: all revisions 𝒜; the affected set (Algorithm 4/5); the reset baseline A; the ambiguous set in the precision formula (l.2146).
- **C**: context (Algorithm 1); cleared set (Algorithm 5); contaminated set (l.2146).
- **D**: deployments D₁/D₂; dependency set (Algorithm 5 l.4); deviation list (Algorithm 7).
- **μ**: copy map (Algorithm 5); mutant (Algorithm 6).

*Required (cheap).* Rename the tainted set (e.g. W_E), forbidden roots (e.g. Φ), the cleared set (e.g. Clr) and the copy map (e.g. ρ). Write the metric sets in words or with distinct letters. Add W_E and F/Φ to Table I.

### 4. Consistency sweep: leftovers that contradict the data or the response

- **"Sensitivity to context order" (l.2210).** The response (R2.M1) says this order-sensitivity claim "was withdrawn (confounded)" and that "all four places" were fixed. The last sentence of the ExpeL behaviour paragraph still says "the effect on pass@1 is within the agent's sensitivity to context order". Replace it with "within the measured inference noise".
- **H_local "null by construction."** The Table VII caption (l.2228) and Lessons (l.2392, "H_local is null by construction") say this. Under curation H_local suspends 15.59 revisions per run with recall 0.03 and residual 1.13 (Table VII). It is not null; it removes store-level memories but leaves every deployed contaminated skill and profile in use. "Null" holds only for ExpeL (all zeros). Reword: "H_local cannot remove deployed copies by construction".
- **Running example, capture (l.1922).** "For task 8, AssembleContext retrieves … m7; Load(r₈, {p¹₀, m6, m7, m5})". By the paper's own convention (l.1732: m_i is written after task i+1; l.1734: task 8 *produces* m7), m7 does not exist during task 8. It must be task 9, matching l.1738 and r₈ at l.1749/l.1895. The listed context also omits the skill k₀, which exists after task 6 and which every curation context includes ("its two most relevant skills", l.2101). Write "{p¹₀, k₀, m₅, m₆, m₇}" or add "…".
- **RQ1 box (l.2290): "as only rollback and reset did".** H_EME-fail also had recall 1.00 in all 52 runs (Tables V/VII). Under ExpeL, R2, R3 and HS_emb did too. Write "among the alternatives to Heartness, only rollback and reset matched this under both policies".
- **l.2206: "F1 0.67, the highest mean of all conditions".** True among the frozen conditions, but Fig. 2 shows TF-IDF reaching 0.69 at other thresholds. Write "of all conditions at their frozen settings".

### 5. Length and density (carried over, reduced)

The paper is now 22 pages. Several result paragraphs are each a page-column of unbroken text:
- l.2241: 287 words
- l.2258: 320 words
- l.2260: 270 words
- l.2377: 313 words
- l.2419: 406 words

Several sentences exceed 60 words. Concrete cuts that cost no content:
- (i) Split l.2258 at "The size of the gap is therefore …" and l.2260 at "EME is a policy of the controller …".
- (ii) Cut the ExpeL ablation paragraph (l.2208) to one sentence; Table V already shows the identical rows.
- (iii) Split Related Work V-E (l.2419) into "taint/IFC", "deletion propagation/view maintenance/unlearning" and "build systems/sagas" paragraphs.
- (iv) Move the four numbered platform justifications (l.2111) to the package. I accept that the authors prefer to keep them, but they duplicate l.2379.

## Minor issues

**Approach and pseudo-code**
- **Algorithm 1:** the run identifier r appears in l.3–4 without being introduced. Add "fresh run r" in l.2.
- **Fig. 1 / l.1811:** the Overview text describes ①–⑨ but not ⑩. Add one clause. Move the ⑩ label so that it does not run vertically along the controller border (p.5).
- **l.2011:** "relative to the text of the withdrawn roots" vs Algorithm 5's text(R). Fine, but say "concatenated", as l.2133 does for R4.
- **l.2090:** the module list omits `revalidation.py`. Add "closure-bounded revalidation (`revalidation.py`, Algorithm 5)".
- **l.1808:** fix or drop the acronym expansion (carried over).
- **l.1998:** "only one of its three sources was faulty". In the real chain k₁ has six sources (l.1740). Say "only one of its sources".

**Evaluation**
- **l.2139:** state that τ_t = 0.05 is the lowest grid value (carried over).
- **l.2188:** "3.30 of them clean" is not in any table. Add a "Coll. (prop.)" column or drop the number (carried over from round 3).
- **E-C (l.2302/l.2316):** give it an Objective/Procedure or call it E-M(b) (carried over).
- **Fig. 4 caption (l.2285):** "Recorded exposure degrades in proportion to missing edges; below about 50–75% capture, lexical recovery is more accurate" (carried over).
- **Table VII caption:** besides H_local (Major 4), "H¬dep equals H by construction (every profile dependency is also a synthesis source)" is good. Add the analogous one-liner for H_EME-fail in Table V, which equals H under ExpeL by construction for the same reason as H¬EME.
- **l.2264:** "(4.1% under the ExpeL-style policy)" repeats l.2210. Give the curation rate as a percentage too (`\LiveCNoiseRate`), as Threats does (l.2377).
- **`experiments/live/supplement.py` docstring (l.1–10):** it still says "re-admit every suspended non-root member that a screen clears" and points to `tests/test_eme.py`. Update it to "subject to Algorithm 5's dependency rule; see tests/test_revalidation.py".

**Related work, threats, rest**
- **Table XI:** replace `\resizebox` with abbreviated headers so that the table is readable in print. Model registries do support version rollback ("○ (version)") (carried over).
- **l.2398:** the CPU-fallback observation duplicates Threats (l.2377). Keep it in one place.
- **l.2457:** provide an anonymized artifact link for review (carried over).
- **Title (l.1657):** still gives model checking equal billing with traceability/withdrawal. This is acceptable; it remains my preference to drop the subtitle or make it "A Model-Driven Approach" only.

## Recommendation

**Minor revision.**

Since round 4 the authors have done the substantive work I asked for:
- Revalidation is now a composition of ordinary operators. It has a real attestation revision, and the live evaluation uses the same pure `plan()` as the engine. I independently reproduced all 150 recorded plans.
- Experience withdrawal closes the re-derivation gap.
- The summaries state the EME cost honestly.
- The running example explains why closure approaches the time cut.

For a TSE audience the paper is readable, practically relevant and unusually transparent.

Required before acceptance (all editorial or pseudo-code fixes; no new experiments):
1. Correct the F1 claim for R3 in the abstract, the RQ1 box and l.2241 (Major 1).
2. Make Algorithms 2 and 4 and Table II use the forbidden set F that the engine checks. Add the experience branch to Algorithm 4. Reconcile Algorithm 5's candidate set, roots and attestation content with `revalidation.py`, and state that the plan = execution test is on a fixture. Fix the "line 12" references (Major 2).
3. Fix the direction of "exposed to" in Definition 4 and Table I, and remove the notation collisions (Major 3).
4. Remove the withdrawn "context order" claim. Reword "H_local is null". Fix the task-8/task-9 slip at l.1922. Qualify "as only rollback and reset did" (Major 4).

The length cuts (Major 5) and the minor items are strongly recommended but not blocking.
