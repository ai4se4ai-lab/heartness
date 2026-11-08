# Round 7 -- Reviewer 3 (presentation, clarity, relevance)

This is an internal, automated review of a draft, not independent peer review. Scores run from 1 (poor) to 5 (excellent). Line numbers refer to `docs/TSE/main.tex` as of this round (2,535 lines; `\begin{document}` at l.1701; macro block above it). Page numbers refer to the compiled `main.pdf`, which has the same timestamp as the .tex. It has **24 pages** (23 in round 6): the body runs to p.21, Table XII is on p.22, and the references fill pp.22-24. I read the PDF text in full and rendered p.5 (Fig. 1, Table II), p.8 (Algorithms 5 and 6), p.14 and p.15 (Tables VI-VIII). I checked the code against the paper: `src/heartness/revalidation.py`, `experiments/live/supplement.py` (`restore`), `experiments/live/process.py` (`selectivity`, l.189-219) and `tests/test_revalidation.py`. I ran the revalidation tests (8 passed). I edited no file other than this review.

## Summary

Heartness is a controller for self-evolving agent harnesses. Its parts are:
- immutable revisions;
- host-recorded exposure, including experience-mediated exposure (EME);
- guarded admission;
- closure-based withdrawal of revisions or experiences across deployments, with rollback admissibility;
- closure-bounded revalidation under an attestation;
- bounded model checking with two encodings and witness replay;
- a conformance monitor.

The live study is unchanged: 200 runs, five generators, two policies.

This round adds one analysis, the oracle-free **structural selectivity** analysis (Table VIII, l.2311-2330). Every final active revision is treated as a hypothetical root, and the analysis measures what share of later revisions its closure covers. Under ExpeL the closure equals the time cut everywhere. Under curation the share is 0.92 / 0.94 / 0.46 / 0.61 for roots at tasks 1-6 / 7-12 / 13-18 / 19-24.

The other changes are clean-ups I asked for in round 6:
- the state tuple of Definition 8;
- the in-use candidate rule and the active frontier in revalidation;
- the abstract wording;
- the copy map renamed ν;
- several carried-over minors.

Most were done correctly, and the code now matches Algorithm 5 on the points that matter. Three things remain:
1. One line reference I flagged is still wrong.
2. Algorithm 5 now *explicitly* defines "affected set A = Cl(R)", which contradicts Definition 5.
3. The new selectivity result is reported through its most favourable cell (0.46) without the horizon caveat that explains it.

The paper also grew by another page.

## Scores

| Criterion | Score | Justification |
|---|---:|---|
| (i) Novelty | 3/5 | Unchanged. The contribution is the integration and the measurement: run contexts recorded as inputs so that EME enters admission and withdrawal; deployment-wide suspension with admissible rollback; the time-cut bound; a two-policy measurement of non-adversarial fault spread. The selectivity analysis is a useful addition, but it is a reanalysis of existing records, not new evidence of selective containment of a real fault. |
| (ii) Rigor | 4/5 | Revalidation is now consistent between paper and code: the in-use rule, the attestation ⟨R, φ, C⟩, the frontier, and "on small fixtures". Notation in Definition 8 is fixed. The score is held at 4 for three reasons: Algorithm 5's "affected set" contradicts Definition 5; the selectivity claim is quoted from one cell without the horizon caveat (Major 2); and the "Line 12" reference is still wrong (Major 1). |
| (iii) Relevance | 4/5 | Unchanged and good. The paper is clearly software engineering: change impact, traceability and rollback for self-modifying software. The lessons are actionable ("the policy decides what closure costs", "closure is a bound, detection is a filter", "withdrawal must reach deployments"). The new table gives designers a concrete lever, provided it is framed correctly (Major 2). There is still no maintainer study. |
| (iv) Verifiability and Transparency | 4/5 | Strong. Every number comes from macros. The selectivity analysis is reproducible from `process.selectivity`. The revalidation re-run and the post-hoc conditions are disclosed. The score stays at 4 because there is no anonymized artifact link for review (l.2528, "DOI will be minted") and because `revalidate()` has a silent default (Minor). |
| (v) Presentation | 4/5 (borderline) | The required notation fixes were made. Still missing: "Line 12" (l.2001); Algorithm 5's A; C, D and T still overloaded. The paper is now **24 pages**. Five paragraphs exceed 320 words, including a new one at l.2059. Several minors are carried over for the third or fourth round: the illegible ⑩ label in Fig. 1, the justified-text gaps in Table II, `\resizebox` in Table XII, the E-C structure, and "Precision tells the other half of the story". |

**Overall recommendation: minor revision.**

## Status of round-6 issues

| Round-6 item | Status | Evidence / remaining gap |
|---|---|---|
| **M1** Definition 8 tuple (F/X clash, Θ missing) | **Resolved** | l.1816: σ = (𝓔, 𝓐, Q, V, Q_acc, W, K, Θ, Act, Ver, Dpl, L, X, Λ). Accepted proposals are Q_acc, Θ is in the state, and effects are X, matching Algorithm 4 l.7/l.11. F now appears only as the derived forbidden roots (l.1919). Withdrawal "of a revision or an experience" is listed among the operators. |
| **M1** μ copy map vs Algorithm 6 mutant | **Resolved** | Algorithm 5 uses ν (l.2064-2075; p.8). |
| **M1** other overloaded letters (C, A, T, D) | **Not done** | C is still the context (Alg. 1 l.2), the cleared set (Alg. 5 l.1) and the contaminated set (metrics, l.2197). A is still the closure (Algs. 4/5), "A reset learned state", and the ambiguous set (l.2197). T is still the frozen texts (Alg. 1 l.7) and the time-cut baseline. D is still the deployments and Algorithm 5's dependency set (l.2069). None of these is wrong locally, but the paper is meant to be read with Table I in hand. At minimum rename Algorithm 5's D (for example `Dep`) and the metric sets (C⁺, Amb). |
| **M2(a)** Algorithm 5 candidate set; superseded members | **Resolved in substance, new naming contradiction** | *Done:* Algorithm 5 l.1 restricts C to members in Act_b ∪ ⋃Dpl_b (l.2065). `revalidate()` intersects with `in_use` (`revalidation.py:70-72`). `supplement.restore` uses `rec["active"] ∪ deployments` (`supplement.py:54`). `test_superseded_revision_is_not_readmitted_beside_its_successor` passes. *New problem:* the Require line now reads "affected set A = Cl(R)" (l.2064; p.8). Definition 5 (l.1800) defines the affected set as Cl(R) ∩ (Act ∪ ⋃Dpl). The two definitions now contradict each other in print. Note that Algorithm 5 l.1 is *exactly* Definition 5's affected set evaluated in the pre-withdrawal state. So the cleanest fix is to write `C ← {x ∈ Aff_b(R) \ R | φ(...) = clean}` with Aff_b the Definition-5 affected set before withdrawal, and to call Algorithm 4's A "Cl" or "S". See Major 1. |
| **M2(b)** attestation admitted only when needed | **Resolved, with a residual** | Algorithm 5 l.3 says "if some x ∈ C is admissible". The code admits the attestation when `plan` (dependency check only) is non-empty (`revalidation.py:75-82`). A copy that the admission guards then reject leaves an attestation with no copy. The paper argues (l.2082) that the guards cannot bind on the live records, which is acceptable. "Admissible" in l.3 should say "passes the dependency check of l.6". The algorithm also does not show that `Admit(x′)` can fail (`revalidation.py:106-110`). One clause would cover both. |
| **M2(b)** ⟨R, φ, C⟩ in prose | **Resolved** | l.2059. The code records `{roots, screen, cleared: sorted(candidates)}` (`revalidation.py:80`), i.e. the in-use-filtered C, as printed. |
| **M2(b)** "on a fixture" | **Resolved** | l.2082: "a test checks on small fixtures that the plan equals the engine's execution". The response reports 300/300 recorded plans reproduced; one sentence in the paper saying so would strengthen the claim. |
| **New (round 6 R1)** active frontier | **Resolved; consistent** | Prose l.2059 and Algorithm 5 l.7 ("active frontier of dropped sources and contexts") match `active_frontier()` (`revalidation.py:122-144`), which walks back over sources, dependencies and EME contexts to active revisions outside Cl(F). The two new tests (cases A and B) pass. The claim at l.2059 that "every source, experience context and dependency of x′ lies outside Cl(F)" holds by construction of `sources`, `experiences` and the frontier. |
| **M2(c)** "line 12" in §III-D | **Half resolved** | l.1999 now says "rejected by line~10" (correct; p.6 shows l.10 = `require S ∩ Cl(F) = ∅`). **l.2001 still says "Line~12 recomputes a closure."** On p.6, line 12 is `Act ← S; append snapshot`; the closure is computed at line 10. The response states "changed to line 10", but only one of the two occurrences was changed. Use `\label`/`\ref` inside `algorithmic` so that this cannot recur. |
| **M3** abstract "barely more precise than rollback" | **Resolved** | l.1718: "but it suspended almost as much as rollback". The sentence is now clumsy, though: "Withdrawal suspended every contaminated derivative, as rollback did, while deleting the root removed none, but it suspended almost as much as rollback". It names rollback twice, and the antecedent of "it" is ambiguous, since the nearest subject is "deleting the root". Suggested: "Withdrawal, like rollback, suspended every contaminated derivative, and deleting the root suspended none; but withdrawal suspended almost as much as rollback." |
| **M3** "clearly higher F1 under both policies" | **Resolved** | Abstract (l.1718): "under curation TF-IDF and the LLM judge had clearly higher F1". RQ1 box (l.2361): "significantly higher F1". Under curation both are supported (0.36 and 0.69 vs 0.18; Holm p < 0.001). |
| **M3** transitive "exposed to" | **Not done** | Definition 4 (l.1793) still defines only *directly* exposed. The transitive form is used at l.2044 ("any revision later exposed to these") and l.2054 ("every revision accepted after the root is exposed to it"). Add "b is exposed to x iff x ⇝⁺ b". |
| **M4** length and density | **Worse** | The paper is now 24 pages (21 → 22 → 23 → 24 over four rounds). Paragraphs over 320 words: l.2490 (Related Work V-E, 406, unsplit for the third round); l.2448 (internal validity, 378); l.2309 (curation closure vs cut, 369); l.2059 (revalidation design, 334, new); l.2292 (curation detectors, 321). None of the splits I proposed in round 6 was made. The response lists this under "not done". |
| Minor: Definition 6 covers experiences | Resolved | l.1802. |
| Minor: Algorithm 1 run r not introduced | Not done | Alg. 1 l.3 `Load(r, C)`. |
| Minor: ⑩ in Overview text | Resolved | l.1858. |
| Minor: ⑩ label in Fig. 1 | **Not done** | Rendered p.5: the label is still rotated (`sloped`) along the controller's right border. At print size it is unreadable. |
| Minor: Table II justified p-column | Not done | p.5, P4: "accepted/loaded content equals" is still set with wide gaps. Use `>{\raggedright\arraybackslash}p{...}`. |
| Minor: running-example indices vs E-L | Not done | l.2331 says "That run is the behavioural inheritance of the running example", then calls the faulty root m₈ and the EME child m₉. In the running example m₇ is the root, m₈ the EME child and m₉ a clean co-batched lesson. Add "(indices of that run)". |
| Minor: "highest mean … at frozen settings" | Resolved | l.2257. |
| Minor: curation noise as a percentage | Resolved | l.2335. |
| Minor: "3.30 of them clean" in no table | Not done | l.2239 (`\LiveEHCollProp`). |
| Minor: E-C has no objective | Not done | It is still a sentence in E-M's Procedure (l.2373). |
| Minor: H_local wording | Resolved | Table VII caption and Lessons: "cannot remove deployed copies". |
| Minor: `revalidation.py` in the module list | Resolved | l.2141. |
| Minor: docstrings | Resolved | `revalidation.py:1-21` and `supplement.py:1-12` now describe the code. |
| Minor: acronym expansion | Resolved | Removed. |
| Minor: Table XI/XII `\resizebox`; registries rollback | Not done (acknowledged) | Now Table XII, p.22. The body is still roughly 5-6 pt. |
| Minor: anonymized artifact link | Not done (acknowledged) | l.2528. |

## Remaining issues

### Major 1. Two leftover inconsistencies in Section III (required, cheap)

1. **l.2001: "Line~12 recomputes a closure"** should be "Line~10". This is the fourth round in which this paragraph has been touched, so please switch to `\label{alg:admit:p2}` / `\ref`.
2. **"Affected set" means two things in print.**
   - Definition 5 (l.1800): Cl(R) ∩ (Act ∪ ⋃Dpl).
   - Algorithm 5 Require (l.2064): "affected set A = Cl(R)".
   - Algorithm 4 l.4: A ← Cl(R), returned to the operator as "the affected set" (Fig. 1 caption ⑦; l.1858).

   Choose one meaning. My suggestion:
   - Keep Definition 5.
   - Write Algorithm 4's set as S (or Cl).
   - State Algorithm 5 l.1 as C ← {x ∈ Aff_b(R) \ R | φ(text(x), text(R)) = clean}, which is what the code computes (`affected & in_use`).
   - Say once in the prose that withdrawal suspends the full closure, while the affected set (what is in use) is what the operator is shown and what revalidation may return.

### Major 2. The structural selectivity result is reported from its best cell, without the horizon caveat (required)

The new analysis is a good idea and answers a real question. It is honest in one important way: l.2311 says it "measures only how much closure spares, not whether what it spares is clean". However, the way it is summarised is not yet accurate.

- **Cherry-picked cell.** The intro (l.1743), the selectivity paragraph (l.2311), Lessons (l.2459) and, implicitly, the RQ1 box and Conclusion all quote the figure for roots "after the first composition" as **0.46**. Table VIII has two such rows: 13-18 gives 0.46 and **19-24 gives 0.61**. The value 0.61 appears nowhere in the text. Write "0.46-0.61" or quote the mean over tasks 13-24, and explain why 19-24 is higher (a root at 19-24 is merged into the task-24 skill and from there into both rewritten profiles).
- **The low ratio is partly an artifact of the 24-task horizon.** Under curation, profiles are rewritten at tasks 12 and 24 from the current skills (l.2152), and every task loads its profile. A memory written at tasks 13-17 is merged into the task-18 skill. That skill feeds the task-24 profiles, which would put every later run in the closure, but there are no later runs, because the evolution stream ends at task 24 (`process.selectivity` takes "later" from the final universe of the run, `process.py:207`). In a longer run with the same period, I would expect a 13-18 root to reach the time cut again after the next composition, just as 1-12 roots do (0.92-0.94). The accurate statement is about the *window between a root's creation and the next broadcast composition that includes its descendants*, not about "later faults" in general.

  The current conclusion, "markedly more selective for later faults under retrieval" (l.2311, l.2361, Conclusion l.2523), reads as a property of late faults. Please either:
  - state the horizon caveat explicitly ("within the remaining 6-12 tasks of our 24-task horizon; a longer run would broadcast the root's descendants at the next composition"); or
  - support the claim with a longer run or an argument that it holds.

  This matters for the designer's lesson at l.2459: the lever is the composition schedule and what composition reads, not merely retrieval.
- **Table presentation.**
  - The ExpeL 1-6 cell rests on **1 root**. Mark it (for example "n/a (1 root)") or merge it into 1-12.
  - The column header "Strict" needs the caption to decode it. "Spares ≥1" or "Narrower" is self-explanatory.
  - The roots are only revisions *active at the end* of a run. A fault root that a later edit replaced, which is the typical ExpeL case described at l.2223, is excluded. Say so in the caption.
  - "Ratio" is a mean of per-root ratios, so roots with few later revisions (19-24) weigh as much as those with many. Say so, or add the pooled ratio.

### Major 3. Length and density (strongly recommended; trending the wrong way for four rounds)

The paper is now 24 pages. I accept that TSE has no hard limit, but every round has added material and none has been removed. The following cuts cost nothing:

1. **l.2490 (406 words).** Split Related Work V-E into taint/IFC, deletion propagation/unlearning, and build systems/registries.
2. **l.2448 (378 words).** Split Threats/internal into design (faults, positions, post-hoc conditions, re-run, thresholds, judge) and inference (non-determinism, CPU fallback, caching).
3. **l.2309 (369 words).** Split it after "…which runs count as exposure". Move the H_faulty and adopted-run sentences into their own short paragraph.
4. **l.2059 (334 words, new).** Split the revalidation design into candidate selection and attestation, then lineage of the copy (sources, experiences, frontier, dependencies), then deployment and P2.
5. **l.2292.** Replace "Precision tells the other half of the story", which then reports F1 and collateral, with "On F1 and collateral the detectors win:". Split the paragraph there.
6. **The compute-platform paragraph (l.2162).** Point (iv) and "the remaining limitation" duplicate Platform validity.
7. **The ExpeL ablation paragraph (l.2259).** Reduce it to one sentence; Table V already shows the identical rows.

### Minor

**Approach and notation**
- Definition 4: add the transitive "exposed to" (see the status table).
- Rename Algorithm 5's D (it clashes with deployments), Algorithm 1's T (it clashes with the time-cut baseline), and the metric sets C/A at l.2196 (they clash with the context or cleared set and with the closure or reset).
- Algorithm 1 l.3: introduce the run ("fresh run r").
- Algorithm 5 l.3: define "admissible" (the dependency check of l.6) and note that `Admit(x′)` may still reject.
- Fig. 1: set the ⑩ label horizontally beside the dashed arrow. It is unreadable on p.5.
- Table II: `\raggedright` in the predicate column.

**Evaluation**
- Abstract (l.1718):
  - "found one corrupted feedback message in the lesson it created" → "found the practice planted by one corrupted feedback message in the lesson it created".
  - Rewrite the "…as rollback did … but it suspended almost as much as rollback" sentence (see the status table).
- l.2331: add "(indices of that run)" to avoid a false cross-reading with the running example.
- l.2239: "3.30 of them clean" is still in no table.
- E-C: give it its own Objective/Procedure, or call it E-M(b).
- l.2082: add the response's "the plan reproduces all 300 recorded revalidation decisions" if it was checked, since this turns a fixture test into evidence on real data.

**Code and artifacts**
- `revalidate(..., active_before=None)` (`revalidation.py:63-71`) silently restricts candidates to *deployed* members when the caller omits `active_before`. A cleared, active but undeployed memory would then never be re-admitted, contrary to Algorithm 5 l.1. Make the parameter required, or default it to the pre-withdrawal active set recorded in the last snapshot before the Withdraw event.
- Table XII: replace `\resizebox` with abbreviated headers.
- l.2528: provide an anonymized artifact link for review.

## Recommendation

**Minor revision.**

The authors made the round-6 changes that affect correctness:
- The state tuple of Definition 8 is clean.
- The copy map no longer collides with the mutant.
- Revalidation restricts candidates to members in use before the withdrawal.
- Revalidation keeps clean lineage through the active frontier, and the code, the evaluation and Algorithm 5 now agree.
- The abstract no longer claims a precision advantage over rollback.

The new selectivity analysis gives practitioners a structural reason to prefer one harness design over another, which is the kind of actionable result TSE readers value.

Required before acceptance:
1. Change l.2001 "Line 12" to "Line 10" (use `\label`/`\ref`). Make "affected set" mean one thing across Definition 5, Algorithm 4 and Algorithm 5; Algorithm 5 l.1 is Definition 5's affected set before withdrawal, so say that (Major 1).
2. Report the selectivity result for both post-composition rows (0.46 and 0.61, not 0.46 alone) in the intro, E-L, Lessons, RQ1 box and Conclusion. State that the low ratios hold only until the next broadcast composition and that the 24-task horizon ends there. Mark the 1-root ExpeL cell, rename "Strict", and note that only final active revisions are roots (Major 2).
3. Fix the abstract sentence that names rollback twice and has an ambiguous "it".

Strongly recommended:
- Split the five paragraphs above 320 words and cut the duplicated platform text, to stop the growth to 24 pages (Major 3).
- The carried-over minors: ⑩ in Fig. 1, Table II, the transitive "exposed to", the remaining letter clashes, E-C, "3.30 clean", Table XII legibility, and the `active_before` default.
