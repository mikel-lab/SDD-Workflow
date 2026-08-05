---
name: sdd-workflow
description: Use when a software change should follow a governed Specification-Driven Development cycle from a Jira task or detailed feature request, including repository-grounded planning, implementation routing, or independent verification.
---

# SDD Workflow

## Authority

Treat `sdd-workflow` as the methodological authority for the entire governed SDD cycle. SpecKit owns the official planning artifacts; compatible implementation and verification skills supply practices without creating a second planning workflow.

Before acting, every role must read this file completely and then every reference linked in its quick-reference row. Treat each listed reference and each required SpecKit skill as a mandatory dependency. If any mandatory dependency is missing, unreadable, or incompatible, fail closed: stop before writing, report the blocker through the applicable contract, and do not advance a gate.

## Universal Rules

1. Keep application source, tests, resources, configuration, and non-SDD documentation read-only until the planning package has an independent `approved` review and the user then sends the exact string `Approved, implement.`.
2. Before that gate, permit writes only to the dynamically resolved SDD artifact set and the exact `.specify/feature.json` bootstrap write performed by official `speckit-specify`. Follow [Sources and Artifacts](references/sources-and-artifacts.md) for source authority, ambiguity, root resolution, and the write boundary; no other `.specify/` path is exempt.
3. Follow [Lifecycle and Gates](references/lifecycle-and-gates.md) for every transition. A deadline, near-match approval, or `conditionally verified` result does not open an approval gate.
4. Use the ordered recipes in [Contracts](references/contracts.md) for every handoff and result. Preserve exact paths, commands, evidence, blockers, and residual risks.
5. Keep the Orchestrator as coordination and gate authority, the Planner as planning owner, implementers as bounded execution owners, and the Reviewer as an independent read-only verifier.

## Core Sequence

1. Validate intake and source access.
2. Plan with `speckit-specify`, `speckit-clarify` when materially blocked, `speckit-checklist`, `speckit-plan`, and `speckit-tasks`.
3. Run `speckit-analyze` read-only; apply any artifact correction as a separate Planner action.
4. Obtain an independent planning review, freeze the approved artifact set, and wait for the exact implementation approval.
5. Route dependency-ready implementation batches and review each delivery.
6. Reconcile every implementation with read-only `speckit-analyze`. When approved-scope work is absent from `tasks.md`, the Planner repairs task coverage under the `speckit-tasks` contract. Use `speckit-converge` only when evidence proves `speckit-implement` executed the current task list, or a future converge contract explicitly supports the executor used. Any task change returns through planning review and a new approval gate.
7. Complete only after final independent review.

## Quick Reference

| Role | Required references before acting |
| --- | --- |
| Orchestrator | [Lifecycle and Gates](references/lifecycle-and-gates.md), [Sources and Artifacts](references/sources-and-artifacts.md), [Contracts](references/contracts.md), [Orchestrator](references/orchestrator.md), [Implementers](references/implementers.md), [Reviewer](references/reviewer.md), and [Luna Lane](references/luna-lane.md) when evaluating or coordinating Luna |
| Planner | [Lifecycle and Gates](references/lifecycle-and-gates.md), [Sources and Artifacts](references/sources-and-artifacts.md), [Contracts](references/contracts.md), and [Planner](references/planner.md) |
| Main / High / Simple | [Lifecycle and Gates](references/lifecycle-and-gates.md), [Contracts](references/contracts.md), and [Implementers](references/implementers.md) |
| Reviewer | [Lifecycle and Gates](references/lifecycle-and-gates.md), [Sources and Artifacts](references/sources-and-artifacts.md), [Contracts](references/contracts.md), and [Reviewer](references/reviewer.md) |

Follow [Luna Lane](references/luna-lane.md) for every Luna authorization, isolated delivery, review, and integration decision.
