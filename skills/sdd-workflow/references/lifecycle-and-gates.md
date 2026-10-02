# Lifecycle and Gates

## States and eligibility
intake → planning → (planning_review when required) → implementation → verification → final_review → complete. planning_correction and implementation_correction are bounded loops; implementation_review is optional. blocked/cancelled and explicit pause never mean complete.

Planning requires source identity/access, complete coherent spec/plan/tasks, cycle validation and risk assessment. Low-risk resolved planning may freeze and enter implementation without independent planning review. Triggered/escalated planning_review must return approved on the exact current version before implementation. Conditionally verified is incomplete evidence and opens no gate.

## Required risk categories
Assess every category with evidence: auth/authorization; security-sensitive behavior; persistence/schema migrations; destructive/irreversible changes; public API/external contracts; critical infrastructure/deployment; significant architectural boundaries; cross-system consistency; data-loss/privacy-sensitive work. Derived planning review is required when any category is triggered or Main escalates; unresolved categories block eligibility until investigated/resolved. Main cannot bypass a trigger. Size, UI label, deadline or model are not evidence of low risk.

Late risk pauses affected continuation and requires planning review of that scope, including what was already written; preserve honest history. Changed planning/sources/technical scope invalidates affected baseline/eligibility and reevaluates risk. Normal coverage repair does not impose universal planning review. When review is required, bounded changes return as focused delta; material changes require full applicable review with same Reviewer.

## Independent review and corrections
Final_review always reconciles sources, intent, planning, tasks, code, tests and observed results, including read-only speckit-analyze, in one integrated action. Confirmed findings return to Main. Main fixes/verifies, and same Reviewer rechecks delta and impacted integrated coverage. Required work absent from tasks returns to Main planning/risk assessment; optional improvements remain outside scope.

Intermediate reviews are optional and purpose-specific. Pending findings/conditioned checks block dependent scope, not unrelated work whose eligibility/ownership remain valid. They never replace required planning or final review.

A Reviewer timeout/compaction is not evidence of loss. Proven unavailability permits recorded replacement after active owner state is resolved; replacement independently reviews full pending scope and previous findings. Main cannot approve itself. A valid prior planning approval is not invalidated merely because Reviewer changes.

## Completion and evidence
Complete requires current independent final approved, matching actual planning/result versions, complete current criterion verification, resolved findings, delivered tasks and no active writer or conditioned check. A stored approval of older bytes is insufficient. Validators recalculate real identities and check eligibility; Main retains evidence before claiming completion. Scope/traceability/verification are universal.

## Autonomous execution and user attention
The request authorizes in-scope planning/execution/corrections unless limited. No acceptance phrase or routine plan/correction/model approval. Exhaust accessible evidence/safe recovery first; ask only when an essential blocked action requires user-owned input. Never lower criteria, accept risk, publish/merge/deploy or weaken access controls without authority. Repeated unchanged failures call for diagnosis and a different evidenced recovery, not automatic gate approval or a new confirmation.

## Remote Archive at Closure
After approved final verdict and final validation, perform configured authorized archival in the same session under remote-memory.md. Report archive_status separately; pending archive failure does not change the final Reviewer verdict. Preserve local files when configuration/access/verification/cleanup authority is absent. Closed-cycle cleanup never edits live frozen planning or tracked files without separately authorized migration.
