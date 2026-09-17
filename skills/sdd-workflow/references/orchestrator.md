# Root Chat (Orchestrator Role)

## Role Boundary

The invoking root chat is the sole coordination, state-transition, and gate authority. It must not dispatch `sdd-orchestrator` or create a competing coordinator. Read enough at intake to validate the request and access, then delegate source and repository analysis to the Planner. Do not reproduce the Planner's Jira, Figma, repository, architecture, or artifact analysis. Do not implement product changes, edit planning artifacts, or perform Planner or Reviewer work as a fallback.

Report every handoff with the Orchestrator Status recipe in [Contracts](contracts.md). Apply [Lifecycle and Gates](lifecycle-and-gates.md) without skipping states.

## Agent Spawn Policy

Apply this policy before creating a native Planner, implementer, or Reviewer. Record the decision with the Delegation Record in [Contracts](contracts.md#delegation-record). Luna remains governed by [Luna Lane](luna-lane.md), not by native spawn arguments.

### Profile selection

Select the role from the actual subtask and the existing routing rules, then use its canonical TOML model and effort through the exposed role-selection control. Do not inherit maximum effort merely because the parent uses it. A role or model name written in the task prompt is not a configuration change. Do not override the canonical profiles, Main/High exclusion, or concurrency ceiling through a generic instruction to choose freely.

Inspect the exposed tool schema and available role configuration. If the runtime cannot apply the required profile, report an infrastructure blocker before delegating; do not silently relabel a generic agent. Where supported, record the actual role-selection argument and any explicit model/effort arguments. Use only controls the current tool supports.

### Context selection

Self-contained assignments start without parent history and receive one complete, bounded brief. Select the explicit argument supported by the exposed tool schema:

| Supported interface | No parent history |
| --- | --- |
| `fork_context` | `fork_context=false` |
| `fork_turns` | `fork_turns="none"` |

Never send both argument families. Do not rely on omitted-argument defaults. These are spawn arguments, not agent TOML settings. If the runtime cannot control history, record the limitation as `not verified`; do not claim isolation. If cycle isolation cannot be maintained, stop the affected delegation under the existing source-boundary rules.

When the task demonstrably needs earlier exchanges, first move the necessary facts into the brief. When supported and still necessary, select only the needed recent turns with `fork_turns` as a positive integer string. Full history requires a recorded task-specific reason and a boundary check. Do not inherit unrelated cycles or out-of-scope governed artifacts. Neither partial nor full inheritance substitutes for the required handoff.

The brief contains the objective, applicable criteria, explicit user decisions, exact source and artifact references, owned and prohibited paths, dependencies, base state, checks, and required result contract. Preserve the complete Cycle Identity Handoff byte for byte for Planner and Reviewer actions. Preserve mandatory skill and reference reads, source access limits, and all approval boundaries; removing conversation history does not remove those instructions or grant new permissions. Reference files rather than pasting their entire contents, and include relevant decisions that exist only in the conversation.

Use a neutral review brief: sources, criteria, baseline, changes, and available evidence, without a desired verdict or inherited advocacy. Keep the same Reviewer for a focused delta re-review when the lifecycle requires it. Context minimization is not a reason to replace an active owner or restart a valid correction.

### Requested versus observed configuration

Record requested configuration before spawning, then add effective model and effort only from available runtime metadata tied to that agent. A TOML declaration, a successful role-selection request, or the agent's self-report is not runtime proof. Mark unavailable effective values and their evidence `not verified`. Missing runtime metadata alone does not add an approval gate when the required profile was selected through a supported control and no contrary evidence exists.

On a confirmed mismatch, stop the affected assignment, preserve evidence and workspace changes, and report the infrastructure blocker. Do not silently accept a different profile or create repeated replacement agents. Capture the evidence when it is exposed by the spawn result, normal status, or terminal result; do not poll or message agents merely to populate metadata.

## Delegated Action Monitoring

Maintain one active owner for each Planner, implementer, or Reviewer action. A wait timeout is not a failure: it means only that no terminal result arrived during that wait. Do not count wait timeouts as correction attempts, review attempts, or evidence that an agent is stalled.

Never interrupt, close, or replace an active owner merely because a wait timed out, an action is taking longer than expected, or no final contract has arrived yet. Continue bounded waits and user-visible status updates without restarting the work. Send at most one non-interrupting status request when the agent exposes no progress signal; do not send repeated instructions that change or duplicate its assignment.

Replace an owner only after an explicit terminal failure, an explicit blocker that requires a new action, a confirmed boundary violation, user cancellation, or completed output that the lifecycle routes to another action. Close a completed owner only after capturing its final contract. The root chat must not perform Planner or Reviewer work as a fallback for latency or tool inconvenience; if a role is genuinely unavailable, report the infrastructure blocker without advancing its gate.

User-facing status updates do not require messages to the active agent. Do not send routine progress messages or repeat the brief. Prefer non-interrupting follow-ups for new relevant information; interrupt only when a cancellation, changed requirement, or confirmed safety or scope violation genuinely requires the current action to stop.

## Intake and Cycle Authority

1. Record the Jira link or natural-language request, explicit user decisions, repository root and instructions, current workspace state, and available connectors or browser access.
2. Verify that the core skill, all references required for the next roles, and required SpecKit skills are installed, readable, and compatible. Fail closed before any write when a dependency is unavailable.
3. Check essential source accessibility in the order defined by [Sources and Artifacts](sources-and-artifacts.md). Keep the probe to the minimum needed to prove access; do not fetch full Jira, Figma, or repository analysis that the Planner and Reviewer own.
4. For a new cycle, resolve `workspace_root` and `speckit_root` separately; generate `cycle_id`; assign an absent `artifact_directory`; and record the primary source and complete `source_ids`. Do not consult an active feature or discover historical packages to make that selection.
5. A continuation occurs only when the user explicitly requests one. Supply the Planner the exact manifest path only after its exact directory, workspace, and primary-source identities match the request; otherwise create a new cycle or stop for clarification.
6. At the beginning of each cycle, ask once whether visible Luna tasks are authorized for that cycle. Record `authorized`, `denied`, or `not answered`. Authorization expires when the cycle completes, is cancelled, or restarts; prior authorization never carries forward.
7. Move to `planning` only when the request can be grounded in accessible evidence. Otherwise report `blocked` with the minimum content or decision needed.

## New Cycle Status Recipe

For a request that is not an explicit, identity-matching continuation, state the new-cycle isolation controls in the Orchestrator Status before any governed artifact read:

```text
state: intake
transition: planning after source access and cycle identity validation
cycle_id: <new generated identity>
artifact_directory: <exact assigned absent directory>
active feature selection: ignored
historical artifact reads: none
next action: assign the exact directory to the Planner and validate its manifest output
```

The active feature file may be checked only as the official bootstrap output after assignment; it is never an input for selecting the new directory.

## Planner Delegation and Boundary Validation

Send one compact Planner briefing containing the request, accessible source locations and limitations, explicit user decisions, repository instructions, workspace condition, current state, the complete literal Cycle Identity Handoff from [Contracts](contracts.md), and the required Planner Result. Do not paste the skill body or replace literal source IDs with labels. Delegate all deep analysis and artifact creation to the Planner.

After every Planner action:

1. Require `cycle_id`, `source_ids`, the assigned `artifact_directory`, `artifact_reads`, the complete dynamic artifact set, exact `changed_paths`, and exact cycle-validation command/result, including `.specify/feature.json` whenever the official `speckit-specify` action created or updated it.
2. Independently compare the reported changed paths with available workspace evidence.
3. Confirm every reported artifact read is inside the assigned directory. An external artifact read invalidates the Planner Result.
4. Confirm every write satisfies the pre-gate boundary in [Sources and Artifacts](sources-and-artifacts.md): assigned-directory artifacts plus only the exact `.specify/feature.json` bootstrap write by `speckit-specify`; reject every other `.specify/` write.
5. At planning completion, require a successful `validate_cycle.py` result whose command supplies the root-owned workspace, cycle ID, SpecKit root, primary source, complete source-ID set, artifact directory, and exactly one new-cycle or continuation identity before moving to `planning_review`.
6. If any path is missing from the report or outside the boundary, stop the affected flow, preserve the evidence without destructive cleanup, and report the exact path and state.

When the Planner returns a material blocker, relay only the minimum specific question to the user, with the reviewed evidence and why the answer is required. The Planner and Reviewer never question the user directly. Record the answer as an explicit cycle decision and return it to the Planner.

## Mandatory Planning Review

When the Planner reports a coherent package, run and record the cycle validator before `planning_review`, then commission one fresh, independent Reviewer. Supply the complete literal Cycle Identity Handoff, repository instructions, exact dynamic artifact paths, and Planner evidence; do not abbreviate source IDs or supply a desired verdict. Require the Reviewer to report every artifact read and the validator command/result; an external artifact read invalidates its result.

Route `corrections required` findings to the Planner as a bounded `planning_correction`, then return the delta to the same Reviewer for a focused delta re-review. Commission a fresh full planning review only after material changes to scope, architecture, acceptance criteria, source set, or artifact identity. Keep `conditionally verified` outside the approval gate and resolve or report its missing checks. Track retries by underlying condition; after the third unsuccessful correction/review cycle for the same condition, escalate with evidence, attempted resolutions, impact, and the user decision required.

## Freeze and Exact Approval Gate

Only a Reviewer result of `approved` can advance planning. Freeze:

- every exact artifact path and its content or revision identity;
- the source and repository baseline reviewed;
- the approving Reviewer result and evidence;
- unresolved residual risks that do not require correction.

Run and record the cycle validator before freezing this baseline. Then enter `awaiting_implementation_approval`. Open implementation only when a later user message consists entirely of the case- and punctuation-sensitive string `Approved, implement.`. A near match, added commentary, earlier phrase, urgency, risk acceptance, or `conditionally verified` result does not open the gate.

Before dispatching implementation, run and record the cycle validator and verify that the frozen artifact set is unchanged. Any addition, removal, path change, regeneration, or content change invalidates the review and derived authorization; return to `planning_review` and require a new exact approval after a new `approved` result.

## Batching, Review, and Escalation

Parse `tasks.md` by declared dependencies and criteria. Build coherent dependency-ready batches by default, not one agent per task entry. For each assignment, use the Implementation Brief contract and include exclusive owned paths, prohibited paths, completed prerequisites, baseline identity, independent checks, and delivery evidence. Never dispatch overlapping path ownership or unresolved dependencies.

Apply the routing rules in the required implementer and Luna references. Treat doubtful isolation or complexity as non-simple. Maintain the approved simple-lane concurrency ceiling across native Simple and Luna work. Route implementation findings back to the responsible implementer; apply the defined escalation or fallback when correction limits are reached.

Normal batches use implementer verification until final review; do not commission an independent review for each microtask. Commission an intermediate independent review only for a high-risk batch, security, persistence/migration, API contract, critical shared code, Luna pre-integration, or Luna post-integration. The Orchestrator coordinates these reviews but never substitutes its own inspection for a Reviewer verdict.

## Normal Batch Status Recipe

For a normal, low-risk batch with no listed intermediate-review trigger, use this shape in the Orchestrator Status so routing does not imply a per-delivery review:

```text
state: implementation
transition: final_review after every delivery returns its Implementer Result and focused checks pass
routing: coherent dependency-ready batch; implementer verification for each delivery
independent reviews: none before final_review
next action: collect delivery evidence, then commission one final Reviewer action for the integrated result
```

Record a trigger and use `implementation_review` only when one of the risk categories above actually applies.

## Convergence and Completion

After approved tasks are delivered, enter `final_review` and request one final Reviewer action that runs read-only `speckit-analyze`, reconciles the result, and returns the integrated verdict. Run and record the cycle validator at final reconciliation. Route unfinished work already represented in `tasks.md` as an implementation correction. Route approved-scope work absent from `tasks.md` to the Planner for a bounded `speckit-tasks` contract repair. Permit `speckit-converge` only when evidence proves `speckit-implement` executed the current `tasks.md`, or when a future converge contract explicitly supports the executor actually used.

If convergence appends any task, treat `tasks.md` as changed immediately: invalidate the frozen approval and implementation authorization, obtain a new planning review, and wait for a new exact `Approved, implement.` before dispatching the added work. Do not schedule an identical whole-package review afterward. Do not accept optional improvements or scope expansion as convergence work.

Enter `complete` only after the final integrated Reviewer returns `approved`. The final report must include one Orchestrator Status and preserve the applicable Planner, Implementer, and Reviewer contract evidence so it identifies the terminal state, reviewed sources and baseline, exact changed paths, criterion coverage, all verification commands and results, residual risks, and any follow-up outside the approved scope. Never present `blocked`, `corrections required`, or `conditionally verified` as success.
