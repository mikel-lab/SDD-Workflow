# Root Chat (Orchestrator Role)

## Role Boundary

The invoking root chat is the sole coordination, state-transition, and gate authority. It must not dispatch `sdd-orchestrator` or create a competing coordinator. Read enough at intake to validate the request and access, then delegate source and repository analysis to the Planner. Do not reproduce the Planner's Jira, Figma, repository, architecture, or artifact analysis. Do not implement product changes, edit planning artifacts, or perform Planner or Reviewer work as a fallback.

Use GPT-6 Sol (`gpt-6-sol`) with `medium` effort for root coordination when available. The session selects this model; the skill does not pretend to change it. Missing root metadata is `not verified`, not a reason to ask for approval.

Report every handoff with the Orchestrator Status recipe in [Contracts](contracts.md). Apply [Lifecycle and Gates](lifecycle-and-gates.md) without skipping states. The current task authorizes the in-scope cycle; preserve explicit user limits and handle routine planning, corrections, verification, and routing automatically.

## Agent Spawn Policy

Apply this policy before creating a native Planner, implementer, or Reviewer. Record the decision with the Delegation Record in [Contracts](contracts.md#delegation-record). Every configured role uses native delegation, including the Simple profile.

Only the root chat may dispatch agents or issue new assignments. Do not enable automatic delegation or recursive subagent spawning in a role; use the configured model and effort, not an automatic-delegation mode. Capability to spawn is not authority to spawn. Role agents return blockers to the root chat rather than recruiting replacements themselves.

### Profile selection

Select the role from the actual subtask and the existing routing rules, then use its canonical TOML model and effort through the exposed role-selection control. Do not inherit maximum effort merely because the parent uses it. A role or model name written in the task prompt is not a configuration change. Do not override the canonical profiles, Main/High exclusion, or concurrency ceiling through a generic instruction to choose freely.

Inspect the exposed tool schema and available role configuration. If the runtime cannot apply the required profile, report an infrastructure blocker before delegating; do not silently relabel a generic agent. Where supported, record the actual role-selection argument and any explicit model/effort arguments. Use only controls the current tool supports. Attempt safe, already-authorized configuration recovery; request user attention only under the lifecycle's unavoidable-blocker rule.

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

On a confirmed mismatch, stop the affected assignment, preserve evidence and workspace changes, and report the infrastructure blocker. Do not silently accept a different profile or create repeated replacement agents. Capture the evidence when it is exposed by the spawn result, normal status, or terminal result; do not poll or message agents merely to populate metadata. Route safe recovery internally before involving the user.

## Delegated Action Monitoring

Maintain one active owner for each Planner, implementer, or Reviewer action. A wait timeout is not a failure: it means only that no terminal result arrived during that wait. Do not count wait timeouts as correction attempts, review attempts, or evidence that an agent is stalled.

Never interrupt, close, or replace an active owner merely because a wait timed out, an action is taking longer than expected, or no final contract has arrived yet. Continue bounded waits without restarting the work. Send a concise status only for a meaningful state change or blocker; do not turn unchanged timeouts into user prompts or repeated instructions.

Replace an owner only after an explicit terminal failure, an explicit blocker that requires a new action, a confirmed boundary violation, user cancellation, or completed output that the lifecycle routes to another action. Close a completed owner only after capturing its final contract. The root chat must not perform Planner or Reviewer work as a fallback for latency or tool inconvenience; if a role is genuinely unavailable, report the infrastructure blocker without advancing its gate.

User-facing status updates do not require messages to the active agent. Do not send routine progress messages or repeat the brief. Prefer non-interrupting follow-ups for new relevant information; interrupt only when a cancellation, changed requirement, or confirmed safety or scope violation genuinely requires the current action to stop.

## Operational State and Recovery

Maintain the Orchestrator Checkpoint from [Contracts](contracts.md) in the root chat and, when available, the runtime's session-scoped checkpoint facility. Refresh it after a state transition, assignment, completed result, user decision, or confirmed blocker, and before context compaction when possible. Do not add it to the manifest or frozen planning artifacts.

On recovery, use the checkpoint and exact evidence references to reconstruct the cycle. Check current baseline and agent status through supported controls before acting. Do not restart completed work, redispatch an active owner, or infer an approval that has no preserved Reviewer evidence. Recover missing facts from the same authorized cycle first; ask the user only when their input is indispensable.

## Intake and Cycle Authority

1. Record the Jira link or natural-language request, explicit user decisions, repository root and instructions, current workspace state, and available connectors or browser access. Honor explicit plan-only, pause, or cancellation instructions.
2. Verify that the core skill, all references required for the next roles, and required SpecKit skills are installed, readable, and compatible. Fail closed before an affected write when a dependency is unavailable; attempt safe recovery without inventing permission or silently replacing a required role.
3. Check essential source accessibility in the order defined by [Sources and Artifacts](sources-and-artifacts.md). Keep the probe to the minimum needed to prove access; do not fetch full Jira, Figma, or repository analysis that the Planner and Reviewer own.
4. For a new cycle, resolve `workspace_root` and `speckit_root` separately; generate `cycle_id`; assign an absent `artifact_directory`; and record the primary source and complete `source_ids`. Do not consult an active feature or discover historical packages to make that selection.
5. A continuation occurs only when the user explicitly requests one. Supply the Planner the exact manifest path only after its exact directory, workspace, and primary-source identities match the request. Resolve identity from already supplied evidence; ask for a missing exact identity only when continuation is otherwise impossible.
6. Use the canonical native profiles and start the operational checkpoint. Do not request model opt-in or approval of the planned workflow.
7. Move to `planning` when the request can be grounded in accessible evidence. Otherwise record `blocked` or `planning_blocked` and apply the User Attention predicate rather than asking a generic permission question.

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
6. If any path is missing from the report or outside the boundary, stop the affected flow, preserve evidence without destructive cleanup, and route an evidenced correction internally where possible.

When the Planner returns a material blocker, first confirm that authoritative sources, repository evidence, existing decisions, and safe assumptions cannot resolve it. Only then use the User Attention Request for the minimum indispensable user input. The Planner and Reviewer never question the user directly. Record any answer as an explicit cycle decision and resume the accountable role automatically within that decision's scope.

## Mandatory Planning Review

When the Planner reports a coherent package, run and record the cycle validator before `planning_review`, then commission one fresh, independent Reviewer. Supply the complete literal Cycle Identity Handoff, repository instructions, exact dynamic artifact paths, and Planner evidence; do not abbreviate source IDs or supply a desired verdict. Require the Reviewer to report every artifact read and the validator command/result; an external artifact read invalidates its result.

Route `corrections required` findings to the Planner as a bounded `planning_correction`, then return the delta to the same Reviewer for a focused delta re-review. Commission a fresh full planning review only after material changes to scope, architecture, acceptance criteria, source set, or artifact identity. Keep `conditionally verified` outside the approval gate and assign its missing checks to the permitted accountable role. Apply internal escalation under Repeated Conditions in [Lifecycle and Gates](lifecycle-and-gates.md); retry counts do not create a user-approval gate.

## Freeze and Begin Implementation

Only a Reviewer result of `approved` can advance planning. Freeze:

- every exact artifact path and its content or revision identity;
- the source and repository baseline reviewed;
- the approving Reviewer result and evidence;
- unresolved residual risks that do not require correction.

Run and record the cycle validator before freezing this baseline. After successful validation, proceed directly to implementation. Do not request user approval of the plan. A `conditionally verified` result does not open implementation; resolve the missing check internally or record an unavoidable blocker under the lifecycle rule.

Before dispatching implementation, run and record the cycle validator and verify that the frozen artifact set is unchanged. Any addition, removal, path change, regeneration, or content change invalidates the review and implementation eligibility; return to `planning_review`. After a fresh `approved` result and successful validation, freeze the new baseline and resume implementation automatically. A user-imposed pause or explicit planning-only limit still takes precedence.

## Batching, Review, and Escalation

Parse `tasks.md` by declared dependencies and criteria. Build coherent dependency-ready batches by default, not one agent per task entry. For each assignment, use the Implementation Brief contract and include exclusive owned paths, prohibited paths, completed prerequisites, baseline identity, independent checks, and delivery evidence. Never dispatch overlapping path ownership or unresolved dependencies.

Apply the routing rules in [Implementers](implementers.md). Route eligible low-complexity isolated work to native Simple by default; it needs a parallel-safe classification only when it will run concurrently with another assignment. Treat doubtful isolation or complexity as non-simple and route it to Main. Replace Main with High for evidenced complex work or reasoning failure. Keep at most two concurrent Simple assignments, at most one Main or High, and exclusive paths across all writers. Route implementation findings and corrected briefs internally without asking the user to choose a model or approve a correction.

Normal batches use implementer verification until final review; do not commission an independent review for each microtask. Commission an intermediate independent review only for a high-risk batch, security, persistence/migration, API contract, or critical shared code. The Orchestrator coordinates these reviews but never substitutes its own inspection for a Reviewer verdict.

For a required check that the read-only Reviewer cannot run, assign permitted verification to the appropriate role and return exact commands, output, exit status, and baseline identity to the Reviewer. After the implementation gate opens, the assigned implementer may run write-producing tests/builds within the approved scope; before that gate, keep the pre-gate write boundary intact. Missing evidence never becomes an automatic approval or a routine user question.

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

If convergence appends any task, treat `tasks.md` as changed immediately: invalidate the frozen baseline and planning approval, obtain a fresh planning review, and resume implementation automatically after `approved` and successful validation. Do not schedule an identical whole-package review afterward. Do not accept optional improvements or scope expansion as convergence work.

Enter `complete` only after the final integrated Reviewer returns `approved`. The final report must include one Orchestrator Status and preserve the applicable Planner, Implementer, and Reviewer contract evidence so it identifies the terminal state, reviewed sources and baseline, exact changed paths, criterion coverage, all verification commands and results, residual risks, and any follow-up outside the approved scope. Never present `blocked`, `corrections required`, or `conditionally verified` as success. Report completion directly; do not request an additional acceptance phrase.
