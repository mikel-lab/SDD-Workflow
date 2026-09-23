# Luna Lane

## Boundary and Cycle Authorization

Treat Luna as an optional external, user-visible Codex task, never as a native SDD agent or subagent. The Orchestrator remains the sole coordinator; Luna receives one bounded implementation assignment and cannot plan the feature, select routing, coordinate native agents, or advance a gate.

Treat an explicit request to use visible Luna as current-cycle authorization; do not ask the user to opt in. Native Simple is the default for eligible low-complexity isolated tasks. Without an explicit request to use Luna, keep work on the native lanes. Authorization expires when the cycle completes, is cancelled, or restarts.

The explicit request to use this lane authorizes creation of its bounded task and one local delivery commit after the implementation gate opens. After an independent pre-integration Reviewer result of approved, it also authorizes Main to integrate only that reviewed delivery against the unchanged target baseline. It does not authorize scope expansion, branch creation, pushing, pull-request creation, or acceptance of residual risk.

## Eligibility Predicate

Route to Luna only when every condition is evidenced:

- the implementation gate in [Lifecycle and Gates](lifecycle-and-gates.md) is open and the approved artifact baseline is unchanged;
- the current user request explicitly selects visible Luna;
- the task is unequivocally low-complexity and isolated;
- the dedicated visible task and worktree provide a concrete coordination or isolation benefit over native Simple; low complexity alone is not a reason to use Luna;
- every dependency is satisfied;
- owned paths are exclusive, non-overlapping, and safe to isolate;
- completion is independently verifiable with focused checks;
- the required tools and source context are available inside the isolated worktree;
- a self-contained brief can be supplied without relying on ignored or otherwise absent documentation;
- the expected value is proportionate to task-creation, worktree, review, and integration overhead; and
- adding the task keeps concurrent native Simple plus Luna executions at two or fewer.

If any condition is uncertain, do not use Luna. Route uncertain complexity or isolation to Main. Use native Simple for eligible low-complexity isolated work regardless of visible-Luna authorization, availability, or coordination overhead; a standalone Simple assignment does not need a parallel-safe label.

## Visible Task and Isolated Delivery

Record the explicit user request, bounded objective, classification evidence, and owned paths in the Orchestrator Status. Do not send a separate authorization prompt.

Create a separate user-visible task using GPT-6 Luna Max in a dedicated worktree based on the recorded revision. Never dispatch Luna through native subagent delegation. Keep its worktree and write scope separate from the shared native workspace and every concurrent assignment.

Supply the full Implementation Brief from [Contracts](contracts.md), including the approved criteria, exact owned and prohibited paths, completed dependencies, base revision and artifact approval identity, workspace condition, required checks, and Implementer Result delivery contract. Include all task-local context needed to act safely. Do not point Luna at planning material that is ignored, inaccessible, or absent from its worktree unless the required content is included directly in the brief.

After the implementation gate is open, require exactly one local delivery commit containing only the assigned delta. Do not push it. If the allowed correction round changes the delivery, amend or replace the isolated history so exactly one final local delivery commit remains.

## Review and Integration

Send the isolated delivery commit, brief, base identity, exact diff, and verification evidence to an independent Reviewer before integration. Apply exactly one Reviewer status from [Contracts](contracts.md):

- `approved` authorizes Main to integrate only this reviewed commit when the target baseline is unchanged; it does not approve the integrated result;
- `corrections required` permits one correction round in the same visible Luna task, followed by a fresh pre-integration review; and
- `conditionally verified` satisfies no gate and remains unintegrated until the missing check is resolved and reviewed.

After the first `corrections required` result, preserve the finding evidence and issue one bounded correction brief. If the fresh review returns a second `corrections required` result, preserve the isolated worktree, final commit, diffs, checks, and both reviews as non-authoritative evidence; never integrate that commit automatically or manually. Reassign the original approved task to Main. Main may inspect the failed Luna result but must implement and verify the assignment under the native contract rather than treating the failed commit as approved work.

For a pre-integration `approved` delivery, Main may integrate the exact reviewed commit without another user prompt when the target baseline is unchanged. If the commit or target baseline changes, invalidate the review and repeat the applicable review before integration.

Only Main may integrate after the Orchestrator confirms the independent pre-integration `approved` result and unchanged target baseline. Main must preserve concurrent and user changes, resolve no conflict by discarding unrelated work, verify the combined state, and return exact integration evidence. Luna and the Orchestrator never merge, cherry-pick, rebase, or otherwise incorporate the delivery.

Commission a new independent post-integration review of the shared repository state. Recheck the approved delta, conflicts, changed paths, criteria, and combined checks; never reuse the isolated-delivery verdict. Route confirmed integration findings to Main under the native correction rules. Only a post-integration `approved` result allows the integrated Luna task to proceed toward convergence and final review.
