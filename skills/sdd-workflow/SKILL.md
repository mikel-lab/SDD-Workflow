---
name: sdd-workflow
description: Use when a software change needs a governed Specification-Driven Development cycle, when preparing a PR containing SDD work, or when explicitly setting up remote SDD storage or migrating local artifacts, including tracked files.
---

# SDD Workflow

## Authority

Treat `sdd-workflow` as the methodological authority for the entire governed SDD cycle. SpecKit owns the official planning artifacts; compatible implementation and verification skills supply practices without creating a second planning workflow or user-approval gate.

Before acting, every role must read this file completely and then every reference linked in its quick-reference row. Treat each listed reference and each required SpecKit skill as a mandatory dependency. If a dependency is missing, unreadable, or incompatible, stop the affected action before writing and report it through the applicable contract. The root chat attempts authorized recovery before applying the User Attention rule in [Lifecycle and Gates](references/lifecycle-and-gates.md).

## Root Chat Authority

The invoking root chat is the sole coordination and user-contact authority for a cycle. It performs the Orchestrator role: it owns lifecycle transitions, gate decisions, unavoidable user questions, Planner, implementer, and Reviewer delegation. The root chat must not dispatch `sdd-orchestrator` or create a competing coordinator.

Select GPT-6 Sol (`gpt-6-sol`) with `medium` reasoning effort for the root chat when supported. This is a session recommendation, not a claim that a skill or agent TOML changes the active root model. Record unavailable runtime metadata as `not verified`.

Before reading a governed artifact, the root chat establishes a cycle identity and exact artifact directory under [Sources and Artifacts](references/sources-and-artifacts.md). It requires the cycle validator at planning completion, before planning review, when freezing the baseline, before implementation, and at final reconciliation. A failed or missing validation blocks the affected transition, not automatically the user's attention.

## Universal Rules

1. The task request authorizes the complete in-scope cycle unless the user explicitly limits it, pauses it, or cancels it. Planning, implementation, verification, corrections, and internal routing proceed without another confirmation. Ask the user only for an unavoidable blocker that requires their decision, access, or authority, before the affected action.
2. Keep application source, tests, resources, configuration, and non-SDD documentation read-only until the planning package has an independent `approved` review, the cycle validator passes, and the root chat freezes the exact artifact baseline. Then implementation proceeds without a separate user approval.
3. Before that gate, permit writes only to the dynamically resolved SDD artifact set and the exact `.specify/feature.json` bootstrap write performed by official `speckit-specify`. Follow [Sources and Artifacts](references/sources-and-artifacts.md) for source authority, ambiguity, root resolution, and the write boundary; no other `.specify/` path is exempt.
4. Follow [Lifecycle and Gates](references/lifecycle-and-gates.md) for every transition. A `conditionally verified` result never opens the implementation gate; resolve its missing check through the accountable role or report an evidenced blocker.
5. Use the ordered recipes in [Contracts](references/contracts.md) for every handoff and result. Preserve exact paths, commands, evidence, blockers, and residual risks. Keep the operational checkpoint separate from the frozen planning artifacts.
6. Keep the root chat as coordination and gate authority, the Planner as planning owner, implementers as bounded execution owners, and the Reviewer as an independent read-only verifier. Only the root chat dispatches agents.

## Remote Memory (Conditional)

The project may declare an authorized documentation repository in `<workspace_root>/.sdd/config.json`. Reading this small config does not load history. Do not read the remote index at intake or consult old packages by default.

Read [Remote Memory](references/remote-memory.md) only for configured archival at task closure, a concrete historical question, explicit storage setup/import or tracked-artifact migration, or authorized preparation of a PR containing SDD work. Setup/import and reference-only PR preparation are bounded administrative operations: follow that reference without invoking SpecKit or opening a development cycle. Tracked-artifact migration requires its own explicit request; routine cleanup still preserves tracked files. The normal role table and gates continue to govern software changes.

The running agent stores documents and maintains the remote index through its authenticated GitHub tools in the same session. When already authorized to prepare a PR, include the verified package references or an honest pending status; do not create a PR or add automation or merge gates for documentation. Administrative catalog/receipt reads to recover exact PR links do not authorize loading old task contents. The only historical-read exception is the bounded, recorded, read-only lookup defined by that reference; it never selects or reactivates the current cycle.

## Agent Profiles

Keep the configured role profiles aligned with these settings:

| Role | Agent profile | Model | Reasoning effort |
| --- | --- | --- | --- |
| Root chat / Orchestrator | invoking session, not an agent file | GPT-6 Sol (gpt-6-sol) | medium |
| Planner | sdd-planner | GPT-6 Sol (gpt-6-sol) | high |
| Reviewer | sdd-reviewer | GPT-6 Sol (gpt-6-sol) | high |
| Main implementer | sdd-implementer-main | GPT-6 Sol (gpt-6-sol) | medium |
| High implementer | sdd-implementer-high | GPT-6 Sol (gpt-6-sol) | high |
| Simple implementer | sdd-implementer-simple | GPT-6 Luna (gpt-6-luna) | high |

All five configured roles are native subagents. Simple is the default route for eligible low-complexity isolated work; Main handles non-trivial work and uncertain classifications; High replaces Main for evidenced complexity. A model name does not create a separate execution mode or extra review gates.

## Core Sequence

1. Validate intake and source access, then establish the isolated cycle identity and artifact directory before any governed artifact read.
2. Delegate Planner creation of the cycle manifest and `speckit-specify` with its exact assigned directory; validate the manifest and active-feature output before artifact reads.
3. Plan with `speckit-clarify` only for unavoidable material blockers, `speckit-checklist`, `speckit-plan`, and `speckit-tasks`, then run the cycle validator at planning completion.
4. Run `speckit-analyze` read-only; apply any artifact correction as a separate Planner action, revalidate the cycle, and obtain the planning review. A bounded correction receives the same Reviewer's focused delta re-review; material changes to scope, architecture, acceptance criteria, source set, or artifact identity require a fresh full planning review.
5. After an independent `approved` planning review, revalidate and freeze the artifact baseline, then proceed directly to implementation without asking the user to approve the plan.
6. Revalidate before routing coherent dependency-ready implementation batches. Normal batches use implementer verification until final review; request an intermediate review only for the defined risk triggers. Route corrections and verification handoffs automatically within the authorized scope.
7. The final Reviewer runs read-only `speckit-analyze` and returns the integrated verdict in the same action. When approved-scope work is absent from `tasks.md`, the Planner repairs task coverage under the `speckit-tasks` contract. Use `speckit-converge` only when evidence proves `speckit-implement` executed the current task list, or a future converge contract explicitly supports the executor used. Any task change returns through planning review; after a fresh independent `approved` result and successful validation, implementation resumes automatically.
8. Complete only after that final independent verdict is `approved`. At closure, perform configured remote archival under Remote Memory before the final report; report task verification and `archive_status` separately. Missing storage configuration or failed archival retains local files and does not invent a failed or successful code review. Never convert unavailable evidence into a success claim.

## Quick Reference

| Role | Required references before acting |
| --- | --- |
| Root chat (Orchestrator role) | [Lifecycle and Gates](references/lifecycle-and-gates.md), [Sources and Artifacts](references/sources-and-artifacts.md), [Contracts](references/contracts.md), [Orchestrator](references/orchestrator.md), [Implementers](references/implementers.md), and [Reviewer](references/reviewer.md) |
| Planner | [Lifecycle and Gates](references/lifecycle-and-gates.md), [Sources and Artifacts](references/sources-and-artifacts.md), [Contracts](references/contracts.md), and [Planner](references/planner.md) |
| Main / High / Simple | [Lifecycle and Gates](references/lifecycle-and-gates.md), [Contracts](references/contracts.md), and [Implementers](references/implementers.md) |
| Reviewer | [Lifecycle and Gates](references/lifecycle-and-gates.md), [Sources and Artifacts](references/sources-and-artifacts.md), [Contracts](references/contracts.md), and [Reviewer](references/reviewer.md) |
