# Lifecycle and Gates

## State Order

Use these normative states in order:

```text
intake
planning
planning_blocked
planning_review
planning_correction
awaiting_implementation_approval
implementation
implementation_review
implementation_correction
post_implementation_convergence
final_review
complete | blocked | cancelled
```

## Transitions

1. `intake` validates the request, mandatory dependencies, source accessibility, repository instructions, and initial authority. Advance to `planning` when the cycle can be grounded in evidence; otherwise finish as `blocked` or `cancelled`.
2. `planning` produces the complete dynamic SDD artifact set. Enter `planning_blocked` for a material ambiguity, or `planning_review` when the set is ready for independent review.
3. `planning_blocked` records the evidence and minimum question required. Resume `planning` after a resolving decision; remain blocked while the decision is unavailable.
4. `planning_review` ends with one Reviewer status. `approved` advances to `awaiting_implementation_approval`; `corrections required` advances to `planning_correction`; `conditionally verified` remains outside every approval gate.
5. `planning_correction` is a Planner write action followed by a new `planning_review`.
6. `awaiting_implementation_approval` freezes the exact approved artifact paths and review evidence. Advance to `implementation` only when the approval remains valid and the user's entire response is exactly `Approved, implement.`.
7. `implementation` executes only approved, dependency-ready work and then advances to `implementation_review`.
8. `implementation_review` advances to `implementation_correction` when corrections are required, or to `post_implementation_convergence` when the reviewed delivery is ready to reconcile.
9. `implementation_correction` returns corrected work to `implementation_review`.
10. `post_implementation_convergence` uses the Reviewer's read-only `speckit-analyze` to compare sources, approved artifacts, tasks, and delivered behavior. Approved-scope work already present in `tasks.md` returns as an implementation correction. Approved-scope work absent from `tasks.md` requires a Planner `speckit-tasks` contract repair; `speckit-converge` is permitted only after proven `speckit-implement` execution of the current tasks, or when a future converge contract explicitly supports the actual executor. Any task change returns to `planning_review`.
11. `final_review` independently verifies the complete integrated result. Advance to `complete` only on `approved`; route findings to the applicable correction state. Use `blocked` or `cancelled` when the cycle ends without a verified delivery.

## Planning and Implementation Gates

The planning gate requires an independent Reviewer result of `approved` for the complete artifact set. `conditionally verified` records incomplete verification and never satisfies an approval gate. A deadline, urgency, general approval, or acceptance of risk does not convert it to `approved`.

The implementation gate requires both, in this order:

1. A still-valid planning review with status `approved`.
2. A later user message whose complete content exactly matches `Approved, implement.`.

String matching is case-sensitive and punctuation-sensitive. Text such as `approved, go ahead`, `Approved, implement`, added commentary, or the exact phrase sent before planning approval leaves the workflow in `awaiting_implementation_approval`.

## Common Mistakes

### Rationalization Table

| Observed rationalization | Required response |
| --- | --- |
| “The deadline is today” or `approved, go ahead` is enough to start while a required review check remains conditioned. | Keep implementation closed. Resolve the check, obtain a fresh independent `approved` result, freeze the package, and then require a later exact `Approved, implement.`. |

### Red Flags

- Preparing an implementer instruction while the planning review is `conditionally verified`.
- Treating urgency or a general approval as a substitute for either stage of the implementation gate.

## Approval Invalidation

Freeze and record every generated artifact path at approval, plus `.specify/feature.json` when the official `speckit-specify` bootstrap changed it. Any content, path, addition, removal, or regeneration in that governed baseline invalidates both the planning approval and any implementation authorization derived from it. Return to `planning_review`; after a new `approved` result, require a new exact `Approved, implement.` message.

This applies to Planner corrections, `speckit-tasks` contract repairs, and compatible `speckit-converge` writes after implementation. It does not expand the original scope: convergence may add only work required to meet the already approved sources and criteria.

## Repeated Conditions

Track correction and review cycles by the underlying blocking condition, not by rewritten wording. Permit at most three cycles for the same condition. If the condition remains after the third cycle, stop cycling and escalate to the user with the precise evidence, attempted resolutions, impact, and decision required. Do not present the escalation as success or gate approval.
