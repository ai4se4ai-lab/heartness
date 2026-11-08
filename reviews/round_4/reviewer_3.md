# Round 4 -- Reviewer 3 (presentation, clarity, relevance)

This is an internal, automated review of a draft. It is not independent peer review. Scores run from 1 (poor) to 5 (excellent). Line numbers refer to `docs/TSE/main.tex` as of this round (2,366 lines; generated macros end at l.1569). Page numbers refer to the compiled `main.pdf` (21 pages), which I read in full. I checked the numbers quoted below against the generated macro block. I also checked the approach against `src/heartness` (`engine.py`, `graph.py`) and the live harness (`experiments/live/harness.py`, `run.py`, `supplement.py`). For one claim I recomputed values from the raw Fir records of the curation campaign (`results/raw/hpc/fir/am-20261107-080855`). I edited no file other than this review.

## Summary

The paper presents Heartness, a model-driven controller for self-evolving agent harnesses. It has these parts:
- immutable revisions;
- host-side exposure capture, including experience-mediated exposure (EME);
- guarded admission;
- closure-based withdrawal across deployments, with rollback admissibility;
- a new closure-bounded revalidation step (Section III-F, Algorithm 5);
- bounded model checking with two encodings and witness replay;
- a conformance monitor.

Two propositions were added. One says closure never exceeds a rollback to before the fault (a time cut). The other says containment is inductive.

The live study now covers two policies: 5 generators × 2 policies × 5 seeds × (3 faults + clean) = 200 runs. Its new curation slice is what the round-3 story was missing.
- **Spread.** Under curation, a fault spread in 42 of 75 runs, against 10 of 75 under the ExpeL-style policy.
- **Recall.** Closure reached recall 1.00 under both policies.
- **Detectors.** Under curation they missed contamination: the embedding detector in 22 of 42 propagated runs, the LLM judge in 13 of 42. TF-IDF at the frozen threshold missed it in only 2, but suspended 11.27 revisions per run at precision 0.24.
- **Closure's cost.** Closure was strictly narrower than the time cut in 42 of 75 runs, but only slightly (20.79 vs 22.20 revisions suspended per run). Precision was 0.10 and F1 0.18 (Table VII).
- **EME edges.** They were the only lineage of a contaminated revision in one run. Removing them changed the closure in 55 of 75 runs and raised F1 from 0.18 to 0.31.

The rewrite is a real improvement. The narrative now matches the data in most places. The running example is anchored in quoted texts from two real curation runs. Revalidation has its own Approach subsection. The Table VIII anomaly is gone. Related work now covers taint tracking, unlearning, build systems and sagas. What remains:
- One substantive consistency problem: revalidation as evaluated is not Algorithm 5 (Major 1).
- Several summary statements (abstract, RQ1 box, conclusion) that are slightly more favourable than the tables (Major 2).
- A set of presentation debts carried over from round 3.

## Scores

| Criterion | Score | Justification |
|---|---:|---|
| (i) Novelty | 3/5 | Unchanged in substance. The integration is new: exposure closure including the EME channel, deployment-wide suspension, rollback admissibility, and a time-cut bound for LLM-written harness state. So is the two-policy measurement of how a single non-adversarial faulty lesson spreads. The individual techniques are known, and the paper now positions them well against taint tracking, build invalidation and unlearning (l.2321–2322). The empirical novelty is clearer now: detectors fail on composed artifacts, closure does not. |
| (ii) Rigor | 3/5 | Much improved. The paper uses paired win/loss counts, states effective n, restricts the Holm family, adds T/A/H_faulty controls, and checks Proposition 1 empirically ("contained in T's in all 75 runs"). Two things hold the score at 3. First, the evaluated revalidation (HS) differs from Algorithm 5: it restores cleared profiles whose dependency skills stay suspended in 18 of 75 curation runs, contradicting l.1932 (Major 1). Second, the price of the EME edges is under-reported in every summary (Major 2). |
| (iii) Relevance | 4/5 | Clearly SE: maintenance, change impact, traceability and rollback of self-modifying software. The new finding that "the policy decides what closure costs" (l.2291) is directly actionable for harness designers. So is the finding that detectors fail on composed artifacts (l.2293). It remains a prototype on function-level tasks, and there is no study with human maintainers (l.2303). |
| (iv) Verifiability and Transparency | 4/5 | Still exemplary. Generated macros, cached LLM responses, `make live-fir`, retained superseded campaigns, and CPU-fallback cells disclosed (l.2280). It is not 5 for three reasons: the HS mismatch is visible only from code, there is still no anonymized artifact URL (l.2359), and Algorithm 5's attestation mechanism has no counterpart in `src/heartness`. |
| (v) Presentation | 4/5 | Large improvement. The running example now quotes real runs (l.1647). Every component has a motivation/design/algorithm/example/limits block. The RQ boxes exist and are mostly calibrated. The two policy tables share one layout. Remaining issues: the abstract is about 296 words, over IEEE's limit; the intro "components" sentence is about 170 words (l.1603); the RQ1 box is 176 words; Fig. 1 does not show revalidation; there are small inconsistencies in the running example (task/memory indexing, "exactly this loop"); and several round-3 minor items are untouched. |

**Overall recommendation: minor revision**, conditional on Major 1. Major 1 needs either an offline re-analysis or a reworded claim plus a disclosure. It does not need new LLM runs.

## Status of round-3 issues

| Round-3 item | Status | Evidence / remaining gap |
|---|---|---|
| M1 similarity claims contradicted by E-L | **Resolved** | Intro l.1601 and Related Work l.2319 now say when similarity works (verbatim) and when it fails (paraphrase, composed artifacts). The curation slice supports the latter (Table VII; 22 of 42 R3 misses). |
| M2 running example vs live data | **Mostly resolved** | l.1647 quotes the gemma2 F1 seed-2 chain m7 → k1 → D1 profile and the llama3.1 F3 seed-3 EME case. Remaining gaps: (a) l.1640 still says "Our live study implements exactly this loop"; only the curation policy does. (b) Task/memory indexing is inconsistent; see Minor. (c) The example never shows the effect that dominates closure cost in the data: once p¹₁₂ is deployed, every later memory is EME-exposed (l.2160). See Major 3. |
| M3 revalidation missing from Approach | **Partially resolved** | Section III-F and Algorithm 5 were added, and l.1902 is reconciled. But Fig. 1 still has no revalidation box or arrow. The Limitations paragraph (l.2303) still says only "quarantine is permanent ... a corrected skill needs fresh lineage" and does not mention revalidation. Algorithm 5 also differs from what was evaluated (Major 1). |
| M4 Table VIII inconsistency | **Resolved** | The constant projection column was removed. Table X (l.2256) and the text (l.2268) now agree: the independent topology hits the cap from n=3, and the chain stays below 6,100. |
| M5 walkthroughs vs algorithms | **Resolved** | Profiles are not restored by withdrawal (l.1900). "m9 itself" (l.1902). The 7-operation witness is listed (l.1955). Contracts are reduced to dependency presence (l.1957). Admission is split into Propose/Validate/Accept, so P9 can fail (Algorithm 2). Closure includes the candidate (l.1855). |
| M6 related work gaps | **Mostly resolved** | New subsection V-E (l.2321). Table XI columns are now defined, and the EVOMAL and AgentSpec cells are corrected. Still missing: a row for git/file-level revert, which is the R1 baseline. Also, "Rollback" for build systems/registries is "--", although model registries do support version rollback. |
| M7 notation overload | **Partially resolved** | H→Λ for history is done. The R/B mapping is in prose (l.2030–2039). Not done: a one-line glossary separating withdrawn (W), quarantined (K) and suspended in Table I; an experiment → RQ → subject → metric map (there are now ten experiment IDs: E-L, E-Q, E-K, E-G, E-M, E-C, E-S, E-O, E-T, E-R); and an explanation of the acronym at l.1716, which still does not visibly yield "Heartness". |
| M8 tables, mixed denominators | **Partially resolved** | Table V/VII captions now state their denominators. The text still quotes values that are not in the tables: collateral per propagated run (3.30, l.2090), and pass@1 / signature on propagated runs (0.60→0.68, 0.09→0.02, l.2112). Add a "Coll. (prop.)" column, or put the propagated-run behaviour values in a small companion table. |
| M9 behaviour claims outrun evidence | **Resolved** | Pass@1 claims withdrawn. "Within the agent's sensitivity to context order" is well argued with order-flip counts (l.2112). Non-significance is stated each time. |
| Minor: title | Not changed | It still gives model checking equal billing (l.1572). This is acceptable but still my preference. |
| Minor: split six-component sentence (l.1603) | Not done | See Minor. |
| Minor: organization paragraph lacks Threats/Lessons | Not done | l.1622. |
| Minor: Def. 8 unexplained symbols | Resolved | Q, V, X, L, F are explained in prose (l.1677). |
| Minor: m7 vs m8 sources sentence | Resolved | l.1810. |
| Minor: compute-platform paragraph | Partially | It is still about 200 words with four numbered justifications (l.2013). Two sentences would suffice, since the threat is in IV-F. |
| Minor: R4 citation | Not done | l.2035, "of the kind proposed for skill-library screening", still has no citation. |
| Minor: HS forward reference | Resolved | It now points to III-F. |
| Minor: precision formula / recall denominators | Resolved | l.2048. |
| Minor: Fig. 2/3 legends | Resolved | Legends are now below the plots. |
| Minor: Fig. 4 caption wording | Not done | l.2188, "falls below lexical recovery when between one half and three quarters of the edges, or fewer, are captured", is unchanged. |
| Minor: "withdrawal guard" undefined | Not done | l.2202. Use "the P2 suspension guard". |
| Minor: E-C without own objective | Not done | l.2205. |
| Minor: RQ3 box "about a second" | Not done | Monitor replay is 2.97 s (`\MonitorMsThirtyTwo` = 2967.7 ms). Say "1–3 s" (l.2275). |
| Minor: MBPP+ / HPC bug list | Resolved | — |
| Minor: human-maintainer follow-up | Not done | l.2303 still only states the limitation. |
| Minor: anonymized URL | Not done (acknowledged) | l.2359. |
| Minor: Burgueño bib | Resolved | Ref. [52] renders correctly. |
| Minor: ExpeL timeline figure | Not done | It is less needed now that curation carries the story. Optional. |

## Major issues

### 1. The revalidation that was evaluated is not Algorithm 5, and the text says it is

**What the text claims.** Section III-F (l.1914) specifies the following:
- Cleared members are re-admitted "in history order, so a profile can be re-admitted only after the skills it depends on, and admission rejects it if one of them stays suspended."
- Algorithm 5, line 3 sets `dep(x') = dep(x)`.

The Limits paragraph (l.1932) then claims that the post-hoc evaluation "yields the same loadable state as Algorithm 5 without replaying the admissions."

**What the code does.** `experiments/live/supplement.py:restore()` simply unions every screen-cleared member back into the active set and into the original deployments. It applies no dependency or contract check, and no ordering.

**What the raw records show.** I recomputed this on the 75 curation records of `am-20261107-080855`:
- HS_judge restored a revision with a dependency that remained suspended in **18 of 75 runs (19 revisions)**. These are profiles whose skill stayed quarantined. Algorithm 5 would reject them (P3), so the evaluated state violates the paper's own P3.
- Taken literally, Algorithm 5 makes x′ depend on the *original* x's dependencies, and those originals stay in K by design (l.1914: "The original x stays quarantined"). Under that reading, any profile whose dependency skill is in the closure can never be re-admitted, even when the skill itself was cleared. That affects 69 restored revisions in all 42 propagated runs. So either dependencies must be remapped to the fresh copies (x ↦ x′), or Algorithm 5 cannot re-admit a dependent profile at all.

**Consequences.**
- The HS_judge and HS_emb curation rows (Table VII), the claim "Revalidation never touched anything outside the closure", and Lesson 3 (l.2293) all rest on a remedy the paper does not specify.
- The direction of the bias is predictable. Algorithm 5 would leave more suspended, giving higher recall and lower precision. It might also *remove* some of the residual contamination that HS_judge reintroduced.
- Algorithm 5's attestation mechanism ("a later withdrawal of the attestation ... withdraws all its re-admissions", l.1914) has no counterpart in `src/heartness`. `tests/test_eme.py::test_revalidated_readmission_is_a_fresh_attested_lineage` admits x′ as an `authorized_seed` with no attestation record. Since attestations are not in ⇝ and `Withdraw` takes a revision id, the paper does not say how withdrawing an attestation would find the re-admissions.
- P1 requires `src ∪ expr ≠ ∅` or a seed. x′ has `src = ∅`, so the paper should say that x′ is admitted as an authorized seed and that the attestation is that authorization.

*Required action.*
- Either (a) re-run the HS analysis offline with Algorithm 5's semantics, or (b) state exactly what was evaluated and replace "the same loadable state" with an honest description, giving the count of runs in which the two differ.
  - For (a): use history order, remap dependencies to re-admitted copies, and reject members with a suspended dependency. All screen verdicts are already stored in the records, so no new LLM calls are needed.
- Fix Algorithm 5, line 3: either `dep(x') = {y' if y was re-admitted, else y | y ∈ dep(x)}`, or say that dependents are re-admitted only when all their dependencies are outside the closure.
- Either implement attestation as a first-class revision with an edge to x′ (so that withdrawing it uses the ordinary closure), or drop the sentence.

### 2. Summaries are a notch more favourable than the tables (EME cost, generator coverage, "only closure")

The body of E-L is now admirably candid. The condensed statements that most readers will actually read are slightly off in four places.

- **EME price is omitted from the summaries.**
  - The intro (l.1605) says: "Experience-mediated exposure was the only lineage of a contaminated lesson in one run."
  - The RQ1 box (l.2193) says: "Experience-mediated edges were needed in one run."
  - The E-L body (l.2162) reports the other side. Without EME, the closure changes in 55 of 75 runs, suspension drops from 20.79 to 14.39 revisions per run, and F1 rises from 0.18 to 0.31, at the price of one contaminated revision in 42 propagated runs.
  - EME is the paper's headline concept (abstract, intro, Definition 4). The summaries should state both sides in one clause, for example: "EME edges were the only lineage of one contaminated revision; omitting them would have raised F1 from 0.18 to 0.31 in this setting."
  - Lesson 2 (l.2291) should also mention that EME is the channel through which a broadcast profile pulls the closure up to the time cut.
- **"for all five generators"** (RQ1 box, l.2193) follows "10 of 75 ExpeL-style runs and 42 of 75 curation runs". That reads as applying to both policies, but gemma2:9b and granite3.3:8b never propagated under ExpeL (l.2074). Write "under curation, for all five generators". The intro (l.1605, "for every generator") is true only for the pooled runs and should be qualified in the same way.
- **The conclusion (l.2354) overclaims in three ways.**
  - "Only closure-based withdrawal removed every contaminated derivative under both policies" contradicts l.2168, where T and A also did.
  - "Content detectors are cheaper in precision" is garbled; presumably "more precise" is meant.
  - "they fail exactly where synthesis dilutes or rewrites it" is too strong: TF-IDF at the frozen threshold kept recall 0.99, at the cost of 11.27 suspensions per run.
- **"because self-evolving harnesses broadcast synthesized state into every later context"** (l.2354) generalizes from the two policies the authors wrote themselves. Say "because both of our harness policies broadcast ...". The third future direction (l.2356) already treats this as a design choice, which contradicts the generalization.
- **"We prove ... containment is inductive over all operators"** (abstract, l.1588): the paper itself calls this a hand proof sketch (l.1980). The abstract should say "argue" or "give a proof sketch".

### 3. The running example hides the mechanism that dominates closure cost in the data

The running example's closure is {m7, m8, k1, p¹₁₂, p²₁₂} "plus any later revisions exposed to these" (l.1666, l.1900). The curation results (l.2160) show that "plus any later revisions" *is* the result. From the first profile composition onward, every task loads its deployment's profile, so every later experience and memory is EME-exposed. Closure therefore approaches the time cut, and precision is 0.10.

A reader who learns the example will expect a small, surgical closure and will be surprised by Table VII.

**Suggested fix.** Add one or two sentences to the III-E running example, for example: "Because every run after task 12 loads p¹₁₂, the memories m₁₂,…,m₂₃ are also EME-exposed and enter the closure; only m₈…m₁₁ written by runs that never loaded m₇ or its descendants are spared." Mirror the same point in Lesson 2.

This turns the paper's most important practical lesson into something a reader can trace by hand. It also prepares the reader for Proposition 1's "how far closure stays below the time cut is determined by the exposure structure".

### 4. Length and density: cut repetition, split the long sentences

TSE has no page limit, but at 21 pages the paper repeats its central results five times: abstract, intro results, E-L "both policies together" (l.2168), the RQ1 box, and the conclusion. Several of these units are themselves dense.

- **Abstract** is about 296 words. IEEE Transactions asks for 150–250. Drop the sentence listing the approach components (it is redundant with the following sentence) and the RQ2 clause.
- **Intro l.1603** is one sentence of about 170 words with six numbered clauses. Turn it into a list, or two sentences plus "(Fig. 1)".
- **Intro l.1605 results paragraph** (about 230 words) duplicates the abstract almost sentence for sentence. Keep the numbers in one of them and make the other qualitative.
- **RQ1 box** (l.2193) is 176 words in nine sentences. An answer box should be readable at a glance. Aim for about 5 lines: recall 1.00 in all 52 propagated runs; precision bounded by the time cut (equal under ExpeL, slightly lower under curation); detectors fail on composed artifacts (22/42, 13/42); EME is necessary once at a large precision cost; behaviour effects are not significant. The capture-sensitivity sentence can stay in E-K.
- **The E-L "both policies together" paragraph** (l.2168) and the RQ1 box say the same thing. Merge them, keeping the box.
- **The E-L ExpeL subsection** (l.2074–2112) could be shortened by about a third now that curation carries the main story. For example, cut the H_faulty and ablation sentences to one each, since both are "identical by construction" under ExpeL.
- **Compute-platform paragraph** (l.2013): see Minor.

## Minor issues

**Running example and Approach**

- **l.1640.** "Our live study ... implements exactly this loop": change to "The curation policy of our live study ...". Also "periodically each deployment's profile is rewritten" → "after tasks 12 and 24", matching l.2003 and `compose_at=(12,24)`.
- **l.1642 vs l.1647 vs l.1798.** Indexing is inconsistent.
  - The hypothetical says the misleading message arrives "at task 7" and becomes m₇, and that task 8's reflection writes m₈.
  - The quoted real run says "the corrupted message at task 8 became memory m₇".
  - l.1798 says "after task 12 the model contains m₀,…,m₁₁".
  - The code (`harness.py`, `mid = f"m{i}"`, with i 0-based) matches the latter two.
  - Fix: either shift the hypothetical to "task 8 → m₇, task 9 → m₈", or say that indices are illustrative.
- **l.1640/l.1647.** "merges m₇ with two unrelated lessons m₆, m₉" vs the real run "merged it with five unrelated memories". The code merges the whole six-task batch. Say "with the other lessons of its batch (here abbreviated to m₆, m₉)", as l.1798 already does.
- **Fig. 1 (l.1721–1769).** Add revalidation: a "screen / re-admit" arrow from the withdrawal engine back to admission, with a number and a caption entry. The figure is otherwise good. At print size, the `\scriptsize` arrow labels inside a `\resizebox` are near the readability limit; check them at 100%.
- **l.1900.** After withdrawal both deployments have no profile. Say what the live evaluation did in that case. `harness.py:194` silently falls back to `BASE_PROFILE[d]` when no profile is loaded, which is exactly the operator action that l.1900 says withdrawal does not take. One sentence in E-L's Procedure would make the pass@1 numbers interpretable.
- **l.1914.** "both relative to the withdrawn root": under ExpeL there are 1–4 roots per run (l.2007). Say which root the screen compares against when there are several.
- **Algorithm 5, line 5** redeploys to `Dpl_before(d)`, but `Dpl_before` is not defined. Define it as "deployment membership before Withdraw(r)".
- **Proposition 1 (l.1904).** "t(b) is the position of the event that accepted b" is undefined for seeds. Say that seeds have t = 0. Also make explicit that the time cut T in the evaluation is the snapshot before the *corrupted experience*, not before the root's acceptance (l.2036). The two differ by the extraction step, and the proposition is stated for the latter.
- **l.1716.** Either show how "Harness Evolution through Auditable Records, Typed dependencies, and Explicit State Semantics" yields "HEARTNESS" (capitalize the letters), or drop the expansion.

**Evaluation**

- **Table III (l.2022).** "29 held-out tasks × 14 conditions per faulty run": T, A and H_faulty have no held-out evaluation (Table V caption), so 11 conditions are solved. Say "14 conditions (11 with held-out evaluation)".
- **l.2041.** The frozen τ_t = 0.05 is the lowest grid value, so the pilot optimum sits on the grid boundary. Say so. It matters for interpreting R2's curation results ("kept recall high only because that threshold is low", l.2143).
- **l.2043.** "H is the full approach (withdraw all roots)": in ExpeL runs the roots include up to four non-faulty insights. One sentence explaining why withdrawing *every* revision motivated by the suspicious experience is the operational choice would help practitioners. l.2160 gives the reason (H_faulty misses 3 runs under curation); forward-reference it.
- **Fig. 3 caption (l.2157).** "Heartness and R2 at the frozen threshold are the only conditions with recall near 1": T and A also have recall 1.00 (Table VII). Say "the only non-rollback conditions" or "the only conditions plotted".
- **Table VII.** HS_judge suspends fewer revisions than R4 (2.71 vs 2.79 per propagated run) with the same recall (0.79). This deserves one sentence: under curation, revalidation with the generator-as-judge is essentially the judge. l.2164 implies it but never says it.
- **l.2162.** "EME edges therefore bought one contaminated revision in 42 propagated runs at the price of 55 runs with more collateral": good. Move this sentence, or its essence, into the RQ1 box (Major 2).
- **l.2202.** "Removing the withdrawal guard": name it (the P2 suspension guard).
- **l.2205.** E-C still has no Objective/Procedure of its own. Either promote it or label it "E-M(b)".
- **l.2240 vs l.1957.** The Discussion says the projection is "without text, contracts, EME or effects", but l.1957 says it "reduces contracts to the presence of dependencies". Make them consistent: "without text, with contracts reduced to dependencies".
- **l.2275, RQ3 box.** "reach about a second for 32-artifact workloads": monitor replay takes 2.97 s. Say "1–3 s".
- **l.2286, conclusion validity.** It gives the effective sample only for ExpeL (10 of 75). Add curation (42 of 75).
- **l.2303, Limitations.** "quarantine is permanent in our prototype, so a corrected skill needs fresh lineage": add "or closure-bounded revalidation (Section III-F)" for consistency with l.1902.
- **l.2013.** Reduce the compute-platform paragraph to two sentences: one cluster and one GPU type, with smoke runs on three other sites used only for debugging; pinned stack recorded per run. Move the four-point justification to the replication package. The threat is already in IV-F (l.2282).
- **l.2035.** Add a citation for "of the kind proposed for skill-library screening" (EVOMAL's gate or VASO, if that is what is meant), or delete the clause.
- **Fig. 4 caption (l.2188).** Reword to: "Recorded exposure degrades in proportion to missing edges; below roughly 60–75% capture, lexical recovery is more accurate."

**Related work and the rest**

- **Table XI (l.2327).** Add a row for "git / file-level revert" (the R1 baseline): persistent state ✓, rollback ✓ (exact, without the withdrawal check), everything else "--". Also reconsider "Rollback --" for model registries. The `\resizebox` makes the table font very small on p.20; abbreviate the headers instead.
- **l.1622.** Mention Threats (IV-F) and Lessons (IV-G) in the organization paragraph.
- **l.2301, "Make live studies replayable".** This is a good lesson. The CPU-fallback observation is better placed in Threats, where it already appears (l.2280).
- **l.2303.** "We did not study usefulness for human maintainers." For TSE, add one sentence on what such a study would look like, for example incident-response tasks with and without withdrawal plans, measuring time to containment and residual contamination.
- **l.2359.** Provide an anonymized artifact link for review (Zenodo or anonymous.4open.science). A camera-ready DOI does not help reviewers.
- **General.** Many sentences in the Results paragraphs exceed 50 words (for example l.2088, l.2143, l.2160, l.2162). One claim per sentence would make the E-L results much easier to scan. The paragraph-opening italic labels ("Results (curation): ...") work well; keep them.

## Recommendation

**Minor revision**, with one required substantive fix.

Since round 3 the paper has turned around:
- The story now matches the evidence. Closure gives guaranteed recall at a precision bounded by the policy's exposure structure; detectors win on verbatim copies and lose on composed artifacts; EME is real but rare and costly.
- The running example is grounded in quoted live runs.
- Revalidation is specified in the Approach.
- The formal claims are scoped honestly.

For a TSE audience the paper is readable, relevant, and unusually transparent.

Before acceptance the authors must:
1. Reconcile the evaluated revalidation with Algorithm 5 (Major 1), by re-analysis or by an exact description with the 18/75 discrepancy disclosed, and fix Algorithm 5's dependency handling and attestation claim.
2. Calibrate the abstract, RQ1 box and conclusion (Major 2): EME's precision cost, "all five generators", "only closure", "prove".
3. Add the profile-broadcast step to the running example (Major 3).
4. Shorten the abstract to IEEE length and condense the RQ1 box (Major 4).

The remaining items are editorial.
