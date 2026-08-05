# Luna Lane

## Boundary and Cycle Authorization

Treat Luna as an optional external, user-visible Codex task, never as a native SDD agent or subagent. The Orchestrator remains the sole coordinator; Luna receives one bounded implementation assignment and cannot plan the feature, select routing, coordinate native agents, or advance a gate.

At the beginning of each SDD cycle, obtain one explicit user decision on whether visible Luna tasks are authorized for that cycle and record `authorized`, `denied`, or `not answered`. Authorization expires when that cycle completes, is cancelled, or restarts. Never reuse authorization from an earlier cycle or infer it from implementation approval.

Current cycle authorization permits only creation of an eligible user-visible Luna task. It does not authorize product writes before the implementation gate, a delivery commit, integration, branch mutation, push, scope expansion, or acceptance of residual risk. Each such action still requires the governing gate and current authority.

## Eligibility Predicate

Route to Luna only when every condition is evidenced:

- the implementation gate in [Lifecycle and Gates](lifecycle-and-gates.md) is open and the approved artifact baseline is unchanged;
- current cycle authorization is `authorized`;
- the task is unequivocally low-complexity and isolated;
- every dependency is satisfied;
- owned paths are exclusive, non-overlapping, and safe to isolate;
- completion is independently verifiable with focused checks;
- the required tools and source context are available inside the isolated worktree;
- a self-contained brief can be supplied without relying on ignored or otherwise absent documentation;
- the expected value is proportionate to task-creation, worktree, review, and integration overhead; and
- adding the task keeps concurrent native Simple plus Luna executions at two or fewer.

If any condition is uncertain, do not use Luna. Route uncertain complexity or isolation to Main. Use native Simple when the work is otherwise simple but Luna is denied, unanswered, unavailable, lacks required tools or context, cannot be isolated safely, cannot receive an adequate brief, or does not justify its coordination cost.

## Visible Task and Isolated Delivery

Before creating an eligible Luna task, announce the bounded objective, classification evidence, owned paths, and use of the recorded current-cycle authorization. Do not ask for a repeated confirmation when that authorization is current; the announcement is not a new gate and does not broaden authority.

Create a separate user-visible task using GPT-5.6 Luna Max in a dedicated worktree based on the recorded revision. Never dispatch Luna through native subagent delegation. Keep its worktree and write scope separate from the shared native workspace and every concurrent assignment.

Supply the full Implementation Brief from [Contracts](contracts.md), including the approved criteria, exact owned and prohibited paths, completed dependencies, base revision and artifact approval identity, workspace condition, required checks, and Implementer Result delivery contract. Include all task-local context needed to act safely. Do not point Luna at planning material that is ignored, inaccessible, or absent from its worktree unless the required content is included directly in the brief.

After the implementation gate is open and current explicit authority permits the commit, require exactly one local delivery commit containing only the assigned delta. Do not push it. If the allowed correction round changes the delivery, amend or replace the isolated history so exactly one final local delivery commit remains.

## Review and Integration Gates

Send the isolated delivery commit, brief, base identity, exact diff, and verification evidence to an independent Reviewer before integration. Apply exactly one Reviewer status from [Contracts](contracts.md):

- `approved` makes the commit eligible for the separate manual integration gate but does not integrate or approve the shared result;
- `corrections required` permits one correction round in the same visible Luna task, followed by a fresh pre-integration review; and
- `conditionally verified` satisfies no gate and remains unintegrated until the missing check is resolved and reviewed.

After the first `corrections required` result, preserve the finding evidence and issue one bounded correction brief. If the fresh review returns a second `corrections required` result, preserve the isolated worktree, final commit, diffs, checks, and both reviews as non-authoritative evidence; never integrate that commit automatically or manually. Reassign the original approved task to Main. Main may inspect the failed Luna result but must implement and verify the assignment under the native contract rather than treating the failed commit as approved work.

For a pre-integration `approved` delivery, stop and obtain the explicit manual integration decision required for that exact commit and target baseline. A planning approval, implementation approval, Luna authorization, delivery commit, or Reviewer approval does not substitute for this gate. If the commit or target baseline changes, invalidate the integration decision and repeat the applicable review and gate.

Only Main may integrate after the Orchestrator confirms the exact pre-integration approval and manual integration gate. Main must preserve concurrent and user changes, resolve no conflict by discarding unrelated work, verify the combined state, and return exact integration evidence. Luna and the Orchestrator never merge, cherry-pick, rebase, or otherwise incorporate the delivery.

Commission a new independent post-integration review of the shared repository state. Recheck the approved delta, conflicts, changed paths, criteria, and combined checks; never reuse the isolated-delivery verdict. Route confirmed integration findings to Main under the native correction rules. Only a post-integration `approved` result allows the integrated Luna task to proceed toward convergence and final review.
