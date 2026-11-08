# Research reading and evidence design

Reading date: 2026-11-06. Sources are primary author copies, publisher/conference
records or standards. The supplied bibliography mixes preprint and proceedings
years (notably TraceFL and BOMs Away); it was not copied into the paper verbatim.
The local source survey is treated as a technical report, not a TSE publication.

| Published work read | What supports its argument | Consequence for Heartness |
|---|---|---|
| Burgueño et al., *Static Fault Localization in Model Transformations*, TSE 2015, DOI 10.1109/TSE.2014.2375201; [author manuscript](https://javiertroyauma.github.io/publications/TSE2015_prePrint.pdf), especially §§3–5 | distinguishes alignment correctness, missing alignments, and diagnostic usefulness; mutation-based evaluation | test the graph, guard behavior and diagnostic witness separately; record surviving faults and oracle limits |
| Ghassabani et al., *Inductive Validity Cores*, TSE 47(2), 279–299, 2021, DOI 10.1109/TSE.2019.2891709; [institutional publication record](https://experts.umn.edu/en/publications/inductive-validity-cores/) | explicitly separates soundness, minimality and computation cost | shortest BFS witnesses need replay and a shorter-depth negative check; scope reductions must not silently imply global safety |
| Gill et al., *TraceFL*, ICSE 2025; [paper](https://arxiv.org/html/2312.13632v4), evaluation and threats | attribution mechanism is evaluated across tasks/models and perturbed conditions, with scale measured separately | query accuracy, incomplete capture, lexical change, state-space cost and model correspondence need distinct campaigns; exposure is weaker than behavioral attribution |
| Stalnaker et al., *BOMs Away!*, ICSE 2024, DOI 10.1145/3597503.3623347; [author manuscript](https://www.twstalnaker.com/resources/icse24.pdf), methods, discussion and threats | evidence comes from stakeholder study, with sampling and external-validity limits | practical relevance cannot be established with synthetic graphs alone; artifact replay is a feasibility check, not practitioner validation |

Additional directly inspected sources: [W3C PROV-DM](https://www.w3.org/TR/2013/REC-prov-dm-20130430/),
[RADIANT](https://arxiv.org/html/2607.16708v1),
[PROV-AGENT](https://arxiv.org/html/2508.02866v3),
[Voyager](https://arxiv.org/abs/2305.16291),
[ExpeL](https://arxiv.org/abs/2308.10144), and the
[source survey](https://zgcagi.github.io/Harness-RSI/).
RADIANT already covers element-level traceability and model checking; novelty must
therefore be narrower than combining MDE and formal checking. Heartness investigates
persistent harness revocation across reuse and the tension with rollback, plus
explicit observation limits. PROV-AGENT supplies agent workflow provenance; a fair
comparison would add its capture to the same lifecycle rather than assume it lacks
every feature not discussed in the paper.

## Evidence that is still required for a strong submission

The current project can support bounded protocol claims and controlled synthetic
measurements. It cannot establish deployment utility, source behavioral causality,
or self-improvement. A convincing external-validity extension needs instrumented
operational updates in multiple harnesses, independently reviewed incident labels,
a stronger tuned history/recovery baseline, and practitioner diagnosis tasks.
The manuscript must make this distinction visible in its abstract and conclusion.
