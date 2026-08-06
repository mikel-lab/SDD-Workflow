# Contracts

Use these ordered recipes for every role handoff. Keep each field present, concise, and evidence-based. Use `none` when a field has no entries so the shape remains explicit.

## Orchestrator Status

```text
state: <current normative lifecycle state>
transition: <proposed next state and triggering condition>
sources: <source, access method, evidence or limitation>
routing: <role or lane, task boundary, and evidence for the route>
gates: <planning review, frozen artifact set, exact approval, and validity>
blockers: <condition, evidence, impact, owner, and required resolution>
risks: <known risk, likelihood or impact, and mitigation>
next action: <single accountable action and required gate>
```

## Planner Result

```text
cycle_id: <generated cycle identity from sdd-cycle.json>
source_ids: <complete authorized source identifiers from the manifest>
artifact_directory: <exact selected package directory, relative to speckit_root>
artifact_reads: <every artifact path read in this action; none when no artifact was read>
artifacts: <resolved root plus complete generated artifact paths and purpose>
evidence: <source or repository evidence mapped to requirement or decision>
assumptions: <each assumption in the required four-line assumption format>
routing evidence: <complexity, isolation, dependencies, owned paths, and independent checks>
questions: <minimum material question, evidence reviewed, and why the answer is required>
changed paths: <exact SDD artifact paths written in this action, including .specify/feature.json when official speckit-specify created or updated it>
cycle_validation_command: <exact validate_cycle.py command with manifest, expected workspace, expected source, and applicable flags>
cycle_validation_result: <exit status plus concise stdout or stderr evidence>
blockers: <unresolved condition, impact, and required decision or dependency>
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
behavior: <criterion-to-observed-behavior mapping>
checks: <exact command or inspection and its result>
blockers: <condition, evidence, impact, and required next decision>
residual risk: <remaining risk, affected criterion, and mitigation or follow-up>
```

## Reviewer Result

```text
cycle_id: <cycle identity from the manifest supplied by the root chat>
source_ids: <complete authorized source identifiers from the manifest>
artifact_directory: <exact selected package directory supplied by the root chat>
artifact_reads: <every artifact path read in this action; none when no artifact was read>
scope: <artifact set, delivery, or integrated result reviewed plus baseline identity>
criterion evidence: <criterion-to-source, artifact, code, test, or observed-result mapping>
findings: <severity, affected criterion, evidence, and required correction>
commands: <exact read-only command or inspection and result>
cycle_validation_command: <exact validate_cycle.py command with manifest, expected workspace, expected source, and applicable flags>
cycle_validation_result: <exit status plus concise stdout or stderr evidence>
conditioned checks: <required check not completed, reason, affected criteria, and retry condition>
residual risk: <verified remaining risk and impact>
status: <approved | corrections required | conditionally verified>
```

Select exactly one Reviewer status:

- `approved`: all required evidence and checks for the reviewed scope are complete and no correction finding remains.
- `corrections required`: one or more findings require a change before approval.
- `conditionally verified`: an environmental or access condition prevented a required check from completing; list it under `conditioned checks`. This status records incomplete verification and satisfies no approval gate.
