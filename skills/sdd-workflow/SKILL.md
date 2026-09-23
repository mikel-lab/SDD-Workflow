---
name: sdd-workflow
description: Use when a software change should follow a governed Specification-Driven Development cycle from a Jira task or detailed feature request, including repository-grounded planning, implementation routing, or independent verification.
---

# SDD Workflow

## Authority

Treat `sdd-workflow` as the methodological authority for the entire governed SDD cycle. SpecKit owns the official planning artifacts; compatible implementation and verification skills supply practices without creating a second planning workflow.

Before acting, every role must read this file completely and then every reference linked in its quick-reference row. Treat each listed reference and each required SpecKit skill as a mandatory dependency. If any mandatory dependency is missing, unreadable, or incompatible, fail closed: stop before writing, report the blocker through the applicable contract, and do not advance a gate.

## Root Chat Authority

The invoking root chat is the sole coordination and user-contact authority for a cycle. It performs the Orchestrator role: it owns lifecycle transitions, gate decisions, user questions, Planner, implementer, and Reviewer delegation. The root chat must not dispatch `sdd-orchestrator`; a configured `sdd-orchestrator` is not a second coordinator for a root-chat cycle.

Before reading a governed artifact, the root chat establishes a cycle identity and exact artifact directory under [Sources and Artifacts](references/sources-and-artifacts.md). It requires the cycle validator at planning completion, before planning review, when freezing the baseline, before implementation, and at final reconciliation. A failed or missing validation blocks the affected transition.

## Universal Rules

1. Keep application source, tests, resources, configuration, and non-SDD documentation read-only until the planning package has an independent `approved` review, the cycle validator passes, and the root chat freezes the exact artifact baseline. Then implementation proceeds without a separate user approval.
2. Before that gate, permit writes only to the dynamically resolved SDD artifact set and the exact `.specify/feature.json` bootstrap write performed by official `speckit-specify`. Follow [Sources and Artifacts](references/sources-and-artifacts.md) for source authority, ambiguity, root resolution, and the write boundary; no other `.specify/` path is exempt.
3. Follow [Lifecycle and Gates](references/lifecycle-and-gates.md) for every transition. A `conditionally verified` result never opens the implementation gate; resolve the missing check or stop as blocked.
4. Use the ordered recipes in [Contracts](references/contracts.md) for every handoff and result. Preserve exact paths, commands, evidence, blockers, and residual risks.
5. Keep the root chat in the Orchestrator role as coordination and gate authority, the Planner as planning owner, implementers as bounded execution owners, and the Reviewer as an independent read-only verifier.

## Agent Profiles

Keep the configured role profiles aligned with these settings:

| Role | Agent profile | Model | Reasoning effort |
| --- | --- | --- | --- |
| Planner | sdd-planner | GPT-6 Sol (gpt-6-sol) | high |
| Reviewer | sdd-reviewer | GPT-6 Sol (gpt-6-sol) | high |
| Main implementer | sdd-implementer-main | GPT-6 Luna (gpt-6-luna) | medium |
| High implementer | sdd-implementer-high | GPT-6 Luna (gpt-6-luna) | high |
| Simple implementer | sdd-implementer-simple | GPT-6 Luna (gpt-6-luna) | low |
| Explicitly requested visible Luna task | separate user-visible task | GPT-6 Luna (gpt-6-luna) | max |

Native Simple is the default route for eligible low-complexity isolated work. A visible Luna task requires a concrete benefit over native Simple and is used only when the current user request explicitly selects it.

## Core Sequence

1. Validate intake and source access, then establish the isolated cycle identity and artifact directory before any governed artifact read.
2. Delegate Planner creation of the cycle manifest and `speckit-specify` with its exact assigned directory; validate the manifest and active-feature output before artifact reads.
3. Plan with `speckit-clarify` when materially blocked, `speckit-checklist`, `speckit-plan`, and `speckit-tasks`, then run the cycle validator at planning completion.
4. Run `speckit-analyze` read-only; apply any artifact correction as a separate Planner action, revalidate the cycle, and obtain the planning review. A bounded correction receives the same Reviewer's focused delta re-review; material changes to scope, architecture, acceptance criteria, source set, or artifact identity require a fresh full planning review.
5. After an independent `approved` planning review, revalidate and freeze the artifact baseline, then proceed directly to implementation without asking the user to approve the plan.
6. Revalidate before routing coherent dependency-ready implementation batches. Normal batches use implementer verification until final review; request an intermediate review only for the defined risk triggers or Luna pre- and post-integration gates.
7. The final Reviewer runs read-only `speckit-analyze` and returns the integrated verdict in the same action. When approved-scope work is absent from `tasks.md`, the Planner repairs task coverage under the `speckit-tasks` contract. Use `speckit-converge` only when evidence proves `speckit-implement` executed the current task list, or a future converge contract explicitly supports the executor used. Any task change returns through planning review; after a fresh independent `approved` result and successful validation, implementation resumes automatically.
8. Complete only after that final independent verdict is `approved`.

## Quick Reference

| Role | Required references before acting |
| --- | --- |
| Root chat (Orchestrator role) | [Lifecycle and Gates](references/lifecycle-and-gates.md), [Sources and Artifacts](references/sources-and-artifacts.md), [Contracts](references/contracts.md), [Orchestrator](references/orchestrator.md), [Implementers](references/implementers.md), [Reviewer](references/reviewer.md), and [Luna Lane](references/luna-lane.md) when evaluating or coordinating Luna |
| Planner | [Lifecycle and Gates](references/lifecycle-and-gates.md), [Sources and Artifacts](references/sources-and-artifacts.md), [Contracts](references/contracts.md), and [Planner](references/planner.md) |
| Main / High / Simple | [Lifecycle and Gates](references/lifecycle-and-gates.md), [Contracts](references/contracts.md), and [Implementers](references/implementers.md) |
| Reviewer | [Lifecycle and Gates](references/lifecycle-and-gates.md), [Sources and Artifacts](references/sources-and-artifacts.md), [Contracts](references/contracts.md), and [Reviewer](references/reviewer.md) |

Follow [Luna Lane](references/luna-lane.md) for every Luna authorization, isolated delivery, review, and integration decision.
