# Round 6 -- Reviewer 3 (presentation, clarity, relevance)

This is an internal, automated review of a draft. It is not independent peer review. Scores run from 1 (poor) to 5 (excellent). Line numbers refer to `docs/TSE/main.tex` as of this round (2,475 lines; `\begin{document}` at l.1663). Page numbers refer to the compiled `main.pdf` (23 pages, up from 22; the body ends on p.21 and references fill pp.22-23). The PDF and the .tex have the same timestamp. I read the PDF text in full and rendered p.5 (Fig. 1, Table II) and p.21 (Table XI). I checked the quoted numbers against the generated macro block (l.~1600-1660).

I checked the code against the paper:
- `src/heartness/revalidation.py`
- `forbidden_roots()` in `src/heartness/model.py:137`
- the admission guard in `src/heartness/engine.py:55`
- `experiments/live/supplement.py`
- `tests/test_revalidation.py`

I edited no file other than this review.

## Summary

Heartness is a model-driven controller for self-evolving agent harnesses. Its parts are:
- immutable revisions;
- host-side capture of exposure, including experience-mediated exposure (EME);
- guarded admission;
- closure-based withdrawal of a revision or an experience across deployments, with rollback admissibility;
- closure-bounded revalidation under an attestation;
- bounded model checking with two encodings and witness replay;
- a conformance monitor.

The live study (200 runs, 5 generators x 2 policies) is unchanged in substance:
- Closure had recall 1.00 in all 52 propagated runs.
- Under ExpeL closure equals the time cut. Under curation it is slightly below it (20.79 vs 22.20 suspended per run).
- Detectors are more precise but miss contamination folded into skills and profiles.

This round's changes are mostly the notation and pseudo-code fixes I asked for in round 5:
- Θ for tainted experiences, and forbidden roots F defined once in the metamodel.
- An experience branch in Algorithm 4.
- Cl(F) used in Algorithm 2, Algorithm 4 and Table II.
- Definition 4 reversed so that "b is exposed to x" reads naturally.
- Revalidation now keeps the clean part of a copy's lineage.
- The R3 F1 overclaim corrected.
- Several leftovers removed.

Most of these fixes are correct. The direction of "exposed to" is now consistent throughout, which was the most important presentation issue of round 5.

Four things remain:
1. One rename created a new collision. Definition 8 still uses F for external effects and X for accepted proposals, which clashes with the new forbidden-root F and with Algorithm 4's X for effects.
2. The authors rejected the "line 12" correction, but the PDF shows I was right. The algorithms are printed without end-lines, so the P2 check is line 10.
3. The abstract still says withdrawal was "barely more precise than rollback", although Table VII gives both 0.10.
4. Algorithm 5's "affected set A" still means three different things (Definition 5, Algorithm 4 and the code).

The paper also grew by a page. Its longest result paragraph is now 369 words.

## Scores

| Criterion | Score | Justification |
|---|---:|---|
| (i) Novelty | 3/5 | Unchanged. The contribution is the integration and the measurement: run contexts recorded as inputs so that EME enters admission and withdrawal; deployment-wide suspension with rollback admissibility; the time-cut bound; a two-policy measurement of non-adversarial fault spread. The individual techniques (taint, provenance, view maintenance, build invalidation) are well positioned in Section V-E. |
| (ii) Rigor | 4/5 | Unchanged. The pseudo-code now prints the guard the engine checks (Cl(F), `engine.py:55`, `model.py:137`). Withdrawal of an experience is in Algorithm 4. Revalidation keeps clean lineage, and a test reproduces the scenario. The score is held below 5 for three reasons: Algorithm 5's candidate set does not match Definition 5 or the code; the plan = execution evidence is still a fixture test; and two summary sentences are still stronger than the tables (Major 2). |
| (iii) Relevance | 4/5 | Unchanged. Clearly software engineering: change impact, traceability and rollback for software that rewrites itself. Three actionable lessons stand out: "the policy decides what closure costs" (l.2399), "closure is a bound, detection is a filter" (l.2401), and "withdrawal must reach deployments". The setting is still a prototype on function-level tasks, with no maintainer study. |
| (iv) Verifiability and Transparency | 4/5 | Strong and slightly improved. The revalidation re-run is disclosed in Threats (l.2388), and the superseded results are kept. The post-hoc status of H_EME-fail is stated in the intro, Threats, Lessons and Conclusion. The score stays at 4 because there is still no anonymized artifact link (l.2468, "DOI will be minted") and because the `supplement.py` and `revalidation.py` docstrings contradict the code (Minor). |
| (v) Presentation | 4/5 | Unchanged. The exposure direction is fixed and the RQ boxes are accurate. The score stays at 4 for several reasons: a new F/X collision in Definition 8; μ means two different things in Algorithms 5 and 6, which are printed side by side on the same page; two line references are still wrong; the paper is now 23 pages; three paragraphs exceed 360 words; Table XI is still about 5 pt; and the ⑩ label in Fig. 1 is still squeezed vertically against the controller border. |

**Overall recommendation: minor revision.**

## Status of round-5 issues

| Round-5 item | Status | Evidence / remaining gap |
|---|---|---|
| **M1** "every detector had higher F1" | **Resolved, with a residual overstatement** | Abstract (l.1680): "Every detector was more precise and TF-IDF and the LLM judge had clearly higher F1". E-L (l.2252) now reports R3 as comparable (0.16 vs 0.18; Heartness higher in 27 runs and lower in 14; p=0.091). The RQ1 box (l.2301) is corrected. Residual: "clearly higher F1 under both policies" (RQ1 box) and "clearly" (abstract) do not fit the ExpeL policy, where l.2215 itself says that none of the F1 differences is significant (n=10). See Major 3. |
| **M2(a)** guard printed ≠ guard checked | **Resolved** | F = W ∪ K ∪ {b \| exp(b) ∩ Θ ≠ ∅} is defined at l.1881. Algorithm 2 l.10, Algorithm 4 l.10 and Table II P2/P8 use Cl(F). This matches `model.py:137-140` and `engine.py:55`. Θ and F are in Table I. |
| **M2(b)** Algorithm 4 experience branch | **Resolved** | Algorithm 4 l.2-3: `if r ∈ ℰ: Θ ← Θ ∪ {r}; R ← {b \| r ∈ exp(b)} else R ← {r}`, followed by `A ← Cl(R)`. This matches the prose in Section III-E (l.1968) and the proof sketch of Proposition 2. Definition 6 (l.1764) still defines withdrawal for a revision only (Minor). |
| **M2(c)** Algorithm 5 vs `revalidation.py` | **Partially resolved** | *Done:* the code takes a root set; the attestation records `{roots, screen, cleared}` with the full candidate set, matching ⟨R, φ, C⟩; sources, experiences and dependencies of x′ match Algorithm 5 l.4-7 (`revalidation.py:84-93`); copies carrying no `replaces` is stated in the response. *Not done:* (1) "affected set A" in the Require line still conflicts with Definition 5 (Cl ∩ (Act ∪ Dpl)), with Algorithm 4 (A = Cl(R), the full closure) and with the code (`closure(roots) - roots` ∩ quarantined, i.e. the full closure). (2) Copies carry no `replaces`, so a cleared, *superseded* member (for example p¹₁₂ after p¹₂₄ replaced it) would be re-admitted into Act next to its successor. The response's count (1,820/1,820 previously active) shows that this did not occur in the data. The algorithm neither excludes it nor says why it is harmless. (3) The code admits the attestation only if the plan is non-empty (`revalidation.py:73`); Algorithm 5 l.2 always admits it. (4) The prose at l.2021 still writes ⟨r, φ, cleared set⟩ with a lower-case r. (5) l.2042 still says "a test checks that the plan equals the engine's execution" without "on a fixture" (`tests/test_revalidation.py:70`). See Major 2. |
| **M2(d)** "line 12" in §III-D | **Not resolved (response incorrect)** | The response says that "line numbering counts procedure-end lines". The PDF (p.6) shows otherwise: the algorithms are typeset without `end procedure` lines. Algorithm 2 is numbered 1-12 with Propose = 1-3, Validate = 4-5 and Accept = 6-12. Line 10 is `require S ∩ Cl(F) = ∅`; line 12 is `Act ← S; append snapshot`. Both "rejected by line 12" (l.1961) and "Line 12 recomputes a closure" (l.1963) are therefore wrong. The other references are correct: Algorithm 1's "line 3" and "lines 7-10", and the numbering of Algorithm 4. Use `\label` inside the algorithm and `\ref` so that the numbers cannot drift. |
| **M3** direction of "exposed to" | **Resolved** | Definition 4 (l.1755): "Revision b is directly exposed to revision x, written x ⇝ b". The example (l.1757, "k₁ is exposed to m₉"), Table I and every later use (l.1766, 2006, 2008, 2016, 2068, 2199, 2418) now read the same way. Remaining minor point: "exposed to" is used transitively (for example l.2016, "every revision accepted after the root is exposed to it"), but only *directly exposed* is defined. Add "b is exposed to x iff x ⇝⁺ b" to Definition 4. |
| **M3** notation collisions | **Partially resolved; one regression** | *Fixed:* tainted set → Θ; forbidden roots F; effects → X in Algorithm 4. *Regression:* Definition 8 (l.1778) still lists the state as (𝓔, 𝓐, Q, V, **X**, W, K, Act, Ver, Dpl, L, **F**, Λ) with **X = accepted proposals** and **F = external effects**. So F means "external effects" in Definition 8 and "forbidden roots" three paragraphs later (l.1881). X means "accepted proposals" in Definition 8 and "external effects" in Algorithm 4 l.7/l.11. Θ is missing from the tuple. *Remaining:* μ is the copy map in Algorithm 5 and the mutant in Algorithm 6, and the two are printed side by side on p.8. C is the context (Algorithm 1), the cleared set (Algorithm 5) and the contaminated set (metrics, l.2157). A is the closure (Algorithms 4/5), the reset baseline and the ambiguous set (l.2157). T is the frozen texts (Algorithm 1 l.7) and the time-cut baseline. D is the deployments and Algorithm 5's dependency set. See Major 1. |
| **M4** "context order" sentence | Resolved | Removed; l.2221 now says "within inference noise". |
| **M4** "H_local null" | Mostly resolved | It is now "ineffective by construction" (Table VII caption l.2239; Lessons l.2403). This is still slightly too strong: under curation H_local has recall 0.03 and residual 1.13 vs 1.20, because it does remove some retrieved memories. The accurate wording is "cannot remove deployed copies by construction". Minor. |
| **M4** running example task 8/9 | Resolved | l.1931: "For task 9 (run r₈) … Load(r₈, {p¹₀, k₀, m₅, m₆, m₇})". This is consistent with l.1740, l.1757 and l.1917. |
| **M4** RQ1 box "only rollback and reset" | Resolved | "as did rollback, reset and the EME-fail variant" (l.2301). |
| **M4** "F1 0.67, the highest mean of all conditions" | Not done | l.2217 is unchanged. The oracle-tuned TF-IDF bound reaches 0.69 (`\LiveEBoundTfidfFone`), and Fig. 2 plots it. Add "at their frozen settings". |
| **M5** length and density | **Worse** | The paper now has 23 pages (22 in round 5, 21 in round 4). Paragraphs that exceed 300 words: l.2269 (curation closure vs cut, **369** words, up from 320); l.2388 (internal validity, 378); l.2430 (Related Work V-E, 406, unsplit); l.2252 (309). None of the four cuts I proposed was applied: split l.2269 and l.2271, shorten the ExpeL ablation paragraph, split V-E, move the platform justifications. |
| Minor: Algorithm 1 run r not introduced | Not done | Algorithm 1 l.3 uses r without introducing it. |
| Minor: ⑩ in Fig. 1 / Overview text | Not done | The Overview (l.1820) still explains ①-⑨ only. On p.5 the rotated ⑩ label still runs along the controller border. |
| Minor: `revalidation.py` in module list | Not done | The implementation paragraph (l.2101) lists every module except `revalidation.py`. |
| Minor: acronym expansion | Not done | l.1817: "Harness Evolution through Auditable Records, Typed dependencies, and Explicit State Semantics" does not spell HEARTNESS. This is the third round I have raised it. Drop the expansion. |
| Minor: "one of its three sources" | Acceptable | It is consistent with the abbreviated src = {m₆, m₇, m₉} of the example. |
| Minor: τ_t on the grid boundary | Resolved | l.2152. |
| Minor: Fig. 4 caption | Resolved | l.2297. |
| Minor: E-C has no objective | Not done | E-C is still a sentence inside E-M's Procedure (l.2313), with its result in the last sentence of l.2327. |
| Minor: "3.30 of them clean" not in any table | Not done | l.2199. |
| Minor: curation noise rate as a percentage | Not done | l.2275 still gives 2/273 for curation next to "4.1% under the ExpeL-style policy". `\LiveCNoiseRate` = 0.7 exists and is used in Threats. |
| Minor: `supplement.py` docstring | Not done | `supplement.py:3-5` still says "re-admit every suspended non-root member that a screen clears … (tests/test_eme.py …)". In addition, `revalidation.py:5` now says that copies have "no experiences", which contradicts l.11-13 and the code (`revalidation.py:90`), which keeps clean experiences. |
| Minor: Table XI `\resizebox`; registries rollback | Not done | Rendered p.21: the body text of the table is about 5 pt. The registries row still shows rollback "--". |
| Minor: anonymized artifact link | Not done (acknowledged) | l.2468. |

## Remaining issues

### Major 1. Notation regression in Definition 8 (required, cheap)

Definition 8 (l.1778) still uses F for "external effects" and X for "accepted proposals". Section III-B (l.1881) then defines F as the forbidden roots. Algorithm 4 (l.7, l.11) uses X for external effects. A reader who reads Definition 8, Table I and Algorithm 4 in sequence meets three incompatible meanings for two letters. The response says "effects renamed X (no clash with F)", but the tuple that defines the state was not updated.

*Required.* Rewrite the tuple, for example as (𝓔, 𝓐, Q, V, Q_acc, W, K, Θ, Act, Ver, Dpl, L, X, Λ), so that:
- accepted proposals get a fresh symbol;
- effects are X;
- Θ is part of the state;
- F is reserved for the derived forbidden-root set.

While doing this, also fix the remaining clashes:
- Rename Algorithm 5's copy map (for example ρ). μ is Algorithm 6's mutant on the same page.
- Rename Algorithm 5's cleared set (for example Clr).
- Write the metric sets in words, or as C⁺ and Amb.
- Rename Algorithm 1's frozen texts (for example Txt), or the time-cut baseline.

### Major 2. Algorithm 5's candidate set, and the line references (required)

**(a) What "affected set A" is.** Definition 5 defines the affected set as Cl(R) ∩ (Act ∪ ⋃Dpl), so superseded revisions are excluded. Algorithm 4 l.4 uses A for the full Cl(R). `revalidate()` screens `cleared & (closure(roots) - roots) & quarantined` (`revalidation.py:67-68`), which is the full closure. Copies carry no `replaces`, so the following can happen:
1. p¹₁₂ is superseded by p¹₂₄; both are in the closure.
2. A screen clears p¹₁₂ but not p¹₂₄.
3. The engine re-admits p¹₁₂~r into Act.

The copy is not redeployed, because it is not in Dpl_before, but it is "active" again next to the successor that replaced it. The live evaluation never hit this case (the response reports 1,820/1,820 restored members that were previously active). The paper and the algorithm should still say which behaviour is intended.

*Required.* Choose one:
- (i) restrict C to the Definition-5 affected set, i.e. members that were active or deployed before the withdrawal, in both Algorithm 5 l.1 and `revalidate()`; or
- (ii) give each copy `replaces = replaces(x)`.

Then rename Algorithm 4's A to Cl (or S) so that "A" means one thing.

**(b) Smaller reconciliations.**
- Algorithm 5 always admits the attestation; the code admits it only when something is planned. State one behaviour.
- l.2021: change ⟨r, φ, cleared set⟩ to ⟨R, φ, C⟩.
- l.2042: "a test checks that the plan equals the engine's execution" → "a unit test on a small fixture checks …". Better still, replay a sample of recorded live states through `revalidate()` and report agreement; that would make the paper's "same loadable state" claim checkable on real data.

**(c) Line references.** In the PDF the P2 check of Algorithm 2 is **line 10**, not 12. The algorithms are typeset without `end procedure` lines; Accept spans lines 6-12. Fix l.1961 and l.1963. I recommend `\label{alg:admit:p2}` with `\ref` so that the numbers cannot drift again.

### Major 3. Two summary sentences are still stronger than the tables (required)

- **Abstract (l.1680): "but it was barely more precise than rollback."** Table V gives H = T = 0.33 under ExpeL (identical sets). Table VII gives H = T = 0.10 under curation (T: 0.10, F1 0.17; H: 0.10, F1 0.18). What is true is that it suspended slightly *less* (20.79 vs 22.20). The response states that the RQ1 box was changed to "suspends slightly less (not precision)" for exactly this reason, but the abstract was not. Write "but it suspended almost as much as rollback".
- **Abstract and RQ1 box (l.2301): "TF-IDF and the LLM judge had clearly higher F1 under both policies."** Under ExpeL the means are 0.60 and 0.65 vs 0.48. However, l.2215 says that Heartness had *higher* F1 than R4 in 2 of the 10 runs and that "none of these differences is significant after Holm correction". "Clearly … under both policies" is therefore not supported for ExpeL. Write "had higher mean F1 under both policies (significantly so under curation)", or drop "clearly".

### Major 4. Length and density (strongly recommended; now trending the wrong way)

The paper gained a page in each of the last two rounds and is now 23 pages, 21 of them body. TSE has no hard limit, but a reader needs to be able to find the result in each paragraph. The following cuts cost no content:

- **(i) l.2269 (369 words).** Split it in three:
  - the mechanism (up to "…which runs count as exposure");
  - the fault-position stratification;
  - H_faulty plus the adopted-run restriction, which could move to its own short paragraph or be cut to one sentence.
- **(ii) l.2252 (309 words).** Split it at "Precision tells the other half of the story". That sentence also needs rewording: it announces precision and then reports F1 and collateral counts.
- **(iii) l.2430 (406 words).** Split Related Work V-E into three paragraphs: taint/IFC; deletion propagation/view maintenance/unlearning; build systems/registries/sagas.
- **(iv) l.2388 (378 words).** Split internal validity into two paragraphs: design (faults, positions, post-hoc conditions, revalidation re-run, thresholds, judge) and inference (non-determinism, CPU fallback, caching).
- **(v) l.2219 (ExpeL ablations).** Cut it to one sentence; Table V already shows the identical rows.
- **(vi) l.2122 (compute platform).** I accept the authors' decision to keep it, but its point (iv) and the "remaining limitation" duplicate Platform validity (l.2390).

### Minor

**Approach**
- Definition 6 (l.1764) defines withdrawal of a revision only. Add "or an experience e (Section III-E)", so that the definition covers Algorithm 4's branch.
- Algorithm 1 l.2-3: introduce the run ("fresh run r").
- l.1820: add one clause for ⑩ to the Overview. On p.5, place the ⑩ label horizontally, beside the dashed arrow, instead of rotated against the border.
- Table II (p.5): the justified p-column produces visible gaps ("accepted/loaded content equals"). Use `>{\raggedright}`.
- Running example vs E-L: the EME example at l.2271 (`llama3.1:8b`, F3, seed 3) uses m₈ for the *faulty root* and m₉ for its EME child. In the running example, m₈ is the EME child and m₉ is a clean co-batched lesson. Add "(indices of that run)" to avoid a false cross-reading.

**Evaluation**
- l.2217: "the highest mean of all conditions" → "of all conditions at their frozen settings" (the oracle-tuned TF-IDF reaches 0.69).
- l.2275: give the curation noise as `\LiveCNoiseRate`% as well.
- l.2199: "3.30 of them clean" is in no table. Add a "Coll. (prop.)" column or drop the number (carried over since round 3).
- E-C: give it its own Objective/Procedure, or call it E-M(b).
- Table VII caption and Lessons: "H_local … is ineffective by construction" → "cannot remove deployed copies by construction (it removes some retrieved memories: recall 0.03)".
- l.2101: add `revalidation.py` (Algorithm 5) to the module list.

**Artifacts and related work**
- Fix the docstrings of `experiments/live/supplement.py:1-10` and `src/heartness/revalidation.py:5` (see the table above).
- Table XI: replace `\resizebox` with abbreviated column headers so that the table is readable in print. The "--" for registries under Rollback is still debatable.
- l.1817: drop the acronym expansion, which does not spell the name (raised for the third time).
- l.2468: an anonymized artifact link for review.

## Recommendation

**Minor revision.**

The authors made the conceptual fixes I asked for in round 5:
- The paper's central term now reads in one direction everywhere.
- The printed guards are the ones the engine checks.
- Withdrawal of an experience is in the pseudo-code.
- Revalidation preserves clean lineage.
- The R3 F1 claim is corrected.

For a TSE audience the paper is clear, honest about its limits and practically relevant, and its replication material is unusually complete. The remaining required changes are small, but several are visible on the first pages a reader checks.

Required before acceptance:
1. Fix Definition 8's state tuple: F and X are reused with other meanings, and Θ is missing. Also rename Algorithm 5's μ, which clashes with Algorithm 6's mutant on the same page, and the other overloaded letters C, A, T and D (Major 1).
2. Make "affected set A" in Algorithm 5 mean one thing, consistent with Definition 5 and `revalidate()`, and handle or exclude superseded members. Reconcile the attestation admission and ⟨R, φ, C⟩. Say "on a fixture". Change "line 12" to "line 10" at l.1961 and l.1963 (Major 2).
3. In the abstract, replace "barely more precise than rollback" (both are 0.10). Qualify "clearly higher F1 under both policies", since under ExpeL the differences are not significant (Major 3).

Strongly recommended:
- Split the three paragraphs above 360 words and shorten the ExpeL ablation paragraph, to reverse the growth to 23 pages (Major 4).
- The carried-over minors: ⑩ in Fig. 1, the acronym, Table XI legibility, the E-C structure, and the docstrings.
