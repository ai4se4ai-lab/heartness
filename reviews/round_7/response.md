# Round 7 response

Reviewers: R1 minor, close to accept (N4/R4/Rel4/V4/P4); R2 minor (N3/R3/Rel4/V4/P4);
R3 minor (N3/R4/Rel4/V4/P4). Internal automated review.

| Request | Action |
|---|---|
| R1.1 copies drop inactive clean ancestors (probes C, D) | Kept sources and the frontier now include clean ancestors whether active or not (retired, replaced); "active frontier" renamed "clean frontier" in code, docstring, Section III-F and Algorithm 5; probes C and D added as tests. |
| R1.2 window effect | Stated in E-L: both task-24 profiles are in the closure of every late root (verified: 1,200/1,200), so sparing lasts until the next broadcast composition; horizon caveat; qualifier added to intro and Lessons. |
| R1 optional symbol a | Attestation is α throughout Section III-F and Algorithm 5. |
| R2.1 / R3.2 selectivity quoted from its best cell | Intro, E-L and Lessons report 0.46–0.61 for both post-composition blocks; "revisions created after" instead of "a fault would have"; "nearly a time cut" for early roots. |
| R2.2 disclosure | Threats: selectivity added after round 6, definition revised once (same-step revisions). |
| R3.1 line reference; affected set | P2 line labelled (\label/\ref; resolves to 10). Algorithm 5 starts from Cl(R) restricted to in-use revisions (Definition 5's affected set); Algorithm 4 uses Z for the full closure. |
| R3.2 table | Caption: roots are revisions active at the end; ExpeL 1–6 row rests on one root; column renamed "Smaller". |
| R3.3 abstract sentence | Rewritten (rollback named once, subject clear). |
| R3 code | `revalidate(active_before=...)` is now required. |
| R2/R3 "Precision tells the other half" | Reworded ("On F1 and collateral the comparison reverses."). |

Not done: human oracle audit; anonymized link; Table XII resizebox; further paragraph splitting
(paper is 24 pages; TSE has no page limit).
