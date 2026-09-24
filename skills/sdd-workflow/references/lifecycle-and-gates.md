# Lifecycle and Gates

## State Order

Use these normative states in order:

- intake
- planning
- planning_blocked
- planning_review
- planning_correction
- implementation
- implementation_review
- implementation_correction
- final_review
- complete, blocked, or cancelled

## Autonomous Execution and User Attention

The task request authorizes in-scope planning, implementation, verification, corrections, and internal escalation through the complete cycle. Continue automatically after each satisfied internal gate. Do not request a confirmation phrase, a second plan approval, approval of routine corrections, or permission to choose a configured native implementer. An `approved` status is an independent Reviewer verdict, not text the user must write. Respect an explicit user pause, cancellation, plan-only request, or narrower execution limit.

Before involving the user, attempt safe in-scope recovery using available source and repository evidence, existing authorization, supported tool controls, documented non-blocking assumptions, and the appropriate role. Correct an incomplete brief, reroute complexity, or obtain missing verification evidence internally. Do not request permission already supplied for the same action and scope. A reversible implementation choice or optional improvement is not a blocker.

Request user attention only when all of these conditions hold: a necessary next action is blocked; accessible evidence and authorized recovery cannot resolve it safely; and the missing decision, essential source, access, or authority is something only the user can supply. Ask before the affected action, using the User Attention Request in [Contracts](contracts.md). Keep unaffected, independently safe work progressing when the frozen baseline and ownership rules allow it. A task that cannot proceed for a purely technical reason must be reported as blocked with evidence, not converted into an empty approval question.

Autonomy does not authorize changing the user's intended behavior, inventing missing requirements, expanding scope, bypassing access controls, weakening sandbox or security protections, ignoring externally enforced approvals, accepting residual risk on the user's behalf, or publishing/deploying without applicable authority. Do not ask for new authority for optional work; leave it outside this cycle.

## Transitions

1. Intake validates the request, mandatory dependencies, source accessibility, repository instructions, and initial authority. Advance to planning when the cycle can be grounded in evidence. Resolve accessible failures internally; apply the User Attention rule only for an unavoidable user-owned blocker.
2. Planning produces the complete dynamic SDD artifact set. Enter planning_blocked only for a material ambiguity or missing essential source that cannot be resolved from available evidence; enter planning_review when the set is ready for independent review.
3. Planning_blocked records the evidence and minimum decision or source content required. Resume planning automatically when resolved; remain blocked while essential information is unavailable.
4. Planning_review is one full planning Reviewer action. Approved advances directly to implementation after successful cycle validation and freezing the reviewed baseline; corrections required advances to planning_correction; conditionally verified remains outside the implementation gate while its missing check is assigned for resolution.
5. Planning_correction is a Planner write action followed by the same Reviewer's focused delta re-review when the correction is bounded. A new full planning review is required only after material changes to scope, architecture, acceptance criteria, source set, or artifact identity. No user approval is requested for either path.
6. Implementation executes coherent dependency-ready batches. Normal batches use implementer verification and remain in implementation; they do not require an independent review for each microtask. Enter implementation_review only for a high-risk batch, security, persistence/migration, API contract, or critical shared code.
7. Implementation_review advances to implementation_correction when corrections are required, or returns to implementation when its triggered review is approved. Incomplete checks are routed to the responsible role and then back to the Reviewer; they do not satisfy a gate.
8. Implementation_correction applies a bounded confirmed correction, verifies it, and returns it to the review that raised the finding: implementation_review for an intermediate-risk finding, or final_review for a final-review finding. Do not add a redundant intermediate review for a normal final-review correction.
9. Final_review combines the final Reviewer's read-only speckit-analyze reconciliation with its final integrated verdict. Approved-scope work already present in tasks.md returns as an implementation correction. Approved-scope work absent from tasks.md requires a Planner speckit-tasks contract repair; speckit-converge is permitted only after proven speckit-implement execution of the current tasks, or when a future converge contract explicitly supports the actual executor. Any task change returns to planning_review; after fresh approval and validation, implementation resumes automatically.
10. Advance to complete only when the final Reviewer returns approved; route findings to the applicable correction state. Use blocked or cancelled when the cycle ends without a verified delivery. Do not ask the user to confirm completion after the evidence already satisfies the final gate.

## Planning and Implementation Gates

The planning gate requires an independent Reviewer result of approved for the complete artifact set. The cycle validator must also pass, and the root chat freezes the exact artifact paths, contents, and reviewed baseline.

The implementation gate opens automatically when the planning review is still valid, the cycle validator passes, and the frozen artifact set is unchanged. The Orchestrator proceeds directly to implementation; it does not ask the user to review or approve the SDD plan. Conditionally verified records incomplete verification and never satisfies the gate. Resolve the missing check through the accountable role, then obtain the independent verdict. Only an unavoidable blocker is escalated under the User Attention rule.

## Common Mistakes

### Rationalization Table

| Observed rationalization | Required response |
| --- | --- |
| "The deadline is today" is a reason to skip a required review or conditioned check. | Keep implementation closed. Resolve the check, obtain a fresh independent approved result, validate and freeze the package, then proceed automatically. |
| A reviewed plan needs the user's final confirmation before coding. | The in-scope task is already authorized; advance after independent approval, validation, and baseline freeze. |
| Three unsuccessful corrections automatically require a user approval. | Diagnose and escalate internally; ask the user only for an unavoidable input that they must supply. |

### Red Flags

- Preparing an implementer instruction while the planning review is conditionally verified.
- Treating urgency as a substitute for a complete independent review or required check.
- Asking the user to approve a coherent plan that has passed independent review and validation.
- Turning a role handoff, retry counter, or missing telemetry into a manual approval gate.

## Approval Invalidation

Freeze and record every generated artifact path, plus .specify/feature.json when the official speckit-specify bootstrap changed it. Any content, path, addition, removal, or regeneration in that baseline invalidates the planning approval and implementation eligibility. Return to planning_review; after a fresh approved result, successful validation, and a new frozen baseline, resume implementation automatically without a user approval prompt.

This applies to Planner corrections, speckit-tasks contract repairs, and compatible speckit-converge writes after implementation. It does not expand the original scope: convergence may add only work required to meet the already approved sources and criteria. Changes to the separate operational checkpoint do not change the planning baseline.

## Repeated Conditions

Track correction and review cycles by the underlying blocking condition, not rewritten wording. Allow at most three unsuccessful correction/review cycles before internal escalation. This threshold is not a user-approval gate. Preserve the attempts, evidence, active owner, and affected baseline; do not reset the count by relabeling the same defect.

Do not repeat an unchanged failing strategy. The root chat obtains a focused diagnosis from the responsible role and routes a materially different, evidenced recovery: an improved bounded brief, a Planner correction, or replacement of Main with the configured High profile when warranted. Respect active-owner handoff and Main/High exclusivity; do not restart active work because a wait timed out. Revalidate and re-review every changed planning baseline before resuming implementation.

Continue only when the recovery has a concrete new basis and a bounded verification target. When no safe autonomous recovery remains, apply Autonomous Execution and User Attention: ask only for a specific necessary user-owned input, or report the technical blocker honestly when the user has no actionable decision. Neither the retry count nor a failed check grants approval.
