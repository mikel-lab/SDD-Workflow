# Native GPT-6 SDD Maintenance Plan

## Scope and authority

Date: 2026-09-24. The user authorized this distribution update: use the proposed native GPT-6 profiles, remove the obsolete external execution mechanism completely, and make the SDD cycle automatic except for unavoidable user-owned blockers. This is the maintenance plan for the workflow repository, not an additional planning workflow or approval requirement for consumer tasks.

Preserve the five-role architecture, sole root-chat coordinator, isolated SpecKit cycles, independent review, exact baseline validation, source boundaries, and explicit user limits. Do not change official SpecKit skills, weaken runtime access controls, or claim a global installation or live model test from repository CI.

## Target profiles

| Owner | Model | Effort |
| --- | --- | --- |
| Root session recommendation | gpt-6-sol | medium |
| Planner | gpt-6-sol | high |
| Main | gpt-6-sol | medium |
| High | gpt-6-sol | high |
| Simple | gpt-6-luna | high |
| Reviewer | gpt-6-sol | high |

The root remains the invoking session, not a sixth TOML. All configured roles use native delegation. Main and High remain mutually exclusive; at most two Simple assignments may execute concurrently with exclusive ownership across every writer.

## Implementation sequence

### 1. Establish regression evidence

Add policy tests before implementation for the target model matrix, native-only inventory, root recommendation, explicit autonomy predicate, internal escalation, no recursive delegation, recoverable coordinator checkpoint, and read-only verification handoff. Keep existing isolation and review guards. Replace obsolete tests for the removed execution contract with guards against its reintroduction.

Run policy tests through GitHub Actions against the unchanged implementation. The initial tests-only commit recorded nine expected failures across 25 policy tests. This is structural regression evidence; it is not an observed failure of a model or a runtime behavioral experiment.

### 2. Update profiles and execution contracts

Update the three implementer profiles, preserve Planner and Reviewer model settings, and align all five instruction bodies with autonomous in-scope execution and root-only delegation. Update the canonical validator matrix at the same time.

Remove the obsolete external reference file and every corresponding instruction, eligibility rule, integration stage, model-specific review, and documentation reference. Do not replace it with another external execution mechanism. Native Simple handles eligible bounded work under the common contract.

Update `SKILL.md`, role references, README, and the current design. Use an explicit root-session recommendation rather than claiming the skill configures the active session.

### 3. Define automatic transitions and recovery

Use the initial task as authority for the in-scope cycle. Continue automatically after independent planning approval, successful validation, and freeze. Apply corrections, task-coverage repairs, re-reviews, verification handoffs, and internal profile selection without routine user approval. Preserve explicit plan-only, pause, cancellation, and narrower scope instructions.

Require all three elements before user attention: a necessary blocked action, exhausted relevant evidence and authorized safe recovery, and an indispensable decision, source, access, or authority only the user can provide. Ask before the affected action using the dedicated contract. A purely technical failure is reported with evidence instead of requesting a meaningless approval.

After three failed correction/review cycles for one underlying condition, diagnose and escalate internally. Continue only with a materially different evidenced recovery and bounded verification target; never rename a condition to restart the counter. Do not replace active agents because a wait times out.

### 4. Preserve state without changing the approved package

Add the operational Orchestrator Checkpoint to the existing contracts reference. Keep cycle identity, state, baseline, user decisions, active/completed assignments, dependencies, reviews, and next permitted transition recoverable in the root session. Do not add a consumer planning artifact or change the manifest schema.

Preserve literal Cycle Identity Handoff values, requested-versus-observed delegation metadata, supported history controls, neutral review briefs, and ownership on delta reviews. On recovery, check the current baseline and existing agents rather than restarting them.

### 5. Keep verification independent and executable

Retain read-only Reviewer behavior. Route write-producing checks after the implementation gate to the assigned implementer, then give exact command, output, exit status, and baseline evidence back to the Reviewer. The Reviewer independently assesses the evidence; a success assertion alone is insufficient.

A missing check remains incomplete verification. Before the gate, retain the existing product-write prohibition. Do not weaken sandbox settings or ask the user to waive required verification. Normal final-review corrections return to final review without a redundant intermediate gate.

### 6. Validate installation migration

The existing installer already backs up and replaces the complete managed skill directory. Add regression coverage proving an obsolete managed reference is absent after upgrade and its original bytes remain in the backup. Confirm dry-run performs no removal, fresh installs contain five agents and the current reference set, and unmanaged agents remain unchanged.

Keep the exact distribution inventory synchronized: remove one reference and add the CI workflow, leaving 25 files and seven direct references. Do not change the cycle validator's identity, source, or manifest semantics.

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

Review the complete diff for contradictory model recommendations, missing reference links, surviving manual gates, unsafe widening of authority, extra source writes by Reviewer, and changes to unrelated cycle checks. Keep branch publication distinct from merging into main or updating a user's installed skill.

## Verification boundaries

Repository policy tests assert shipped configuration and instruction contracts. Validator and installer tests execute their actual Python/Bash entrypoints in isolated fixtures. Neither these tests nor a green CI run demonstrates actual subagent selection, model quality, token cost, or long-context coordination.

A live Codex smoke test must later confirm effective model/effort, supported native delegation, no unnecessary parent history, automatic phase transitions, and escalation behavior on representative tasks. No such runtime experiment or active-user installation is asserted by this maintenance update.
