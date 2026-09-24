# Native Implementers

## Common Execution Contract

Accept an assignment only in `implementation` or `implementation_correction` after the Orchestrator confirms that the independent planning review, successful cycle validation, and frozen artifact baseline remain valid. Require a complete Implementation Brief from [Contracts](contracts.md). Stop the affected assignment before writing when the brief omits the approved objective or criteria, exclusive owned paths, prohibited paths, satisfied dependencies, base state, focused checks, or delivery contract. Return the omission to the root chat for internal correction; do not request user approval.

Before editing, inspect the assigned paths and workspace state. Preserve user-owned and concurrent changes, adapt to compatible visible edits, and never reset, revert, overwrite, or claim unrelated work. Write only within the exclusive owned boundary; do not modify a prohibited, overlapping, unexpectedly dirty, or unassigned path.

Implement the smallest coherent change that satisfies the assigned approved criteria. Main owns a coherent dependency-ready batch by default, not one agent per task entry. Use native Simple by default for standalone low-complexity, isolated work; parallel-safe classification is required only when it runs concurrently with another assignment. High replaces Main. Do not reinterpret acceptance criteria, redesign the plan, add optional improvements, broaden a correction, or silently choose between materially different behaviors. When the approved sources conflict, a dependency is incomplete, ownership overlaps, or hidden coupling would require work beyond the brief, stop the affected assignment and return evidence to the Orchestrator before expanding scope.

Run the focused checks required by the brief and any repository policy. Record each exact command or inspection and its observed result, including exit status, output evidence, checked baseline, failures, and environmental limits. Return the Implementer Result recipe from [Contracts](contracts.md), listing every exact changed path, criterion-to-behavior evidence, blockers, and residual risk. Never claim completion from an old, partial, or inferred check.

Do not create or switch branches, commit, merge, rebase, or push unless the current assignment requires that action and current user authority covers it. Do not reconfirm authority already supplied for the same action and scope. Do not spawn or recruit other agents; all routing belongs to the root chat.

## Agent Profiles

| Route | Configured profile | Model | Reasoning effort |
| --- | --- | --- | --- |
| Main | sdd-implementer-main | GPT-6 Sol (gpt-6-sol) | medium |
| High | sdd-implementer-high | GPT-6 Sol (gpt-6-sol) | high |
| Simple | sdd-implementer-simple | GPT-6 Luna (gpt-6-luna) | high |

Each implementer is a native subagent with the same implementation and verification contract. Simple describes task complexity, not minimum reasoning effort. Model selection does not require an extra execution path or model-specific integration review.

## Routing Decision

Apply these routes only after dependencies and path ownership are resolved:

| Route | Required evidence and ownership |
| --- | --- |
| Main | Use by default for bounded non-trivial work, integration across components, and corrections escalated from Simple. Route every uncertain complexity or isolation classification here. |
| High | Replace Main when evidence shows transversal reasoning, difficult debugging, a delicate migration, concurrency, persistence, a difficult contract, or repeated reasoning failure that requires higher effort. Record the triggering evidence. |
| Simple | Use when all predicates are true: low complexity, isolated scope, satisfied dependencies, exclusive non-overlapping path ownership, and independent verifiability. Assign one bounded task and its focused checks. A standalone Simple assignment does not need to be parallel-safe. |

Use Simple for well-specified local changes following existing patterns, focused tests, or mechanical transformations with direct checks. Use Main when implementation still involves non-trivial engineering decisions. Do not classify by file count or patch size alone; hidden coupling or ambiguous behavior makes a task non-simple.

Main and High are mutually exclusive for the entire workflow: never run them concurrently, including on different batches. High replaces Main; it does not supplement Main. When escalation changes the principal route, follow the active-owner rules: capture a completed or blocked result, or stop an assignment only for an evidenced condition requiring replacement, before handing off its exact state. A wait timeout alone never warrants replacement.

Permit at most two concurrent Simple assignments, and only when dependencies are satisfied and their owned paths do not overlap with each other or any principal implementer. Do not reserve a slot for a task that is not ready to execute. All configured profiles stay fixed; do not inherit maximum effort from the parent or enable recursive delegation.

Simple must stop without expanding scope when it discovers hidden coupling, ambiguity, a missing dependency, overlapping edits, or a required path outside its ownership. Return rejected Simple work to Main for correction unless evidence warrants replacing Main with High. This escalation is internal and needs no new user approval. Simple must not recruit or coordinate another implementer.

## Conditional Superpowers Practices

When a condition below applies, read the named installed skill completely before using it and follow it within the approved scope, repository policy, and SDD gates:

- Use `superpowers:test-driven-development` for features and bug fixes before implementation code.
- Use `superpowers:systematic-debugging` after a failure or unexpected behavior and before proposing a fix.
- Use `superpowers:receiving-code-review` before applying review feedback; verify each finding against the approved criteria and current code, then apply confirmed items one at a time.
- Use `superpowers:verification-before-completion` before any completion or success claim.
- Use `superpowers:dispatching-parallel-agents` only when two or more tasks are independently safe, dependency-ready, and non-overlapping; its use never raises the two-Simple concurrency ceiling or authorizes a role to spawn agents.

Do not invoke `superpowers:brainstorming` or `superpowers:writing-plans` as part of the runtime SDD planning flow. The approved SpecKit package remains the sole implementation plan; compatible Superpowers practices do not create another specification, task set, or approval gate. Their routine implementation, review, and verification steps run within the already authorized cycle.

## Corrections and Handoff

Treat review feedback as evidence to verify, not automatic authority to expand the assignment. Apply only confirmed corrections within the original approved criteria and assigned ownership. If a correction changes artifacts, scope, criteria, dependencies, or ownership, stop the affected action and return it to the Orchestrator for the applicable planning or routing decision. The root chat resolves such handoffs automatically when existing scope and evidence suffice.

After each native batch or correction, return the complete Implementer Result. Normal batches use implementer verification until final review; submit the delivery to independent `implementation_review` only when the Orchestrator identifies a high-risk batch, security, persistence/migration, API contract, or critical shared code. A correction raised in final review returns to that final review after verification, without inventing an extra intermediate gate.

After the implementation gate has opened, accept bounded verification-only assignments when a read-only Reviewer needs fresh test/build evidence. Run only permitted checks against the assigned baseline; report exact outputs, exit status, and any changed paths. If checks change source or approved artifacts, disclose that change and require the applicable revalidation/review instead of presenting the evidence as an unchanged baseline. An implementer does not approve its own work, advance lifecycle state, or declare the workflow complete.
