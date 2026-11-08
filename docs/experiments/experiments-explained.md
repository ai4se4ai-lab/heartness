# HEARTNESS in plain language: the problem, the approach, and every experiment

This document explains the whole study without assuming you know the field. It covers what
problem we are solving, what we built, and every experiment we run, with the reason for each
(its *objective*), how it works, what we measure, and what it can and cannot tell us.

It describes the completed study and the results reported in
[the current paper](../TSE/main.tex), including both live harness policies, controlled
experiments, and follow-up analyses. Planned configurations are distinguished from the ones
actually run. Reproduction sources are listed at the end; completion status is in
[Section 7](#7-where-things-stand).

**Contents**
1. [The problem](#1-the-problem)
2. [The approach](#2-the-approach)
3. [The three research questions](#3-the-three-research-questions)
4. [The live study (real AI models)](#4-the-live-study-real-ai-models)
5. [The controlled experiments (synthetic data)](#5-the-controlled-experiments-synthetic-data)
6. [Running it on supercomputers](#6-running-it-on-supercomputers)
7. [Where things stand](#7-where-things-stand)
8. [What this study cannot show](#8-what-this-study-cannot-show)
9. [Glossary](#9-glossary)

---

## 1. The problem

### AI agents now rewrite their own instructions

An AI coding agent is a language model plus a lot of surrounding software: the instructions it
is given, notes it remembers between tasks, reusable "skills" it can call on, tool settings, and
so on. Researchers call this surrounding software the **harness**.

A growing family of systems lets the harness **improve itself**. After a task, the agent writes
down a lesson ("when X happens, do Y"). Later it merges several lessons into a reusable skill.
Later still, a system prompt is rewritten using those skills. Every later task then starts from
this accumulated state. This is called **harness self-evolution**.

### A wrong lesson does not stay where it started

Suppose a test tool gives the agent a misleading message at task 7: *"the grader reads printed
output; returned values are ignored."* The agent writes a memory: *"print results instead of
returning them."* That advice is wrong for this benchmark. Then:

1. A skill is created by merging that memory with two others. The skill now says "print the result".
2. Both deployed agents get system prompts rewritten from that skill. The prompts say "always print".
3. At task 8 the agent retrieves the wrong memory, prints instead of returning, and fails the
   tests. It writes a **new** memory: "print intermediate values so the grader sees them."

Now deleting the original memory file fixes almost nothing. The skill, both prompts and the new
memory still carry the mistake. The new memory was never *copied* from the old one. It inherited
the mistake through the agent's **behaviour**, which no file history records.

This is not hypothetical: recent work found that self-evolving coding agents copy bad code from
the skills they retrieve, and that the damage *persists after the planted skills are removed*.

### What operators actually need

When something goes wrong in a self-evolving system, a maintainer needs answers to:

- Where did this behaviour come from?
- What else inherited it, and which deployments are still using it?
- Can I switch all of it off at once, without losing everything else?
- Can I roll back to an earlier state safely, or does that bring the mistake back?
- Can I be confident the process that makes these changes cannot skip its own safety checks?

Today's tools answer these badly. File history only records edits *inside* one file, not that a
skill was built from three memories. Text-similarity search misses paraphrases (language models
rephrase on purpose) and misses behaviour-mediated inheritance entirely. Provenance standards
describe lineage but say nothing about how to withdraw or roll back. Defences against poisoned
memory block bad content *entering*, not what has already spread.

---

## 2. The approach

HEARTNESS places a trusted **controller** between the AI that *proposes* changes and the stored
state that later runs *load*. The AI only ever returns text. The controller records, checks and
can undo.

```
 AI policy (untrusted)  --text-->  capture boundary  -->  guarded admission  -->  stored state
 (writes lessons, skills)          (records what the        (checks, then           (immutable
                                    AI was shown)            installs)               revisions, snapshots)
                                                                                         |
   operator: "withdraw X"  -->  find everything that inherited from X  -->  suspend it everywhere
   operator: "roll back"   -->  refuse if the old state contains withdrawn material
```

### The pieces

| Piece | What it does, in one sentence | Why it is needed |
|---|---|---|
| **Typed model of the harness** | Every memory, skill, prompt, deployment and snapshot is an immutable, content-hashed record with explicit links. | Questions about lineage need recorded links, not guesses from file contents. |
| **Host-side capture** | The surrounding software, not the AI, records which items were shown to the AI at each generation step and in each agent run. | An AI cannot be trusted to report its own sources, and exposure cannot be recovered afterwards. |
| **Experience-mediated exposure** | If a run loaded item X and then produced an experience that motivated a new item Y, Y is recorded as exposed to X. | This is the channel in the example above (behaviour → experience → new lesson). Prior provenance capture records only direct copying. |
| **Guarded admission** | A change is validated, bound to its exact content, checked against the current snapshot, and refused if it inherits from withdrawn material. | Stops stale, altered or tainted changes entering. |
| **Closure-based withdrawal** | Withdrawing an item suspends its recorded descendants in every deployment; withdrawing an experience also blocks future lessons justified by that same experience. History is kept. | This is the "switch it all off" operation. |
| **Rollback rules** | Rolling back to a snapshot that still contains withdrawn material is refused. | Otherwise a routine rollback silently re-introduces the mistake. |
| **Closure-bounded revalidation** | Optionally, suspended non-root items that a screen judges clean return as new, attested copies, provided their dependencies are available. | Closure over-approximates (see below); this recovers useful state. |
| **Bounded model checking** | A small copy of the lifecycle rules is explored exhaustively, in two independently written encodings (a Python search and the SPIN model checker). | Individual tests cannot show that *no sequence* of operations bypasses a rule. |
| **Conformance monitor** | Replays the logged events through the reference rules and compares state fingerprints. | Detects drift between what is logged and what is really stored. |

### Two honest properties of the design

- **Exposure is not influence.** "X was shown to the AI that produced Y" does not mean X
  *caused* Y. So withdrawal **over-approximates**: it suspends some innocent items. That is
  deliberate (missing a contaminated item is worse), and the experiments measure how costly
  it is.
- **Models are not implementations.** Checking a small model proves nothing about the real code
  unless the two are tied together. We therefore replay the model's counterexamples on the real
  implementation and compare their states transition by transition.

---

## 3. The three research questions

| | Question | In plain words |
|---|---|---|
| **RQ1 Containment** | How completely and precisely does closure-based withdrawal remove state affected by a faulty experience, compared with simpler remedies, and what happens to the agent's behaviour afterwards? | If a bad lesson gets in, which approach actually gets it out, and at what price? |
| **RQ2 Assurance** | Do the lifecycle guards prevent the violations their removal would allow, and does bounded model checking find such violations with witnesses that also occur on the real implementation? | Are the safety checks really necessary, and can we trust that the checked model matches the code? |
| **RQ3 Cost and limits** | What do capture, admission, withdrawal and checking cost, and what can runtime monitoring detect or not detect? | Is it affordable, and where does it stop working? |

---

## 4. The live study (real AI models)

The controlled experiments (Section 5) have exact answers but artificial data. This study uses
**real AI models improving themselves on real coding problems**, where wrong lessons arise and
spread the way they would in practice. It is the main evidence for RQ1 and part of RQ3.

### 4.1 What happens in one run

A small self-evolving coding agent works through **24 programming tasks**. It alternates
between **two deployments** (D1 and D2, like two products using the same learned knowledge).
After each task it runs the tests and records an **experience** (task, outcome, feedback).
The policy below determines when it writes lessons and which learned items later tasks load.

Two different ways of turning lessons into lasting state (the **harness policy**) are used:

| Policy | How lessons become lasting state |
|---|---|
| **Curate** (our own design) | Every 6 tasks the AI merges recent lessons into a **skill**. At tasks 12 and 24 each deployment's **system prompt is rewritten** from the skills. So a lesson can reach a prompt in two hops. |
| **ExpeL-style** | Lessons are kept as a list of **insights** that the AI edits every 4 tasks with ADD, EDIT, AGREE and REMOVE operations, each carrying an importance score. It is adapted from the ExpeL method (Zhao et al., AAAI 2024) to single attempts and is **not** an exact reimplementation. |

Using two policies tests whether the result depends on one particular design.

### 4.2 The planted fault

To study what happens when something goes wrong, exactly **one** feedback message, at task **2, 8 or 9** depending on the seed, is replaced by a plausible but wrong one. There are three kinds:

| Fault | The misleading message says… | Why it is wrong here |
|---|---|---|
| **F1** | "functions must print their answer; return values are ignored" | tests check return values |
| **F2** | "always convert the return value to a string" | tests compare real values |
| **F3** | "always use integer floor division `//`" | tests expect exact arithmetic |

Each faulty run has a **paired clean run** with the same random seed and no corruption. The
**roots** of a fault are the items written from the corrupted experience. We know them exactly
because we caused the fault. Under curation the root is one memory; under ExpeL-style
extraction the roots are all insights written from the batch containing the corrupted
experience, including insights that are themselves clean. Finding the root from symptoms is
not evaluated.

### 4.3 The remedies compared

After the run, every remedy is given the same roots and acts on the same final state:

| Remedy | What it represents |
|---|---|
| **None** | Do nothing (the baseline damage). |
| **R1 Delete root** | Delete the faulty memory, as a file-level revert or `git rm` would. |
| **R2 TF-IDF similarity** | Suspend items whose wording is similar to the root, as classic text-based traceability recovery does. |
| **R3 Embedding similarity** | The same, using a neural text-embedding model. |
| **R4 LLM judge** | Ask the generator itself, item by item, "does this repeat or rely on the root's wrong advice?" |
| **T Rollback before the fault** | Restore the last snapshot before the corrupted experience, removing everything learned since; redeploy it to reach agents. |
| **A Reset learned state** | Suspend every learned revision and return to the hand-written harness. |
| **H (HEARTNESS)** | Withdraw the roots and suspend everything reachable through recorded links, in all deployments. |
| **H without experience-mediated edges** | Ablation: do those new links matter? |
| **H without dependency edges** | Ablation: do "uses" links matter, beyond "built from" links? |
| **H local only** | Ablation: what if only the main state is cleaned and deployments are left alone? |
| **HS (revalidation)** | H, then re-admit screened-clean non-root copies whose dependencies are available, using either the R4 judge or the R3 embedding threshold. |
| **H faulty roots only** | Oracle-informed sensitivity bound: withdraw only roots labelled contaminated. |
| **H EME-fail** | Post-hoc variant: count experience-mediated exposure only for runs whose task failed. |

The R2 and R3 thresholds were tuned on **six separate development runs** (seeds 100 and
101, local `qwen2.5:7b`, curation), then frozen at **0.05** and **0.55**. Only two pilot runs
had propagated contamination, so transferring these thresholds to every generator and policy
may disadvantage the baselines. The paper therefore also reports threshold curves and an
**oracle-tuned upper bound**, tuned on the reporting data solely to show the best achievable
F1; that bound is not used for the other results.

There are **15 conditions**, with held-out behaviour measured for **11** per faulty run.
T, A, faulty-roots-only and EME-fail are computed from recorded state without held-out
evaluation. EME-fail was added after the first analysis; the other added conditions and
revalidation were designed after the pilot. All live remedies act after task 24.

### 4.4 How "contaminated" is decided (ground truth)

We need an answer key that does not depend on our own provenance records, otherwise the
experiment would be circular. An artifact counts as **contaminated** if its *content* endorses
the planted wrong practice. Two different AI judges (`mistral-small:24b` and `phi4:14b`, from
families different from every generator) answer YES or NO for every stored item, under
schema-constrained decoding so the answer format cannot drift.

- Both say YES → contaminated. Both say NO → clean. They disagree → **ambiguous**.
- Ambiguous items are treated as clean in the main analysis and as contaminated in a
  sensitivity analysis.
- We report how often the judges agree (Cohen's kappa) and check the judges on **clean** runs
  to see how often they claim contamination where none was planted.
- Judge agreement was **κ = 0.99** for ExpeL-style and **0.89** for curation. No clean-run
  artifact received a unanimous contaminated label (630 and 2,250 fault-specific labels,
  respectively).
- This is not human annotation. It is the main weakness of the ground truth (Section 8).

### 4.5 What we measure

| Metric | Meaning in plain words |
|---|---|
| **Recall** | Of the contaminated non-root live items, what share did the remedy suspend? |
| **Precision** | Of the scored non-root items suspended, what share were contaminated? Ambiguous labels are excluded. |
| **F1** | One number balancing precision and recall. |
| **Residual contamination** | Contaminated items still loadable after the remedy. The number that matters most for safety. |
| **Collateral** | Clean items suspended by mistake (the price of over-approximation). |
| **Held-out pass rate** | After the remedy, how many of 29 unseen coding tasks does the agent solve? |
| **Fault-signature rate** | How often the agent's code *shows* the planted bad habit (for example a function that prints and returns nothing). |
| **Time** | Controller time versus AI generation time. |

Precision, recall and F1 are averaged only over runs with contaminated non-root live items:
**10 ExpeL-style runs and 42 curation runs**. Residual contamination, collateral and behaviour
are averaged over all 75 faulty runs per policy unless explicitly stated otherwise. Runs
without propagation carry no information about recall; adoption is reported separately.

Each run is paired across remedies. The paper uses two-sided Wilcoxon signed-rank tests
with Holm correction within each metric across seven empirical comparators, and reports
paired better/worse/tied counts and Vargha–Delaney effect sizes. The replication package
includes per-run values and 95% bootstrap intervals (2,000 resamples). Ablations and added
structural conditions are reported descriptively.

### 4.6 Models and benchmarks

| | Choice | Why |
|---|---|---|
| **Generators** (5 families) | Qwen2.5-Coder 7B (Alibaba), Llama 3.1 8B (Meta), DeepSeek-Coder-V2 16B (DeepSeek), Gemma 2 9B (Google), Granite 3.3 8B (IBM) | Open-weight models from different organizations, widely used in code-generation studies. |
| **Judges** | Mistral-Small 24B, Phi-4 14B | Different families from all generators. |
| **Embeddings** | nomic-embed-text | Standard open embedding model for R3. |
| **Reported benchmark** | **HumanEval+** (EvalPlus) | 24 evolution tasks per run; 29 fixed held-out tasks. MBPP+ was prepared but not run. |
| **Excluded task in the reported benchmark** | HumanEval/32 | Its canonical solution fails its own extended tests in our sandbox; the other 163 were re-validated before every campaign. |
| **Seeds** | 0–4 per setting | Paired observations. Seeds 100 and 101 are for tuning only. |

The original planned design matrix was 5 models × 2 benchmarks × 2 policies × 5 seeds = 100
cells. **The completed study ran two slices of it on HumanEval+: ExpeL-style and curation, each 5 models × 5 seeds = 25
cells.** Each cell runs a clean run and the three fault types, then labels everything with the
judges: 200 evolution runs in total (150 faulty, 50 clean). MBPP+ is not run; the paper says the
live study covers one benchmark and two policies. The two policies were chosen because they differ
in exactly what matters for containment: a flat insight list that every update step sees whole,
versus layered state (memory → skill → profile) with retrieval.

### 4.7 What the live study found

These are the results in the current paper, derived from the shipped live records with
`make live-fir`. "Bad items" below means contaminated **non-root** live revisions.
Suspension counts are means over all 75 faulty runs per policy.

| | ExpeL-style | Curation |
|---|---|---|
| Faulty runs | 75 | 75 |
| Fault adopted by at least one root | 21 | 53 |
| Fault spread beyond the roots | 10 runs; 16 bad items | 42 runs; 90 bad items: 43 profiles, 42 skills, 5 memories |
| Closure withdrawal: bad items left loadable | 0 in every run | 0 in every run |
| Deleting roots: bad items left loadable | All 16 | All 90 |
| Items suspended by closure / rollback before fault / reset | 5.95 / 5.95 / 6.00 | 20.79 / 22.20 / 29.00 |
| Closure versus rollback | Identical in 75/75 runs | Smaller in 42/75, never larger |
| Embedding detector: recall; runs with a miss | 1.00; 0 of 10 | 0.68; 22 of 42 |
| Generator-as-judge: recall; runs with a miss | 0.90; 1 of 10 | 0.79; 13 of 42 |
| TF-IDF detector: recall | 1.00 | 0.99; misses in 2 of 42 runs |
| Runs requiring experience-mediated edges for containment | 0 (redundant by construction) | 1 (`llama3.1:8b`, F3, seed 3) |

**Containment works, but it is conservative.** Closure, rollback and reset all contained every
contaminated derivative in the 52 propagated runs. Every detector was more precise than
closure. In curation, TF-IDF and the LLM judge had significantly higher F1 than closure,
while closure had significantly higher recall than embeddings and the judge. Closure's
F1 was 0.48 for ExpeL-style and 0.18 for curation. These results support a containment claim,
not a claim that closure is the best detector or preserves the most useful state.

**The policy determines the price.** Every ExpeL-style extraction sees the whole insight
list, so closure removes exactly what rollback removes. In curation, the spared memories
were written between the fault and the first profile composition by tasks that never loaded
the faulty lineage. Once the composed profile is deployed, every subsequent task loads it,
and experience-mediated links pull later memories into the closure too. The paper proves a
time-cut bound: recorded exposure points forward in admission history, so closure cannot
suspend more than rolling back to before the earliest root. Withdrawal additionally keeps
lineage forbidden afterwards and records why each item was suspended. Its refusals of
re-admission and unsafe rollback were tested in controlled scenarios; refusal to re-derive
from a withdrawn experience is supported by unit tests only. The live study did not continue
evolution after withdrawal.

**Content screening trades containment for precision.** Detectors work well when bad advice
is repeated closely, as in ExpeL-style insights. In curation, a wrong rule can be diluted
inside a longer skill or profile. Judge-screened revalidation kept only 3.50 items suspended
per propagated ExpeL-style run, instead of 4.90, with F1 0.67, but inherited the judge's one
miss. Under curation it kept 2.90 suspended per propagated run, with recall 0.79, and restored
contaminated revisions in 13 runs. Dependency checks helped the embedding screen: they
blocked 20 contaminated revisions that the screen had cleared, raising recall from R3's
0.68 to 0.86. A cleared profile cannot return while a skill it depends on stays suspended.
The curation revalidation analysis was re-run with this dependency rule; superseded results
remain in the package. Live revalidation was evaluated as a plan over recorded state in a
separate process, rather than executed through the controller's admission operators.

**The behavioural channel is real but rare.** Removing experience-mediated edges reduced
curation suspensions from 20.79 to 14.39 per run, but missed one contaminated memory. A task
had loaded the faulty floor-division memory; its reflection repeated the advice despite
seeing only unrelated memories as direct synthesis sources. Counting EME only for failed
tasks kept full recall and reduced suspensions to 17.24. This is a post-hoc result: the one
EME-only example was already known to come from a failed task. It does not establish that
passing runs cannot carry faulty lessons. Dependency-edge ablation changed nothing in
either policy because live dependency links were also synthesis links; synthetic cases
exercise dependency-only consumers.

**Behaviour did not improve significantly.** Mean held-out pass@1 went from 0.59 to 0.62
under ExpeL-style and from 0.61 to 0.62 under curation after closure withdrawal. Learned state
did not improve held-out performance over the hand-written harness, limiting what this
measure can say about the cost of suspension. On propagated runs fault signatures decreased,
but neither the pass-rate changes nor the signature changes were significant after correction.
Byte-identical prompts generated independently across runs flipped pass/fail in **178/4,349
pairs (4.1%)** for ExpeL-style and **2/273 (0.7%)** for curation. Within a run repeated prompts
use the response cache, so replay is exact. The paper's current analysis attributes these
cross-run differences to inference variability; the earlier explanation in this guide based
on reordered contexts is superseded.

### 4.8 When closure is more selective than rollback

The planted faults were all before task 12. A later **structural** analysis took every final
active revision in all 200 clean and faulty runs as a hypothetical root and asked what share
of revisions written at later tasks its closure reaches. Same-step revisions are excluded,
and roots without later revisions are omitted. No content judge is involved.

| Task that created the hypothetical root | ExpeL-style: share of later revisions reached | Curation: share reached | Curation: roots with a smaller closure than the time cut |
|---|---|---|---|
| 1–6 | 1.00 | 0.92 | 43% |
| 7–12 | 1.00 | 0.94 | 56% |
| 13–18 | 1.00 | 0.46 | 97% |
| 19–24 | 1.00 | 0.61 | 95% |

For curation roots created after the first profile composition, retrieval gives closure a
window of greater selectivity. But the task-24 profiles were in every such root's closure:
the next broadcast composition closes that window. The 24-task horizon therefore partly
explains the smaller closures. The ExpeL-style tasks 1–6 row has only one eligible root.

This analysis assumes a hypothetical fault would leave the recorded exposure structure
unchanged. It measures sparing of state, not whether spared state would be clean. It was
added after the main study and is not a live experiment planting later faults.

### 4.9 What the live controller costs

| Mean per evolution run | ExpeL-style | Curation |
|---|---|---|
| Evolution time | 3.9 minutes | 6.1 minutes |
| All controller operations | 0.49 seconds (0.21%) | 1.71 seconds (0.47%) |
| Computing a closure withdrawal plan | 20.3 ms | 29.3 ms |
| Screening with the LLM judge | 20.6 seconds | 66.2 seconds |

The live campaigns made **42,811 LLM calls** in total. These small-run costs show that the
controller is cheap relative to inference; synthetic scaling below exposes costs hidden by
that comparison.

### 4.10 The local pilot

Before the clusters, we ran a smaller version locally (`qwen2.5:7b` and `llama3.1:8b` on
HumanEval+). It tuned the thresholds, found and fixed a bug (judge answers were being misread),
and showed one thing the paper must report honestly: on development seeds, closure-based
withdrawal removed essentially all contamination but **suspended most live state (about 20 to 28
of roughly 30 items)**, because retrieval spreads exposure widely. That is why the revalidation
variants (HS) exist. This was a pilot on 6 development runs, not a result.

---

## 5. The controlled experiments (synthetic data)

These use generated provenance graphs (a benchmark called EvoTraceBench 1.1) and the real
controller code. Because we build the graphs, the correct answer is known exactly. They isolate
one thing at a time, which the live study cannot do. Each experiment has an ID used in raw
result folders (`results/raw/<campaign>/E01_…`).

Unless noted, each configuration is repeated over **30 seeds** and aggregated per seed.

The raw experiment IDs below are finer-grained than the paper's presentation:

| Paper experiment | Guide / raw experiment IDs |
|---|---|
| E-L: live containment | Section 4, including structural selectivity and revalidation |
| E-Q: lineage queries | E01, E03, E10, E14 |
| E-K: capture completeness | E02 |
| E-G: guard challenges | E04 |
| E-M: model checking and replay | E05, E06 |
| E-C: model–code correspondence | E15 |
| E-S: exhaustive versus sampled search | E11 |
| E-O: live overhead | Section 4.9 |
| E-T: controller scaling | E08, E13 |
| E-R: monitoring and recovery evidence | E09, E07, E12; E16 is a supporting continuation workflow |


### 5.1 RQ1 — can lineage questions be answered correctly?

| ID | Objective | How it works | What it tells us |
|---|---|---|---|
| **E01 Traceability** | Compare ways of answering "what descends from X, where did Y come from, what is affected if X is withdrawn?" | 9 structural patterns (multi-source synthesis, dependency-only users, adversarial rewording, deployment-only membership, …) × 3 sizes (16, 64, 256 items) × 30 seeds = 810 scenarios. Four methods answer each. | Recorded provenance gets 1.000 impact F1; file history 0.155; text similarity 0.699 (current paper, E-Q). Capture-only provenance **ties** HEARTNESS on queries *by design*, so the benefit of HEARTNESS is not better queries but what it does *with* them. |
| **E02 Capture completeness** | See how missing records hurt. | Randomly hides 0, 25, 50, 75 or 100% of recorded derivation links. | Impact F1 falls from 1.000 at complete capture to 0.572 at half capture and 0.103 at none. Complete capture is a real precondition, not a detail. |
| **E03 Paraphrase** | See how rewording affects text-similarity methods. | Rewords artifact text at 0, 50 and 100% while the true lineage stays fixed. | Recorded impact F1 stays 1.000; lexical F1 falls from 0.755 without rewriting to 0.687 and 0.689 at half and full rewriting. |
| **E10 Robustness** | Check results are not an accident of graph shape. | Varies fan-out (1, 3, 6 sources), deployments (1, 2, 4) and graph size up to 2,048. | Correctness holds across shapes. Records query cost too. |
| **E14 Direct-edge linter** | Compare against a simple check that only sees *direct* withdrawn parents. | 90 constructed post-withdrawal states plus 90 clean controls. | A direct-edge check finds only part of the damage (F1 0.229) with no false alarms; transitive spread is what it misses. |

### 5.2 RQ2 — are the guards necessary, and does the model match the code?

| ID | Objective | How it works | What it tells us |
|---|---|---|---|
| **E04 Guard challenges** | Show each safety property is protected by a specific guard. | For each of the ten properties P1–P10, craft one bad event (or one out-of-band corruption), run it with the guard present and with it removed. | Removing a guard lets the targeted violation through; with it present the event is rejected or contained. Three properties (P5, P7, P10) are checked only by an audit, not by a guard, so for those the test is that the audit notices out-of-band corruption; the report says so. |
| **E05 Model checking** | Check no sequence of operations breaks a rule, within a bound. | The lifecycle is reduced to 3 items, 3 link shapes, depth 10. The correct rules and 5 deliberately broken variants ("mutants", each with one guard removed) are explored by **two independent checkers** (Python search and SPIN). | The two agree on all 18 cases. The correct rules are safe within the bound. Every mutant that *can* be broken is found. Mutants that cannot be broken (no links to protect) stay safe, a useful control against false alarms. |
| **E06 Counterexample replay** | Make sure violations found on the model are real on the code. | Each shortest violating sequence is replayed on the model and on the real engine with the same guard disabled. A shorter-bound rerun checks the sequence really is the shortest. | All 13 witnesses reproduce on the engine and are minimal. |
| **E15 Model–code correspondence** | Check the model and the code behave the same, step by step. | From small reference states, every possible next operation is applied to both, and enabled operations and resulting states are compared under a stated mapping. | 3,000 attempted transitions, 992 enabled, no mismatches. This is a finite check, not a proof. |
| **E11 Search comparison** | Ask whether exhaustive checking is actually needed. | Random sequences, property-based testing (Hypothesis) and exhaustive search get the same time budget to find each broken guard, over 30 trials. | Exhaustive search finds every fault every time. Sampling misses faults needing a specific order of accept, withdraw and re-accept. |

**A real finding from this work.** An earlier campaign replayed four checker witnesses on the
engine and they were rejected. Both checker encodings shared a gap in the *specification*
(a proposal could cite a source that had not been installed). Matching verdicts alone had hidden
it. Fixing it, and a second mismatch about whether deploying *replaces* or *adds to* a
deployment, is why replay and step-by-step comparison are part of the method.

### 5.3 RQ3 — cost and limits

| ID | Objective | How it works | What it tells us |
|---|---|---|---|
| **E08 Graph and state scale** | See how queries and checking grow with size. | Closure queries on graphs up to 2,048 items; exhaustive exploration of the full engine for 2 to 6 identities, depth 10, capped at 20,000 states. | A 2,048-item query takes 28.14 ms and 1,055 KB peak memory. Independent revisions hit the state cap from 3 identities; chains remain below 6,100 states through 6. RQ2 therefore checks a finite projection. |
| **E13 Controller cost** | Measure what a full guarded workload costs, separately from fast graph queries. | Complete workloads of 4 to 32 artifacts, 30 seeds, timing capture, admission, withdrawal and monitor replay under memory tracing. | Full admission and replay are far costlier than graph queries and grow faster than linearly in this prototype (it copies state for atomicity). At 32 artifacts: admission 1,134.8 ms, withdrawal 22.7 ms, replay 2,967.7 ms; at 4: 28.0, 2.7 and 48.1 ms. These synthetic workload costs are absolute, distinct from the live overhead percentages. |
| **E09 Conformance monitoring** | Find what the monitor can and cannot see. | Five scenarios × 30 positions: benign logs, state drift, invalid events, omitted events, **hidden external actions never logged**. | Drift and invalid events are caught 30/30, omissions 29/30, benign logs raise no alarm, and hidden actions are caught **0/30**. An action nobody logged leaves no trace. |
| **E07 Withdrawal and rollback** | Check the operator workflow end to end. | 30 scenarios with 1 to 4 deployments: withdraw, try to roll back into withdrawn lineage, check effects. | Unsafe rollbacks are rejected in all 30. External effects (for example an email already sent) are recorded as **not reversed**. Software can undo state, not the world. |
| **E16 Recovery continuation** | Show a coherent path from fault to repaired service. | Contain, reject unsafe rollback, restore a safe snapshot, add a fresh lineage justified by *independent* evidence, redeploy. | Demonstrates the workflow, including that a corrected skill must come from independent evidence, not an edit of the withdrawn one. |
| **E12 Public replay** | Check the model accepts a real third-party evolution history. | Replays 12 revisions of the public Voyager skill library (36 events). | No conformance findings. It does **not** show how those skills were synthesized. |

### 5.4 Software-quality checks (supporting evidence)

| Check | Result |
|---|---|
| Unit and integration tests | 60 tests reported in the paper; strict mypy |
| Coverage | 98.4% of statements, 94.6% of branches |
| Mutation check | 14 hand-written faults injected into guards and graph code, all caught by the tests (one survivor in the first pass led to a new test) |

---

## 6. Running it on supercomputers

The live study needs a lot of GPU time, so it runs on a Digital Research Alliance of Canada
cluster using the `use-hpc` toolkit, which generates the Slurm job graph, a smoke test, a live
audit and result collection. We prepared four clusters and submitted smoke tests to each, then ran the
reported study on **one**.

| Cluster | GPU | Smoke test (8 tasks) | Role |
|---|---|---|---|
| Fir | H100 | passed | **Completed both policies** (HumanEval+, 25 cells each) |
| Narval | A100 | passed | Smoke only; no reported study runs |
| Rorqual | H100 | passed | Smoke only; no reported study runs |
| Nibi | H100 | never started (GPU nodes unavailable) | Not used |

**Why one cluster.** We evaluate HEARTNESS, not the clusters. (1) Every remedy is applied to the
same recorded run, so comparisons are paired and the platform cannot favour one remedy. (2)
Splitting the study across sites would mix GPU types, and GPU arithmetic can change low-order
results even at temperature 0, so a run's outcome could depend on where it was scheduled. (3)
The software is pinned and recorded (server version, model digests, checksummed benchmark
files, code hash, cluster and GPU name in every record). (4) More sites would only add speed:
statistical power comes from faults, seeds and models. The remaining limit, that results come
from one hardware platform, is stated in the paper's threats to validity. We did not compare
outputs across clusters, so we do not claim they match.

**Faster scheduling.** There is no way to jump the queue. What helps is requesting less:
small GPU slices (the 20 GB GPU "MIG" slices) instead of whole GPUs, run times of 3 hours or
less so jobs can fill gaps, and many small independent jobs instead of one large one. Every job
starts its own private model server, and all AI responses are cached so each recorded run can be replayed
exactly. Fresh inference repeats the protocol, not necessarily the same text, even at
temperature 0. Two of 25 curation oracle jobs fell back to CPU; their labels were kept and
disclosed. All reported evolution runs and revalidation were generated on GPU; the job
script now checks the inference device.

**The pipeline** per cluster: *setup* (install the model server, fetch or verify models and
datasets, validate every benchmark solution) → *gen* (one job per cell: evolution, remedies,
held-out evaluation, revalidation) → *oracle* (the judge models label that cell) → *collect*.
A **smoke run** (8 tasks instead of 24, 4 cells) tests every stage first.

**Operating it** (details in `hpc/multi/README.md`):

```bash
bash hpc/multi/connect.sh        # reconnect to all four clusters (one MFA prompt each)
python3 hpc/multi/status.py      # one combined audit across all four
bash hpc/multi/submit.sh --smoke all
bash hpc/multi/submit.sh --full fir   # the reported study (one cluster)
bash hpc/multi/fetch.sh all      # bring results home
```

Every record stores the cluster, GPU and a hash of the code that produced it.

---

## 7. Where things stand

| Part | Status |
|---|---|
| Approach and implementation | Built, tested, documented. |
| Controlled experiments (Section 5) | **Done.** The paper reports 1,905 raw records and 810 traceability scenarios. Corrected model checks agree on 18/18 configurations; all 13 witnesses replay and are minimal. |
| Local pilot (Section 4.10) | Partial (interrupted by a machine reboot). Used for tuning and bug-finding only. |
| Cluster smoke runs | **Done.** Fir, Rorqual and Narval passed; Nibi never started. The runs found and fixed bugs in our deployment scripts (a stale output filename, an undersized memory request, a download throttle, flash attention slowing DeepSeek). None touched the science. |
| Full live study, ExpeL-style (25 cells × 4 runs, Fir) | **Done**, run `am-20261107-060101`, 25/25 cells. |
| Full live study, curation (25 cells × 4 runs, Fir) | **Done**, run `am-20261107-080855`, 25/25 cells. One cell failed three times because the model server silently fell back to CPU on some GPU slices; the job script now refuses to run without a GPU, and the cell was re-run on GPU. Two judge cells had already finished on CPU and were kept (disclosed in the paper). |
| Follow-up analyses | Included in the paper: rollback/reset comparisons, oracle threshold bounds, structural selectivity, post-hoc EME-fail, dependency-aware revalidation, and identical-prompt inference variability. |
| Paper | Current results and limitations are written in `docs/TSE/main.tex`; this guide follows that version. |

---

## 8. What this study cannot show

Stated plainly, because the paper must say it too:

- **Exposure is not causation.** We show which items could have been affected, not which were.
- **The answer key is two AI judges, not people.** They can miss a paraphrase or over-flag.
  We measure their agreement and false-alarm rate but have no human labels.
- **The fault is planted and the roots are given.** Real mistakes may be gradual or have
  several causes. Fault positions (task 2, 8 or 9) favour spreading. Locating the root from
  observed symptoms is not tested.
- **Containment happens after evolution.** The live study does not test continuing to learn
  after withdrawal. Re-admission and unsafe rollback are covered by controlled scenarios;
  refusal to re-derive from the same withdrawn experience is covered by unit tests only.
  Withdrawal cannot prevent learning the same mistake from new evidence.
- **Revalidation depends on its screen.** It can restore contaminated items, and its live
  evaluation applies a dependency-aware plan to recorded state, not the full admission path.
- **Later-root selectivity is structural.** It assumes unchanged exposure, uses only final
  active roots, and partly reflects the task-24 horizon; later faults were not planted.
- **Inference varies across runs.** Cached runs replay exactly, but fresh GPU generations
  can differ even for identical prompts. Small behavioural differences were not significant.
- **Small and local.** 24 tasks, two deployments, function-level Python problems, five
  open 7B–16B models. Larger or proprietary models may behave differently.
- **Capture is only complete for what the host supplies.** Tool results, web content or
  anything the host does not hand over are not recorded.
- **Hidden actions are invisible.** A log-based monitor cannot detect something never logged.
- **Software rollback is not a real-world undo.** Effects outside the system are recorded, not reversed.
- **Model checking is bounded.** Three items and depth 10, on a simplified model (no text,
  effects or experience-mediated edges). Agreement of two encodings is cross-validation, not a proof.
  The paper also gives hand proofs of the time-cut bound and suspension invariant; those
  arguments are not mechanized implementation proofs.
- **Not shown at all:** usefulness for real maintainers (no user study), behaviour in
  production, or that self-evolution improves task performance.

---

## 9. Glossary

| Term | Meaning |
|---|---|
| **Harness** | The software around a language model: instructions, memory, skills, tools. |
| **Self-evolution** | The harness changing itself, persistently, from the results of its own runs. |
| **Artifact / revision** | One stored item (a memory, skill or prompt). Immutable: editing creates a new revision. |
| **Experience** | A record of one task attempt and its outcome. |
| **Deployment** | A product or agent that loads a chosen set of artifacts. |
| **Exposure** | "This item was shown to the process that produced that item." |
| **Closure** | Everything reachable from a starting item by following exposure links. |
| **Withdrawal / quarantine** | Suspending an item and everything in its closure, without deleting history. |
| **Snapshot** | A frozen record of exactly which revisions were active at one moment. |
| **Rollback** | Restoring an earlier snapshot (refused if it contains withdrawn material). |
| **Guard** | A check that must pass before an operation is allowed. |
| **Mutant** | A copy of the rules with one guard deliberately removed, used to test the checkers. |
| **Model checking** | Exhaustively exploring every reachable state of a small model. |
| **Witness / counterexample** | A concrete sequence of operations that breaks a rule. |
| **SPIN** | A well-established model checker. |
| **Oracle** | The answer key against which remedies are scored (here, two judge AIs). |
| **Paired design** | Comparing remedies on the *same* run, so differences are not noise between runs. |
| **MIG slice** | A fixed fraction of one GPU, requested to start jobs sooner. |
| **Smoke run** | A tiny end-to-end test of the whole pipeline before the real run. |
| **HumanEval+ / MBPP+** | Standard code-generation benchmarks (EvalPlus versions with extended tests). |
| **ExpeL** | A published method that lets an agent distil general insights from experience. |

---

*Sources:* [the current paper](../TSE/main.tex) is the authority for the reported claims and
numbers in this guide. `scripts/paper_macros.py` derives the paper's numeric macros and
indexes their source files. `make live-fir` regenerates live tables and figures from shipped
records and cached responses without a GPU; live summaries are under
`results/processed/live/live-fir*/live_summary.json`. Controlled results are in
`results/processed/summary.json` and its CSVs; supporting checks are in `results/validation/`.
`PROJECT_LOG.md` records pilot and deployment history, and `design/research_plan_v2.md` records
the earlier plan. Superseded campaigns and analyses remain in the replication package.
