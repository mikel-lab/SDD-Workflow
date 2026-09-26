# Contracts

Use these ordered recipes for every role handoff. Keep each field present, concise, and evidence-based. Use `none` when a field has no entries so the shape remains explicit.

## Cycle Identity Handoff

Create this block once from root-owned values and reuse it byte for byte for every Planner and Reviewer action. Values are literal and must not be abbreviated, summarized, converted to labels, or reconstructed from the manifest. Keep `artifact_directory` relative to `speckit_root`.

```text
manifest: <exact absolute sdd-cycle.json path, or pending before first creation>
cycle_id: <exact root-generated identity>
workspace_root: <exact absolute workspace root>
speckit_root: <exact absolute SpecKit root>
primary_source: <exact primary source identifier>
source_ids: <complete ordered list of exact literal source identifiers>
artifact_directory: <exact directory relative to speckit_root>
identity_mode: <--new-cycle | --expected-continuation-of exact-cycle-id>
cycle_validation_command: <exact command using every value above and each literal --expected-source-id>
```

The block must not be abbreviated in a retry or follow-up. Add action-specific scope and evidence after it; do not repeat the skill body or role instructions in the handoff.

## Orchestrator Status

```text
state: <current normative lifecycle state>
transition: <proposed next state and triggering condition>
sources: <source, access method, evidence or limitation>
routing: <native role, task boundary, and evidence for the route>
delegation: <native agent ID and reference to its latest Delegation Record, or none>
gates: <independent planning review, successful cycle validation, frozen artifact baseline, and validity>
blockers: <condition, evidence, impact, owner, and required resolution>
user_attention: <none, or reference to an unavoidable User Attention Request>
risks: <known risk, likelihood or impact, and mitigation>
next action: <single accountable action and required gate>
```

## Orchestrator Checkpoint

Maintain this compact operational record in the root chat, with session-scoped runtime checkpoint storage when available. It is not a governed planning artifact: do not add it to `sdd-cycle.json`, change the approved artifact set, or write it into a consumer's planning package. Keep exact references to evidence rather than duplicating full transcripts.

```text
cycle_id: <exact current cycle identity and reference to its literal Cycle Identity Handoff>
state: <current lifecycle state>
baseline: <approved artifact identities, repository revision/diff identity, and review evidence>
decisions: <explicit user decisions, scope limits, pauses, and documented assumptions>
assignments: <task IDs, active/completed/blocked status, owning agent IDs, exact owned paths, and result references>
dependencies: <completed and pending prerequisites, unavailable essential sources or tools>
reviews: <review owner and verdict, open findings, conditioned checks, attempt counts, and recovery evidence>
next_transition: <next allowed state, its remaining conditions, and accountable action>
```

Refresh after meaningful state changes and before compaction when possible. Recover the preserved identity and compare current baseline and agent status before resuming. Do not redispatch completed or still-active assignments merely because context was compacted. Missing state is recovered from authorized cycle evidence; it is not permission to guess a gate verdict or rediscover unrelated packages.

## Historical Read Record

Use only after a justified read under [Remote Memory](remote-memory.md); otherwise report `historical_reads: none`. Keep this record in role results and the operational checkpoint, not as a new governed artifact. Do not add historical reads to `source_ids`, `artifact_reads`, the manifest inventory, or the literal Cycle Identity Handoff.

```text
question: <concrete unresolved question and why current evidence is insufficient>
repository: <authorized documentation repository>
revision: <exact remote commit read>
paths: <exact index and document paths read at that revision>
conclusion: <relevant finding, applicability check, or unresolved limitation>
```

Reference the record in downstream briefs rather than copying documents. Separate records may identify different pinned revisions. An adopted planning change still follows the ordinary Planner and review contracts. Index reads performed solely to update the catalog at closure are administrative publication reads, not historical evidence for the task. Explicit migration inventories are recorded separately as `import_inventory`.

## Archive Result

At closure or after explicit import, report the storage outcome independently of the development-cycle verdict. Do not create a new approval gate.

```text
archive_status: <stored | partial | pending | not_configured>
archive_location: <repository, exact remote commit, archive ID and index path; or none>
verification: <inventory/hash and index read-back evidence; or exact missing check>
local_cleanup: <exact deleted or retained paths and reason; never implied>
```

## User Attention Request

Use only when the unavoidable-user-owned-blocker predicate in [Lifecycle and Gates](lifecycle-and-gates.md) is satisfied. Internal role blockers and routine corrections use the normal result contracts instead. Do not ask for a plan approval or permission already supplied.

```text
blocker: <necessary action that cannot safely proceed>
evidence: <exact source, observed failure, or unresolved material contradiction>
attempted_recovery: <relevant source checks, safe alternatives, and internal corrections already tried>
why_user: <why existing authority/evidence cannot resolve it and why the user's input is indispensable>
required_input: <smallest specific decision, essential content, access, or authority needed>
affected_scope: <work paused before the affected action and independent work that may still proceed>
```

Record the answer as a scoped cycle decision, revalidate any changed baseline, and resume automatically. Do not interpret an answer as approval of unrelated publishing, scope expansion, or residual risk.

## Delegation Record

Keep one compact record per native agent in the root chat, linked from Orchestrator Status. Fill requested values before spawning and update observed values only when runtime evidence becomes available. Reuse its agent ID on follow-ups rather than repeating the record. This is not a new governed artifact and must not change the manifest, approved baseline, or Cycle Identity Handoff. Do not create another agent or review to gather this metadata.

```text
agent_id: <runtime agent identifier; pending before spawn; not verified if unavailable>
requested_role: <exact canonical native SDD role>
requested_model: <model from the selected canonical TOML>
requested_effort: <effort from the selected canonical TOML>
selection_evidence: <supported tool/profile arguments actually used, or blocking limitation>
context_policy: <none | recent | all | not verified>
context_argument: <exact supported argument and value used, or not verified>
context_reason: <self-contained brief, or task-specific need and boundary check for inherited history>
effective_model: <runtime-observed value, or not verified>
effective_effort: <runtime-observed value, or not verified>
runtime_evidence: <agent-linked metadata source and observed values, or not verified>
configuration_status: <verified | not verified | mismatch | blocked>
```

`verified` requires matching runtime evidence for the effective model and effort and a supported context selection. `not verified` identifies missing observability, not permission to invent evidence. A confirmed contrary value takes `mismatch` precedence even when other values are unavailable; `blocked` records inability to apply the required profile or maintain the source boundary before delegation. These are configuration diagnostics, not Reviewer verdicts or lifecycle states; they neither grant nor replace any approval. Keep the actual blocker in Orchestrator Status when one exists. Task-specific briefs and every required literal identity field remain mandatory even when history is inherited.

## Planner Result

```text
cycle_id: <generated cycle identity from sdd-cycle.json>
source_ids: <complete authorized source identifiers from the manifest>
artifact_directory: <exact selected package directory, relative to speckit_root>
artifact_reads: <every active governed artifact path read in this action; none when no artifact was read>
historical_reads: <none, or exact Historical Read Records for bounded remote lookups>
artifacts: <resolved root plus complete generated artifact paths and purpose>
evidence: <source or repository evidence mapped to requirement or decision>
assumptions: <each assumption in the required four-line assumption format>
routing evidence: <complexity, isolation, dependencies, owned paths, and independent checks>
questions: <none, or unavoidable material question, evidence reviewed, and why only user input can resolve it>
changed_paths: <exact SDD artifact paths written in this action, including .specify/feature.json when official speckit-specify created or updated it>
cycle_validation_command: <exact validate_cycle.py command with manifest, expected workspace, cycle ID, SpecKit root, primary source, each repeatable source ID, artifact directory, and exactly one new-cycle or expected-continuation identity>
cycle_validation_result: <exit status plus concise stdout or stderr evidence>
blockers: <unresolved condition, evidence, recovery tried, impact, and accountable next action>
```

## Implementation Brief

```text
objective: <bounded behavior or outcome from an approved task>
criteria: <applicable approved criterion identifiers and expected evidence>
owned paths: <exclusive exact paths or path boundaries permitted for this assignment>
prohibited paths: <exact paths or boundaries reserved for others or outside scope>
dependencies: <completed prerequisites and permitted interfaces>
base state: <branch, worktree or revision, artifact approval identity, and workspace condition>
checks: <tests, builds, lint, inspection, and expected result>
delivery contract: <Implementer Result fields, evidence location, and handoff recipient>
```

## Implementer Result

```text
changed paths: <exact paths changed by this delivery>
historical_reads: <none, or exact Historical Read Records for bounded remote lookups>
behavior: <criterion-to-observed-behavior mapping>
checks: <exact command or inspection, exit status/output evidence, and checked baseline>
blockers: <condition, evidence, recovery tried, impact, and accountable next action>
residual risk: <remaining risk, affected criterion, and mitigation or follow-up>
```

## Reviewer Result

```text
cycle_id: <cycle identity from the manifest supplied by the root chat>
source_ids: <complete authorized source identifiers from the manifest>
artifact_directory: <exact selected package directory supplied by the root chat>
artifact_reads: <every active governed artifact path read in this action; none when no artifact was read>
historical_reads: <none, or exact Historical Read Records for bounded remote lookups>
changed_paths: <exact paths changed by the reviewed delivery, or none for a planning-package review>
scope: <artifact set, delivery, or integrated result reviewed plus baseline identity>
criterion evidence: <criterion-to-source, artifact, code, test, or observed-result mapping>
findings: <severity, affected criterion, evidence, and required correction>
commands: <exact read-only command or inspection and result>
cycle_validation_command: <exact validate_cycle.py command with manifest, expected workspace, cycle ID, SpecKit root, primary source, each repeatable source ID, artifact directory, and exactly one new-cycle or expected-continuation identity>
cycle_validation_result: <exit status plus concise stdout or stderr evidence>
conditioned checks: <required check not completed, reason, affected criteria, accountable role, and retry condition>
residual risk: <verified remaining risk and impact>
status: <approved | corrections required | conditionally verified>
```

Select exactly one Reviewer status:

- `approved`: all required evidence and checks for the reviewed scope are complete and no correction finding remains. This is the Reviewer's verdict, not a user confirmation.
- `corrections required`: one or more findings require a change before approval; the root chat routes bounded correction automatically.
- `conditionally verified`: an environmental or access condition prevented a required check from completing; list it under `conditioned checks`. This status records incomplete verification and satisfies no approval gate. Resolve checks internally whenever the authorized runtime permits them.
