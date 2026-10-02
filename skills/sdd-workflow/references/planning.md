# Planning by Main
SpecKit owns official planning artifacts. Main invokes its skills directly; no Planner subagent is required. Read applicable installed skills completely and honor compatible hooks, user decisions and pre-gate write boundaries. Do not create a parallel Superpowers specification/plan.

## Ordered artifact workflow
1. Establish exact external cycle identity and an absent assigned artifact_directory. Create sdd-cycle.json first with identity and dynamic inventory. No historic/active-package discovery.
2. Read request, authorized sources and current code/tests enough to ground scope. Source authority and material questions follow Sources and Artifacts; no inaccessible content invented.
3. speckit-specify produces spec.md and checklists/requirements.md, using exact SPECIFY_FEATURE_DIRECTORY, and persists only .specify/feature.json as bootstrap. Validate identity/inventory before generated artifact reads.
4. speckit-clarify only for unavoidable material ambiguity; exhaust evidence/recovery first. User decisions are already authoritative; do not repeat resolved questions.
5. speckit-checklist generates requirement-quality checklists, not implementation test results.
6. speckit-plan produces plan.md, research.md, applicable data-model.md, contracts/ and quickstart.md. Skip only an artifact the compatible workflow finds inapplicable; no extra agent-context writes before the gate.
7. speckit-tasks generates dependency-ordered, traceable tasks with exact paths and observable checks. Mark parallel only when prerequisites are satisfied and exclusive ownership proves safety; a task does not dispatch an agent.
8. speckit-analyze is strictly read-only. Main applies bounded artifact corrections separately and revalidates. Evaluate all risk categories; commission planning review only if triggered/escalated. Freeze the current package after its applicable gates.

## Coverage repair
A required obligation omitted from tasks is repaired by Main under speckit-tasks, with source/criterion evidence. Revalidate/reclassify changed planning. Use speckit-converge only when its actual contract supports the executor (currently proven speckit-implement execution); native Main work does not by itself satisfy that prerequisite. A repair never imports optional improvements, silently changes acceptance or universally forces planning review.

## Evidence
Return Planning Evidence with artifact_reads, changed_paths, generated inventory, source/criterion provenance, non-blocking assumptions, exact validation commands/results and blockers. Keep historical_reads from remote-memory.md separate, never add them to source_ids/artifact inventory. Product source/tests/config/resources remain read-only before eligibility. Only exact per-cycle operational control output may additionally persist locally under Contracts.
