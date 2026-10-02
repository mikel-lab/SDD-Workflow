---
name: sdd-workflow
description: Use when a software change needs a governed Specification-Driven Development cycle, when preparing a PR containing SDD work, or when explicitly setting up remote SDD storage or migrating local artifacts, including tracked files.
---

# SDD Workflow

## Authority and invariants
The invoking Main owns understand, specify, plan, implement and verify. This skill imposes no model or reasoning-effort requirement on Main and cannot reconfigure its session. Only independent Reviewer is structurally mandatory; no Planner or implementer profile is required. Only Main dispatches agents, and recursive delegation is disabled by default.

Preserve eight invariants: specification before implementation; plan before implementation; requirement → specification → tasks/changes → verification traceability; implementation verification; independent final review for every cycle; findings return to Main for correction and the same Reviewer rechecks the delta; evidence before completion; scope protection.

The request authorizes in-scope work unless explicitly limited, paused or cancelled. Do not ask for plan acceptance, model choice, routine corrections or an approval phrase. Attempt safe authorized recovery first; ask the user only for an unavoidable decision/access/authority they alone can supply. Do not publish, deploy, merge, broaden scope or weaken permissions without applicable authority.

## Core sequence
1. Intake: identify request/sources and exact workspace/SpecKit roots; select a new isolated cycle ID/directory without discovering historical packages. Follow [Sources and Artifacts](references/sources-and-artifacts.md).
2. Main invokes official SpecKit specification, necessary clarification, checklist, plan and tasks under [Planning](references/planning.md). Create sdd-cycle.json first, inventory all generated artifacts, validate external identity, and run read-only speckit-analyze. Product files remain read-only until implementation eligible.
3. Evaluate all nine risk categories and resolve uncertainty. Planning review is mandatory only for triggered risks or Main escalation, under [Lifecycle and Gates](references/lifecycle-and-gates.md). A triggered review cannot be waived. Low-risk planning proceeds after validation/freeze without planning review.
4. Freeze exact planning bytes and record eligibility. Main implements and verifies coherent dependency-ready work under [Execution](references/execution.md); delegate additional work only for concrete benefit, with exclusive writer paths including Main. The [Main](references/main.md) procedure owns state, dispatch and recovery.
5. Obtain one independent integrated final review under [Reviewer](references/reviewer.md), including read-only speckit-analyze and intent/artifact/code/evidence reconciliation. Main corrects findings, verifies affected work and returns to the same Reviewer. Review replacement needs demonstrated unavailability and full pending-scope review; timeout/compaction alone never justify it.
6. Complete only with current independent approved final verdict, required verification and no pending findings/conditioned checks. Validate current identities and gates; record evidence and residual risks. Report any archival limitation separately.

## Operational evidence and validators
Use [Contracts](references/contracts.md) and the shipped schemas/operational-state.schema.json for local .sdd/cycles/<cycle_id>/state.json, immutable events and evidence, separate from frozen planning. Main alone writes control records. Keep original Reviewer results and honest requested/observed runtime configuration; missing telemetry alone adds no gate. Local persistence does not imply a commit or external publication.

scripts/validate_cycle.py checks external cycle identity, isolation, inventory and references. scripts/validate_state.py is read-only: capture planning/product versions, inspect state/history/evidence and reject ineligible transitions, unresolved risk, stale versions or ownership overlap. Run identity validation at planning completion, before required review/freeze/implementation and final reconciliation; run state validation before affected transitions/assignments and recovery. Recalculate actual file identities; never trust a declared approved label alone. Validators neither intercept all tools nor authenticate reviewers or semantic dependency coverage: independent inspection remains required.

## Remote Memory (Conditional)
The project may configure an authorized documentation destination in .sdd/config.json. Do not read the remote index at intake or routinely load history. Read [Remote Memory](references/remote-memory.md) only for configured closure archival, a justified bounded lookup, explicit storage/import or tracked-artifact migration, or authorized PR preparation. Setup/reference-only administrative operations need no development cycle. Missing configuration/access preserves local evidence; archive_status is separate from task verification. Routine cleanup preserves tracked/active/user files. Do not configure new destinations, import history, create PRs or add archive automation implicitly.

## Quick Reference
| Action | Required guidance |
| --- | --- |
| Main intake/planning | Sources and Artifacts; Planning; Lifecycle and Gates; Contracts |
| Main execution/delegation/recovery | Main; Execution; Lifecycle and Gates; Contracts |
| Independent Reviewer | Reviewer; Sources and Artifacts; Lifecycle and Gates; Contracts |

Read applicable references completely before acting. Official SpecKit is the planning artifact authority; compatible Superpowers execution practices are conditional, detailed in Execution. They cannot add a competing planning lifecycle, user approval gate or self-review fallback.
