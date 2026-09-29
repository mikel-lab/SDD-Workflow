# Native SDD Agent Profile Maintenance Plan

## Scope and authority

Date: 2026-09-30. The user authorized this distribution update: Planner and Reviewer use GPT-6.1 Sol high; exactly two implementation profiles remain, GPT-6 Luna max by default and GPT-6.1 Sol medium for complex tasks. The root session recommendation and the existing autonomous cycle remain unchanged. This is the maintenance plan for the workflow repository, not an additional planning workflow or approval requirement for consumer tasks.

Keep the retained Simple and Main profile identifiers for compatibility while changing their routing responsibilities. Remove the third implementer profile and retire its exact installed path with backup. Preserve the sole root-chat coordinator, isolated SpecKit cycles, independent review, exact baseline validation, source boundaries, remote memory, and explicit user limits. Do not change official SpecKit skills, weaken runtime access controls, or claim a global installation or live model test from repository CI.

## Target profiles

| Owner | Model | Effort |
| --- | --- | --- |
| Root session recommendation | gpt-6-sol | medium |
| Planner | gpt-6.1-sol | high |
| Default implementer (Simple) | gpt-6-luna | max |
| Complex implementer (Main) | gpt-6.1-sol | medium |
| Reviewer | gpt-6.1-sol | high |

The root remains the invoking session, not a fifth TOML. All four configured roles use native delegation. There are exactly two implementation profiles. Preserve the existing instance ceilings of at most two concurrent Simple assignments and one Main assignment, with satisfied dependencies and exclusive ownership across every writer. A handoff between profiles must never duplicate an active assignment.

## Implementation sequence

### 1. Establish regression evidence

Update policy tests before implementation for the exact target model/effort matrix, four-agent inventory, two implementation profiles, default routing beyond trivial tasks, and absence of dispatch instructions for the retired profile. Preserve the existing root recommendation, autonomy, isolation, independent review, context controls, and recovery guards.

Run policy tests through GitHub Actions against the unchanged implementation. Record the tests-only commit and observed assertion failures in the PR, including their causes. This is structural regression evidence; it is not an observed failure of a model or a runtime behavioral experiment.

### 2. Update profiles and execution contracts

Set Planner and Reviewer to `gpt-6.1-sol` with `high` effort. Set Simple to `gpt-6-luna` with `max` effort and make it the default for approved, bounded work and ordinary corrections. Set Main to `gpt-6.1-sol` with `medium` effort and reserve it for evidenced complex work. Delete `agents/sdd-implementer-high.toml`. Update the canonical validator matrix at the same time.

Remove the former three-tier routing and every active instruction to dispatch the retired implementer. Keep both retained profiles native and governed by the common execution and verification contract. Default does not mean trivial-only, and complex does not authorize a higher effort than its configured medium value. An incomplete brief, unresolved dependency, or overlapping ownership must be corrected before dispatch, not hidden by a model change.

Update `SKILL.md`, role references, README, and the current design. Keep the root-session recommendation unchanged rather than claiming the skill configures the active session. Reclassify corrections by actual complexity: ordinary bounded fixes remain on Simple; complex corrections move to Main with recorded evidence and a safe state handoff.

### 3. Preserve automatic transitions and recovery

Use the initial task as authority for the in-scope cycle. Continue automatically after independent planning approval, successful validation, and freeze. Apply corrections, task-coverage repairs, re-reviews, verification handoffs, and internal profile selection without routine user approval. Preserve explicit plan-only, pause, cancellation, and narrower scope instructions.

Require all three elements before user attention: a necessary blocked action, exhausted relevant evidence and authorized safe recovery, and an indispensable decision, source, access, or authority only the user can provide. Ask before the affected action using the dedicated contract. A purely technical failure is reported with evidence instead of requesting a meaningless approval.

After three failed correction/review cycles for one underlying condition, diagnose and escalate internally. Continue only with a materially different evidenced recovery and bounded verification target; never rename a condition to restart the counter. Do not replace active agents because a wait times out. Escalate Simple to Main only for evidenced complexity; if Main is already assigned, improve diagnosis or the brief, or route a necessary planning correction, without inventing a third implementer or silently raising effort.

### 4. Preserve state without changing the approved package

Retain the operational Orchestrator Checkpoint in the existing contracts reference. Keep cycle identity, state, baseline, user decisions, active/completed assignments, dependencies, reviews, and next permitted transition recoverable in the root session. Do not add a consumer planning artifact or change the manifest schema.

Preserve literal Cycle Identity Handoff values, requested-versus-observed delegation metadata, supported history controls, neutral review briefs, and ownership on delta reviews. On recovery, check the current baseline and existing agents rather than restarting them.

### 5. Keep verification independent and executable

Retain read-only Reviewer behavior. Route write-producing checks after the implementation gate to the assigned implementer, then give exact command, output, exit status, and baseline evidence back to the Reviewer. The Reviewer independently assesses the evidence; a success assertion alone is insufficient.

A missing check remains incomplete verification. Before the gate, retain the existing product-write prohibition. Do not weaken sandbox settings or ask the user to waive required verification. Normal final-review corrections return to final review without a redundant intermediate gate.

### 6. Validate installation migration

The existing installer already backs up and replaces the complete managed skill directory. Remove the third implementer from the active agent list and add its exact former path to the retired list alongside the retired Orchestrator. Back up original bytes before deletion and leave unmanaged agents, including similarly named custom profiles, untouched.

Extend regression coverage for a five-to-four agent upgrade, exact backup contents, removal of the retired implementer, replacement of retained profiles, and dry-run reporting without writes. Fresh installs contain four agents, exactly two implementation profiles, and eight references. Preserve existing validation-before-write, interpreter compatibility, reinstall backup, and obsolete-reference removal checks.

Keep the exact distribution inventory synchronized at 26 files and eight direct references. Do not add CI workflows or change the cycle validator's identity, source, or manifest semantics.

### 7. Run full verification and publish evidence

Run these checks on the completed PR commit:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_delegation_policy.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
bash tests/test_install.sh
bash -n scripts/install.sh tests/test_install.sh
git diff --check
```

CI uses a read-only checkout, Python 3.11 or newer, and temporary installer destinations. It must not change the working tree. Record observed test counts and the exact passing run in the PR rather than copying historical results from another version. The optional official skill validator runs only when installed; its absence is not proof it passed.

Review the complete diff for contradictory model recommendations, stale third-profile routing, missing reference links, surviving manual gates, unsafe widening of authority, extra source writes by Reviewer, and changes to unrelated cycle checks. Keep branch publication distinct from merging into main or updating a user's installed skill.

## Verification boundaries

Repository policy tests assert shipped configuration and instruction contracts. Validator and installer tests execute their actual Python/Bash entrypoints in isolated fixtures. Neither these tests nor a green CI run demonstrates actual subagent selection, model quality, token cost, or long-context coordination.

A live Codex smoke test must later confirm effective model/effort, supported native delegation, no unnecessary parent history, automatic phase transitions, and escalation behavior on representative tasks. No such runtime experiment or active-user installation is asserted by this maintenance update.
