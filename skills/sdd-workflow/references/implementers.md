# Native Implementers

## Common Execution Contract

Accept an assignment only in `implementation` or `implementation_correction` after the Orchestrator confirms that the approved artifact baseline and exact implementation authorization remain valid. Require a complete Implementation Brief from [Contracts](contracts.md). Stop before writing when the brief omits the approved objective or criteria, exclusive owned paths, prohibited paths, satisfied dependencies, base state, focused checks, or delivery contract.

Before editing, inspect the assigned paths and workspace state. Preserve user-owned and concurrent changes, adapt to compatible visible edits, and never reset, revert, overwrite, or claim unrelated work. Write only within the exclusive owned boundary; do not modify a prohibited, overlapping, unexpectedly dirty, or unassigned path.

Implement the smallest coherent change that satisfies the assigned approved criteria. Main owns a coherent dependency-ready batch by default, not one agent per task entry. Use Simple or Luna only when isolation yields net savings; High replaces Main. Do not reinterpret acceptance criteria, redesign the plan, add optional improvements, broaden a correction, or silently choose between materially different behaviors. When the approved sources conflict, a dependency is incomplete, ownership overlaps, or hidden coupling would require work beyond the brief, stop the affected assignment and return the evidence to the Orchestrator before expanding scope.

Run the focused checks required by the brief and any repository policy. Record each exact command or inspection and its observed result, including failures or environmental limits. Return the Implementer Result recipe from [Contracts](contracts.md), listing every exact changed path, criterion-to-behavior evidence, blockers, and residual risk. Never claim completion from an old, partial, or inferred check.

Do not create or switch branches, commit, merge, rebase, or push unless the current assignment explicitly requires that action and current user authority covers it. Luna delivery and integration use the separate rules in [Luna Lane](luna-lane.md).

## Routing Decision

Apply these routes only after dependencies and path ownership are resolved:

| Route | Required evidence and ownership |
| --- | --- |
| Main | Use by default for bounded non-trivial work, integration across components, native Simple corrections, fallback after a second rejected Luna delivery, and gated integration of an approved Luna delivery. Route every uncertain complexity or isolation classification here. |
| High | Replace Main when evidence shows transversal reasoning, difficult debugging, a delicate migration, concurrency, persistence, a difficult contract, or repeated reasoning failure that requires higher effort. Record the triggering evidence. |
| Simple | Use only when every predicate is true: low complexity, isolated scope, satisfied dependencies, exclusive non-overlapping path ownership, and independent verifiability. Assign one bounded task and its focused checks. |

Main and High are mutually exclusive for the entire workflow: never run them concurrently, including on different batches. High replaces Main; it does not supplement Main. When escalation changes the principal route, stop the prior principal assignment and hand off its exact state before the replacement begins.

Count native Simple and Luna executions together. Permit at most two concurrent executions across that aggregate simple lane, and only when their dependencies are satisfied and their owned paths do not overlap. Do not reserve a slot for a task that is not ready to execute.

Simple must stop without expanding scope when it discovers hidden coupling, ambiguity, a missing dependency, overlapping edits, or a required path outside its ownership. Return rejected Simple work to Main for correction unless evidence warrants replacing Main with High. Simple must not recruit or coordinate another implementer.

## Conditional Superpowers Practices

When a condition below applies, read the named installed skill completely before using it and follow it within the approved scope, repository policy, and SDD gates:

- Use `superpowers:test-driven-development` for features and bug fixes before implementation code.
- Use `superpowers:systematic-debugging` after a failure or unexpected behavior and before proposing a fix.
- Use `superpowers:receiving-code-review` before applying review feedback; verify each finding against the approved criteria and current code, then apply confirmed items one at a time.
- Use `superpowers:verification-before-completion` before any completion or success claim.
- Use `superpowers:dispatching-parallel-agents` only when two or more tasks are independently safe, dependency-ready, and non-overlapping; its use never raises the two-execution aggregate simple-lane ceiling.

Do not invoke `superpowers:brainstorming` or `superpowers:writing-plans` as part of the runtime SDD planning flow. The approved SpecKit package remains the sole implementation plan; compatible Superpowers practices do not create another specification, task set, or approval gate.

## Corrections and Handoff

Treat review feedback as evidence to verify, not automatic authority to expand the assignment. Apply only confirmed corrections within the original approved criteria and assigned ownership. If a correction changes artifacts, scope, criteria, dependencies, or ownership, stop and return it to the Orchestrator for the applicable planning or routing decision.

After each native batch or correction, return the complete Implementer Result. Normal batches use implementer verification until final review; submit the delivery to independent `implementation_review` only when the Orchestrator identifies a high-risk batch, security, persistence/migration, API contract, critical shared code, or a Luna pre- or post-integration gate. An implementer does not approve its own work, advance lifecycle state, or declare the workflow complete.
