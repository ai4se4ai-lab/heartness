# Problem and evidence requirements

A self-evolving harness uses execution feedback to propose persistent revisions
that later runs load. Its update targets include memory, skills, instructions,
workflows, agent/tool configuration and executable components. A successful
transition is not necessarily a task improvement (source survey §§2,6).

An incorrect experience e1 motivates memory m1. Skill s1 summarizes m1 and another
source. Agents a1 and a2 consume s1 in deployments d1 and d2. Editing or deleting
m1's file does not erase s1's inherited lesson. A deployment rollback does not
recall an external message already sent. File history records revisions inside
files; it does not necessarily record synthesis between files. Exposure to a
source is also insufficient evidence of its behavioral contribution.

## Research problem

Given an append-only event history, immutable revisions, recorded derivation and
dependency edges, and deployment snapshots, support six tasks:

1. Explain artifact origins by experiences or authorized seeds.
2. Compute derivative and active-consumer closure across deployments.
3. Withdraw a source and suspend the affected closure without deleting history.
4. Admit only validated, contract-consistent snapshots against a current base.
5. Select a compatible earlier snapshot and retain external-effect obligations.
6. Check finite transition sequences and compare observed execution with the model.

The proposed model cannot recover absent edges, prove source causality, prove
natural-language contracts, observe uninstrumented runtime changes, or reverse
external effects. Connected clients and serialized admission are assumptions.

## Positioning and falsifiable expectations

Graph reachability with complete edges is an established algorithm, not the
novel contribution. The contribution under investigation is its integration with
admission, cross-deployment containment and observed-state conformance. Capture-only
must tie the full system on provenance query accuracy. If it does not, inspect the
baseline. Model checking adds prospective sequence exploration, not more accurate
reachability. Comparing an unsafe transition system with guarded admission must be
reported as guard validation, not an empirical claim of general superiority.
