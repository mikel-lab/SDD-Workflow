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

## Transitions

1. Intake validates the request, mandatory dependencies, source accessibility, repository instructions, and initial authority. Advance to planning when the cycle can be grounded in evidence; otherwise finish as blocked or cancelled.
2. Planning produces the complete dynamic SDD artifact set. Enter planning_blocked only for a material ambiguity or missing essential source that cannot be resolved from available evidence; enter planning_review when the set is ready for independent review.
3. Planning_blocked records the evidence and minimum decision or source content required. Resume planning when resolved; remain blocked while the essential information is unavailable.
4. Planning_review is one full planning Reviewer action. Approved advances directly to implementation after successful cycle validation and freezing the reviewed baseline; corrections required advances to planning_correction; conditionally verified remains outside the implementation gate until the missing check is resolved.
5. Planning_correction is a Planner write action followed by the same Reviewer's focused delta re-review when the correction is bounded. A new full planning review is required only after material changes to scope, architecture, acceptance criteria, source set, or artifact identity.
6. Implementation executes coherent dependency-ready batches. Normal batches use implementer verification and remain in implementation; they do not require an independent review for each microtask. Enter implementation_review only for a high-risk batch, security, persistence/migration, API contract, critical shared code, Luna pre-integration, or Luna post-integration.
7. Implementation_review advances to implementation_correction when corrections are required, or returns to implementation when its triggered review is approved.
8. Implementation_correction returns corrected work to implementation_review.
9. Final_review combines the Reviewer's read-only speckit-analyze reconciliation with its final integrated verdict. Approved-scope work already present in tasks.md returns as an implementation correction. Approved-scope work absent from tasks.md requires a Planner speckit-tasks contract repair; speckit-converge is permitted only after proven speckit-implement execution of the current tasks, or when a future converge contract explicitly supports the actual executor. Any task change returns to planning_review; after fresh approval and validation, implementation resumes automatically.
10. Advance to complete only when the final Reviewer returns approved; route findings to the applicable correction state. Use blocked or cancelled when the cycle ends without a verified delivery.

## Planning and Implementation Gates

The planning gate requires an independent Reviewer result of approved for the complete artifact set. The cycle validator must also pass, and the root chat freezes the exact artifact paths, contents, and reviewed baseline.

The implementation gate opens automatically when the planning review is still valid, the cycle validator passes, and the frozen artifact set is unchanged. The Orchestrator proceeds directly to implementation; it does not ask the user to review or approve the SDD plan. Conditionally verified records incomplete verification and never satisfies the gate. Resolve the missing check or stop as blocked.

## Common Mistakes

### Rationalization Table

| Observed rationalization | Required response |
| --- | --- |
| “The deadline is today” is a reason to skip a required review or conditioned check. | Keep implementation closed. Resolve the check, obtain a fresh independent approved result, validate and freeze the package, then proceed automatically. |

### Red Flags

- Preparing an implementer instruction while the planning review is conditionally verified.
- Treating urgency as a substitute for a complete independent review or required check.
- Asking the user to approve a coherent plan that has passed independent review and validation.

## Approval Invalidation

Freeze and record every generated artifact path, plus .specify/feature.json when the official speckit-specify bootstrap changed it. Any content, path, addition, removal, or regeneration in that baseline invalidates the planning approval and implementation eligibility. Return to planning_review; after a fresh approved result, successful validation, and a new frozen baseline, resume implementation automatically without a user approval prompt.

This applies to Planner corrections, speckit-tasks contract repairs, and compatible speckit-converge writes after implementation. It does not expand the original scope: convergence may add only work required to meet the already approved sources and criteria.

## Repeated Conditions

Track correction and review cycles by the underlying blocking condition, not by rewritten wording. Permit at most three cycles for the same condition. If the condition remains after the third cycle, stop and ask the user only for the specific decision or access needed to unblock it, with the precise evidence, attempted resolutions, and impact. Do not present the escalation as success or gate approval.
