# Reviewer 3: Presentation and relevance to software engineering (round 3)

This is an internal, automated review of a draft. It is not independent peer review and should not be cited as evidence that the paper is ready for submission. Scores run from 1 (poor) to 5 (excellent).

**Material.** I compiled `docs/TSE/main.tex` (pdflatex, bibtex, pdflatex twice). It built with no errors, no undefined references and no overfull boxes; there were only minor underfull warnings and one font-shape substitution. The PDF is 16 pages, and I read all of it. I also read the generated macros at the top of `main.tex` (lines 35–540) and checked the numbers quoted in the text against them. I did not change any file except this review.

**Pending parts, by agreement with the authors.** The curation-policy slice of the live study, the RQ1 answer box, the abstract, the intro results paragraph and the conclusion are still placeholders. The sentence about "two open-weight LLMs" (line 575) is known to be stale. I do not penalize any of these for being missing. I do say below what each of them has to deliver.

## Summary

The paper presents \sys{} (Heartness), a model-driven controller for "self-evolving" agent harnesses. These are harnesses whose memories, skills, insights and prompts are written by the LLM itself. The controller has six parts:
- a metamodel of immutable revisions, experiences, snapshots and deployments;
- host-side capture of what each generation step and each agent run was shown, including the "experience-mediated exposure" (EME) channel;
- guarded admission;
- closure-based withdrawal that propagates to every deployment and rejects unsafe rollbacks;
- bounded model checking of a finite projection, with two encodings (BFS and SPIN) whose witnesses are replayed on the implementation;
- a runtime conformance monitor.

The evaluation has three subjects. S1 is a live HumanEval+ harness: 5 generators × 5 seeds × (3 planted faults + 1 clean run) = 100 runs, all reported with the ExpeL-style insight policy. S2 is a synthetic provenance benchmark. S3 is a replay of Voyager's skill library. There are three RQs: containment, assurance, and cost/limits.

The live ExpeL-style results are honest, and they are sobering:
- A planted fault spread beyond its root in only 10 of 75 runs.
- Closure reached recall 1.00 but precision 0.33 (F1 0.48).
- The TF-IDF, embedding and LLM-judge detectors reached equal or higher F1 (0.60, 0.50, 0.65).
- The EME and dependency ablations changed nothing.
- The best condition was closure-bounded revalidation (HS_judge, F1 0.67), and no difference survives Holm correction.

The engineering, the assurance chain (guard challenges, mutants, two encodings, witness replay, mapped-state comparison) and the reproducibility pipeline are strong. Presentation is the paper's weakest dimension. The main problems are these:
- The narrative (intro, running example, related work) was written for a result the live data does not currently show: a curation hierarchy with EME and paraphrase defeating similarity.
- The contribution that performs best (revalidation) is not described in the Approach.
- One results table (Table VIII) contradicts both its own text and another table.

## Scores

| Criterion | Score | Justification |
|---|---:|---|
| Novelty | 3/5 | Bringing exposure-closure withdrawal, deployment-wide suspension and rollback admissibility to LLM-written harness state is a new framing, and the EME concept is a real insight. The individual techniques are known: reachability-based impact analysis, PROV-style capture, guarded transitions and bounded explicit-state checking. Novelty rests on the integration and on the empirical study. So far the live study shows closure *tying or losing* on F1 against simple detectors, with the advantage confined to recall. |
| Rigor | 3/5 | RQ2 is rigorous and well controlled: negative controls, minimality checks, an equal-budget comparison with random and Hypothesis testing, and a model–code mismatch found by replay. RQ1 is statistically careful (paired tests, Holm, Â12, sensitivity of the oracle, a pilot kept separate from tuning), but its effective sample is only 10 propagated runs and nothing is significant. Several running-example and table statements are internally inconsistent (Major 3 and 4). |
| Relevance | 4/5 | This is clearly an SE problem: maintenance, change impact, traceability and rollback for software that rewrites itself, especially coding agents. The Lessons section turns the results into design guidance ("the policy decides what closure costs"), which is valuable. Relevance would be higher with related work on taint/information-flow tracking, machine unlearning and ML artifact lineage, which SE readers will expect. |
| Verifiability and Transparency | 4/5 | This is excellent practice. Every number comes from generated macros with an index back to its source file; LLM responses are cached so runs can be replayed; model digests and dataset checksums are pinned; superseded campaigns are kept. Two things hold the score at 4. Table VIII shows a suspicious constant column (Major 4). The Data Availability section gives no (anonymized) URL for reviewers. |
| Presentation | 3/5 | The structure follows the committed template closely. The overview figure is good. Each component has motivation, design, pseudo-code, a running example and limits. Against that: the running example no longer matches the reported live evidence; heavy jargon and symbol overloading (H, HS, EME, B0–B3 vs R1–R4); very long sentences and paragraphs; tables whose captions mix denominators; a key technique (HS) that appears only in the Evaluation. |

## Structure check

| Required element | Status | Comment |
|---|---|---|
| Abstract | Placeholder | Pending, by agreement. |
| Intro: motivation | Present (l.567–569) | Strong and concrete; the EVOMAL persistence result is a good hook. |
| Intro: problems of state of the art | Present (l.571) | One dense 150-word paragraph. Its claim that LLM synthesis "deliberately removes" textual resemblance is contradicted by E-L (Major 1). |
| Intro: high-level approach | Present (l.573) | All six components are packed into one sentence of about 120 words. Needs splitting, or a pointer to Fig. 1. |
| Intro: brief results | Placeholder | Pending. Must report the calibrated outcome (Major 1). |
| Intro: contributions | Present (l.577–583) | Reasonable. The third bullet should name closure-bounded revalidation, since it is the best-performing idea. |
| Intro: exactly three RQs | Present (l.585–590) | Yes, each with a motivation. Good. |
| Intro: organization | Present (l.592) | Does not mention Threats and Lessons (minor). |
| Background: motivated-then-defined concepts | Mostly | Every subsection motivates before defining. Def. 8 introduces Q, V, X, L, F with no explanation and no entry in Table I. |
| Background: one running example used throughout | Present but mismatched | The example is the *curation* policy. All reported live results are *ExpeL-style insights* (Major 2). |
| Approach: overview figure | Present (Fig. 1) | Clear, numbered, with a stand-alone caption. Revalidation is missing from it. |
| Approach: one subsection per component, with motivation, prose, short pseudo-code, step-by-step example | Present for 6 components | The structure is consistent and good. Closure-bounded revalidation has no subsection, algorithm or example (Major 3). The metamodel has no pseudo-code, which is acceptable. |
| Evaluation: implementation | Present (l.917–920) | Good. |
| Evaluation: setup | Present (l.922–975) | Thorough, but the compute-platform paragraph (l.939) is too long for the main text. |
| Evaluation: per-experiment objective | Present | Each of E-L, E-Q, E-K, E-G, E-M, E-S, E-T and E-R has an Objective and a Procedure. E-C is embedded inside E-M without its own objective. |
| Evaluation: one subsection per RQ ending with "Answer to RQ#" | RQ2 and RQ3 yes; RQ1 placeholder | Pending. |
| Threats to validity | Present (l.1131–1140) | Complete and candid. One stale item (MBPP+). |
| Lessons learned | Present (l.1142–1155) | Mostly actionable (see Strengths). One item is HPC housekeeping. |
| Related work: grouped, compared, comparison table | Present (l.1158–1195, Table IX) | Five groups, each says what is added. Missing areas (Major 6). Table IX column semantics need definitions. |
| Conclusion | Placeholder | Pending. |
| Data availability | Present (l.1201–1202) | Thorough content description. No anonymized link. |

## Strengths

1. **Problem framing that speaks to SE readers.** The intro asks "where did this behaviour come from, what else inherits it, which deployments load it, and how do we remove it without reintroducing it on the next rollback?" (l.569). Phrasing the problem as everyday maintenance questions is exactly right for TSE. The analogy to change impact analysis and slicing (l.630) is apt.
2. **The template is applied consistently.** Every Approach subsection has Motivation / Design / Algorithm / Running example / Assumptions-limits. A newcomer can follow the controller component by component, and the explicit assumptions (A1–A3) are a model of scoping.
3. **The overview figure** (Fig. 1) separates trusted from untrusted parts, numbers the flows, and has a caption that stands alone.
4. **The empirical reporting is honest.** The paper reports adoption and propagation counts (Table IV) rather than averaging over runs with nothing to contain. It states non-significance plainly, gives oracle-tuned upper bounds for the baselines, and explains why the EME and dependency ablations are uninformative under ExpeL. This candour is unusual and valuable.
5. **The lessons are actionable.** "The policy decides what closure costs" (l.1145) and "Closure is a bound, detection is a filter" (l.1147) are concrete recommendations to harness designers. "Check the model against the code" (l.1151) is backed by an anecdote: replay found a specification gap that two encodings agreed on.
6. **Reproducibility engineering.** Generated macros, cached responses, pinned digests and kept superseded campaigns make the numbers auditable.

## Major concerns

1. **The intro and related-work claims about similarity-based recovery are contradicted by the reported live evidence.**
   - The intro (l.571) says IR traceability and semantic detectors fail because "LLM synthesis deliberately removes" textual resemblance.
   - Related Work (l.1171) says "The live study shows why recovery is insufficient here: ... similarity between a root and its derivatives is low, and behaviour-mediated inheritance leaves no textual trace at all."
   - In E-L, however, TF-IDF and embedding recovery reached recall 1.00 at the frozen thresholds and F1 0.60/0.50, against 0.48 for \sys{}. The LLM judge reached F1 0.65.
   - The paper's own example run shows the root insight being "re-emitted verbatim" (l.998).
   - Under the only reported policy, behaviour-mediated inheritance produced zero distinct edges (H¬EME identical to H in 75/75 runs).

   *Action:* Rewrite l.571 and l.1171 so they claim only what the data shows. Similarity fails under paraphrase in S2 (E-Q: lexical F1 drops to 0.69). Closure's advantage in the live study is *guaranteed recall with a bounded candidate set*, not higher F1. If the curation slice shows that similarity fails on hierarchical, paraphrased state, cite that result specifically. The pending abstract, results paragraph and RQ1 answer must state outright that closure alone was the *least* precise remedy under ExpeL-style insights and that HS_judge was best, without significance.

2. **The running example describes a policy and phenomena that the reported live data does not show.**
   - Section II-B (l.610) says "Our live study implements exactly this loop," and l.618 says "This example is a compact version of what we observed in the live study."
   - Neither is true of the reported results. They come from the ExpeL-style policy: one flat list of insights, with no memories, skills, profiles, dependencies or distinct EME edges. The concrete example in the results (deepseek, F1, seed 2) is an *insight* being re-emitted by merges.
   - A newcomer who learned m7 → k1 → p12 and m7 ⇝ m8 will find none of these structures in Tables IV and V.

   *Action, either:*
   - (a) Once the curation slice lands, show an actual curation run that reproduces the m7/k1/p12/m8 pattern (quote the real texts) and say which parts were observed. Or:
   - (b) Add a short second example in Section IV-C for the ExpeL-style policy (insight list, ADD/EDIT/AGREE, the whole list exposed to each extraction). Make clear that the running example illustrates the curation policy.

   In either case, soften l.610/l.618 to "the curation policy of our live study implements this loop." If the curation slice also shows no EME effect, the running example's centrepiece (m8) has no empirical support and should be presented as a motivating scenario only.

3. **Closure-bounded revalidation (HS) is a headline result but is absent from the Approach.**
   - HS is mentioned in the intro (l.573, "optional closure-bounded revalidation") and first defined in the Evaluation (l.967), which points to "Section IV-C" (the RQ1 section itself).
   - It gives the best F1 (l.1016) and is the main recommendation in Lessons (l.1147).
   - Section III-E, meanwhile, says "Quarantine is permanent in this prototype; re-admitting a corrected skill requires a fresh lineage" (l.867), which reads as contradicting HS ("re-admits ... as fresh attested revisions", l.967).

   *Action:* Add a subsection (e.g., III-E') covering:
   - the motivation (closure is a bound, detectors are filters);
   - the design: which screen is used, what "fresh attested revision" means, and how it interacts with W/K, P2 and rollback;
   - a 5-line algorithm and a running-example step;
   - a new arrow or box in Fig. 1.

   Reconcile it with l.867.

4. **Table VIII and its text are inconsistent with each other and with Table VI.**
   - The "Proj. states" column is the constant 3,317 for every n (2–6) and both topologies.
   - Table VI reports 93,266 projection BFS states for n=3, independent topology, at the same depth 10.
   - The text (l.1122) says Table VIII "shows the expected exponential growth" and that "beyond five identities the full-engine BFS hits the 20,000-state cap." The table shows the cap already at n=3 for the independent topology, and near-flat growth for chain (3,317 → 6,016).
   - Either the projection column records the wrong quantity (it looks like it is fixed at n=2), or the scopes differ and the caption does not say so.

   *Action:* Check `scale` in the processed results and `scripts/paper_macros.py` (around line 113). Fix or explain the column, correct the text, and label the unlabeled "s" column. Since the paper's credibility rests on its "every number is generated" promise, an anomaly like this is especially costly.

5. **Several running-example walkthroughs do not match the algorithms they illustrate.** A reader who traces them step by step will lose confidence.
   - l.865: after Withdraw(m7) both deployments "fall back to the base profile and k0." Algorithm 4 only removes the closure. It does not reactivate p0, which p12 *replaced* (line 6 of Algorithm 2). Either Withdraw restores replaced revisions (then say so and show it in Algorithm 4), or the deployments are left with no profile (then say that, and explain how they recover).
   - l.867: "m9's descendants are not suspended." k1 *is* a descendant of m9 and is suspended. Presumably "m9 itself" is meant.
   - l.888: the listed sequence (Propose/Validate/Accept m7, k1; Withdraw m7; Accept p12) has at least 10 operations if p12 must also be proposed and validated, yet it is called a "7-step witness". Give the actual 7-operation witness, perhaps as a small inset trace or table.
   - l.890 says the projection omits "contracts as arbitrary sets," yet P3 (contract consistency) is checked on the projection (Table II) and the witness yields a P3 violation. Explain what contract fragment the projection keeps.
   - l.821/Algorithm 2: P9 (stale base) can never fail inside a single sequential Admit, because line 2 sets base = |Ver|−1 and line 5 checks the same value. Show Propose and Accept as separate steps with an interleaving, as the prose does.
   - l.821: "any later proposal that merges m8 is rejected by line 7" requires the candidate itself to be in Cl(W ∪ K). Say that closure is computed over the graph *including* a's source edges.

6. **Related work misses areas that SE reviewers will raise immediately.**
   - **Dynamic taint and information-flow tracking.** EME is essentially taint propagation through the agent's execution: context → behaviour → new artifact. The analogy is natural, and the differences should be explained (no influence tracking, over-approximation by construction).
   - **Machine unlearning and data deletion.** This is the closest ML analogue of "withdraw an input's influence from derived state."
   - **ML artifact lineage and versioning:** DVC, MLflow, model registries, data-pipeline provenance.
   - **Configuration management and feature-flag rollback** in continuous deployment, which motivates deployment-wide suspension.

   In Table IX, define each column precisely. For example, AgentSpec gets "Runtime conformance ✓", but it enforces action rules; it does not check conformance of a lifecycle log. "Live eval." is defined in the caption, but EVOMAL's "quarantine gate" is listed under *deployment-wide withdrawal*, which it is not. Add rows for capture-only PROV and for git or file-level revert, since both are baselines.

7. **Terminology and notation overload hurt readability for a general SE audience.**
   - *H* names both the append-only event history (Def. 8, Table I, Fig. 1 "event log H") and the full approach variant ("H", "H_local", "HS", Table V). Rename the variants, e.g. "Heartness / Heartness-local / Heartness+screen", or "C" for closure.
   - S1 baselines are R1–R4; S2 baselines are B0–B3 (l.958–963). These are partly the same baseline under two names. Use one scheme, or add a mapping table.
   - EME, closure, affected set, suspension, quarantine and withdrawal are used close together. Add a one-line glossary to Table I that separates *withdrawn (root, W)*, *quarantined (closure member, K)* and *suspended (removed from Act/Dpl)*.
   - Experiment IDs (E-L, E-Q, E-K, E-G, E-M, E-C, E-S, E-T, E-R) are not mnemonic, and E-L is reused for cost under RQ3. Table III says "16 experiments," but nine are named. Add a table: experiment → RQ → subject → metric → section.
   - The acronym expansion at l.686 ("Harness Evolution through Auditable Records, Typed dependencies, and Explicit State Semantics") does not visibly yield "Heartness". Explain it or drop it.

8. **The tables do not stand alone, and Table V mixes denominators.**
   - In Table V, "Susp. (all)" and "Susp. (prop.)" sit next to Precision/Recall/F1 (propagated runs only), Residual/Collateral (all runs) and Pass@1 (all runs).
   - The text then quotes values that are not in the table: collateral 3.30 per propagated run, and pass@1 0.60 → 0.68 on propagated runs (l.1014, l.1020).

   *Action:* Split Table V into (a) propagated runs, with Susp., P, R, F1, Residual, Collateral, Pass@1 and Signature, and (b) all runs. Alternatively, add the propagated-run columns the text relies on. Add CIs, or at least note which differences are significant. Table IV should also give the per-fault adoption counts that are currently only in the prose (l.998).

9. **Claims about behaviour outrun the evidence.**
   - l.1020: "pass@1 after Heartness was the highest of all conditions." The value is 0.62, against 0.61 for R3, HS_emb and the clean reference, with p = 1.0. That is noise, and saying it invites scepticism.
   - "a consistent direction" with Â12 = 0.70 and p_Holm = 1.000 from 10 runs is too strong. Say "a non-significant tendency."
   - l.1147 "gave the best F1 in our study ... We recommend this combination": qualify it as not significant and policy-specific.
   - l.1012 and l.1149: the H_local result ("Withdrawal must reach deployments") follows by construction, since deployments load their own membership. Present it as a confirmation of a design requirement, not as an empirical finding.

## Minor concerns (main.tex line numbers)

- l.543: The title gives "Bounded Model Checking" equal billing, although the main SE contribution is traceable withdrawal and the live study. Consider "... A Model-Driven Approach" alone.
- l.573: Split the six-component sentence into a list or two sentences, and refer to Fig. 1.
- l.575: Stale "two open-weight LLMs" (known). "100 runs" will also change when the second slice is added.
- l.592: The organization paragraph should mention Threats (IV-F) and Lessons (IV-G).
- l.648 (Def. 8): Q, V, X, L, F are introduced in a 13-tuple and never used again. Either add them to Table I or present only the components used later.
- l.659: Table I floats into Section III (page 4). Place it at the start of Section II, or use `[t]` placement there.
- l.769: "After task 12 the model contains m0,…,m11". With one memory per task, m12 should exist. Check indexing.
- l.796: m8's sources are {m5, m6}, but the context lists three memories including m7. Briefly say why m7 is not a synthesis source (it was in the run context, not in the reflection input). This is the whole point of EME and deserves one sentence.
- l.888: Give the actual witness as a small trace.
- l.933 / l.948: "For each policy" and "1 policies" (Table III). Fix the grammar and update after the second slice. "5 open-weight generators" vs. macro `\LiveModels`: fine.
- l.935: EvoTraceBench 1.1 is introduced as if known. Say it is the authors' benchmark and where its datasheet is.
- l.939: The compute-platform paragraph is about 300 words of justification for using one cluster. Reduce it to two sentences and move the rest to the replication package. The threat is already in IV-F.
- l.961: R4 "of the kind proposed for skill-library screening" has no citation.
- l.967: HS is defined here, with a forward reference to its own section (see Major 3).
- l.972: The precision formula |S∩C|/|S\A|: say whether roots are in S and excluded, since C excludes roots.
- l.975: "Recall and F1 are computed only for runs in which contamination propagated". Precision, too, according to Table V's caption. Make the two consistent.
- l.998: This paragraph is about 280 words. Split it into adoption and persistence.
- l.1018: Ablations that change 0/75 runs could be dropped from Table V (three identical rows) and reported in one sentence until the curation slice shows a difference.
- l.1022: `%LIVE-CURATE-PLACEHOLDER`. The curation results must (a) show whether H¬EME and H¬dep differ from H, which is the only evidence for EME and dependency edges in the live setting; (b) report closure precision under a hierarchical policy, to test the "policy decides cost" lesson; (c) report whether similarity loses recall on paraphrased skills and profiles, to support l.571 and l.1171; (d) use the same table layout as Table V for direct comparison.
- l.1042 (Fig. 2): The legend overlaps the "Heartness" curve between x = 0.5 and 0.75. Move it to the north-west or outside. Reword the caption: "falls below lexical recovery when between one half and three quarters of the edges, or fewer, are captured" is hard to parse.
- l.1047: The RQ1 answer box (pending) should state containment (recall), precision cost, the HS result, non-significance and the capture-sensitivity crossover, in no more than 5 lines.
- l.1056: "Removing the withdrawal guard" names a guard not defined elsewhere. Use the P-number.
- l.1059: E-C is described inside E-M without its own Objective or Procedure. Promote it, or clearly mark it as part of E-M.
- l.1062 (Table VI): Repeating "yes" in all 18 rows of the Agree column adds little. Consider merging the topology rows per mutant to make the table more compact.
- l.1104: "one run took 3.9 minutes of evolution". Report the range across generators too.
- l.1111 (Table VIII): Unlabeled "s" column. See Major 4.
- l.1129 (RQ3 box): "reach about a second for 32-artifact workloads" understates monitor replay (2.97 s). Say "1–3 s".
- l.1132: "HumanEval+/MBPP+ tests". MBPP+ is not used anywhere. Remove it.
- l.1134: "both policies" is fine once the second slice is in. Until then it is inconsistent with `\LivePolicies` = 1.
- l.1153: The list of HPC deployment bugs (stale file name, memory request, download path) is not a software-engineering lesson. Keep the caching lesson, and move the bug list to the replication package.
- l.1155: "We did not study usefulness for human maintainers". This is a significant limitation for a TSE paper on maintenance. Say what a follow-up study would look like.
- l.1177 (Table IX): Define the columns in the caption or a footnote. The resizebox makes the font very small. Consider abbreviating the headers and dropping resizebox.
- l.1202: Provide an anonymized artifact URL (e.g., Zenodo or anonymous.4open.science) for review, not only "a DOI for camera-ready."
- Bibliography: Ref. [44] renders as "L. B. no". The BibTeX `Burgue\~no` must be `Burgue{\~n}o`. Ref. [19] title quotes render unbalanced. Several 2026 arXiv references: make sure the versions are stable.
- General: many sentences exceed 40 words (e.g. l.571, l.573, l.689, l.803, l.939, l.998, l.1012). For a general SE audience, aim for one claim per sentence in the Introduction and in Results.
- General: Add a small figure for the ExpeL-style live run (a timeline of insights, their exposure edges, the root, contaminated derivatives and the closure). It would show "why closure ≈ whole state under ExpeL" better than any prose, and would make Lesson 2 concrete.

## Recommendation

**Major revision.** This assumes the pending parts are completed as planned.

The paper tackles a timely, genuinely SE-relevant problem. Its assurance chain and reproducibility are well above average, and its reporting is commendably candid. The current draft, however, tells a story the evidence does not yet support:
- the running example and the motivation rest on curation hierarchies, experience-mediated exposure and the failure of similarity;
- the reported live data (ExpeL-style) shows a flat list, no EME effect, and detectors matching or beating closure on F1.

The pending curation slice may restore part of that story, but the text must be rewritten to match whatever it shows. Before resubmission the authors must at minimum:
- move closure-bounded revalidation into the Approach;
- fix the Table VIII inconsistency;
- align the running-example walkthroughs with the algorithms;
- disambiguate H and the baseline naming;
- calibrate the behavioural claims;
- extend related work to taint tracking, unlearning and ML lineage.
