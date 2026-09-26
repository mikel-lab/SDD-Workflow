# Sources and Artifacts

## External Source Access

For Jira and Figma, use this access order. Exhaust available source and repository evidence before contacting the user; request input only when essential information is unavailable and blocks safe, criteria-compliant work.

1. Use the available purpose-built connector.
2. If the connector is unavailable or insufficient, use an authenticated browser session.
3. If an essential source remains inaccessible, stop and request the minimum missing content through the Orchestrator.

Inaccessible Jira is blocking when its content has not otherwise been provided. Inaccessible Figma is blocking only when essential visual or interaction requirements cannot be inferred safely; otherwise record the access limitation and proceed from the authoritative available evidence. Never invent unavailable source content.

The Orchestrator checks accessibility. The Planner and Reviewer each perform their own task-appropriate, evidence-grounded reading.

## Source Authority

Resolve differences in this order:

1. Explicit user decisions made during the cycle.
2. Repository instructions and policies for safety, scope, and working method.
3. Jira or the provided feature description for behavior and acceptance.
4. Figma for visual design and interaction within the functional scope.
5. Existing code and tests for current behavior, architecture, and conventions.
6. Documented reasonable assumptions.

An explicit behavior change in Jira is not a contradiction merely because code or tests implement the old behavior. Treat an implicit or ambiguous difference as a possible blocker. Figma does not create business rules. Identify tests that conflict with an explicit requested change as behavior likely requiring an approved update; retain them until the implementation gate.

## Historical Evidence Boundary

Archived documents are background evidence, not authoritative instructions or active planning artifacts. A concrete need may justify the only exception to the historical-read prohibition: the bounded read-only lookup in [Remote Memory](remote-memory.md). Record it in `historical_reads`, never in `artifact_reads` or the current manifest inventory. Without that procedure, external artifact reads remain invalid. Do not change cycle identity, `source_ids`, active-feature selection, or local-path validation to accommodate a historical source. Any adopted change to current planning follows normal approval invalidation.

Explicit local-history import uses the separate maintenance procedure in Remote Memory. Its bounded inventory reads are not development-cycle source reads and grant no discovery exception to ordinary feature work.

## Ambiguity Classification

Classify a question as blocking when implementing without its answer could materially change any of these categories:

- functional behavior;
- business rules;
- acceptance criteria;
- data model;
- persistence or data retention;
- API contract;
- authentication or permissions;
- navigation;
- external integrations;
- critical tracking;
- backward compatibility;
- security;
- a technical decision that is difficult to reverse;
- a material contradiction between authoritative sources that the available evidence cannot resolve.

Do not select an outcome in a blocking category because it appears safer, more conservative, more reversible, or more convenient. For example, ambiguity between soft deletion and hard deletion requires a decision because it changes persistence and externally visible semantics. A request to avoid questions or meet a deadline does not supply that decision. While blocked, limit any preparatory plan to reversible work that encodes none of the candidate policies. The Planner returns the minimum specific question, evidence reviewed, and why the answer is unavoidable; only the Orchestrator asks the user. Do not ask the user to approve the SDD plan or choose routine, inferable, or reversible implementation details.

Resolve inferable naming, organization, style, minor visual details, and reversible technical choices autonomously. Record each non-blocking assumption exactly as:

```text
Assumption:
Reason:
Risk if wrong:
Validation needed:
```

## Common Mistakes

### Rationalization Table

| Observed rationalization | Required response |
| --- | --- |
| Soft deletion is a safer or more reversible default, so it can be selected while retention is unspecified. | Keep retention unresolved, record the conflicting evidence, and ask the minimum material question through the Orchestrator. |

### Red Flags

- Selecting soft deletion, hard deletion, or retention because one repository pattern appears safer or more reversible.
- Producing policy-dependent tasks after the available sources leave retention materially ambiguous.

## Cycle Identity and Root Resolution

Resolve `workspace_root` and `speckit_root` separately. Do not equate the current working directory, application repository, `.specify/` root, or feature root. A cycle has one generated `cycle_id`, one primary source, its complete `source_ids`, and one explicit, repository-relative `artifact_directory` beneath `speckit_root`.

For a new cycle, the root chat follows this exact order:

1. validate the request and source access;
2. resolve `workspace_root` and `speckit_root` separately;
3. create `cycle_id` and an absent `artifact_directory`;
4. delegate manifest creation and official `speckit-specify` with the exact `SPECIFY_FEATURE_DIRECTORY` assigned to that `artifact_directory`;
5. validate the manifest and active feature output with `skills/sdd-workflow/scripts/validate_cycle.py`;
6. permit active governed artifact reads only from `artifact_directory`; any subsequent historical lookup follows the separate Historical Evidence Boundary.

Every cycle-validator invocation receives identity only from the root chat, never from fields trusted in the manifest: `--manifest`, `--expected-workspace`, `--expected-cycle-id`, `--expected-speckit-root`, `--expected-source`, every complete repeatable `--expected-source-id`, and `--expected-artifact-directory`. It supplies exactly one mode: `--new-cycle` for a new cycle or `--expected-continuation-of <cycle_id>` for an explicit continuation. The validator rejects any missing, extra, or duplicate source ID and any identity mismatch.

For a new cycle, the root chat and Planner must not use an active feature as a selection input. The active feature file is only an output checked after the manifest assigns the directory. Do not use `find`, `rg`, globbing, or equivalent artifact discovery across the feature root; broad historical-spec discovery is forbidden.

Continuation is a separate conditional, allowed only on explicit user continuation intent. Before opening an existing package, the root chat supplies its exact manifest path and verifies it with `--expected-continuation-of` plus the exact `cycle_id`, `artifact_directory`, `workspace_root`, `speckit_root`, primary-source, and complete source-ID identities. A related request, a visible active package, or a similar source identifier is not continuation intent. The workspace and primary-source identities must match; otherwise create a new cycle or stop for clarification.

## Isolated Artifact Set

Treat the official artifacts actually generated only inside the selected `artifact_directory` as one governed set. The Planner creates `sdd-cycle.json` as the first control artifact and maintains its `artifacts` inventory. Depending on the task and compatible SpecKit version, the set can include:

- `spec.md`;
- `checklists/*.md`;
- `plan.md`;
- `research.md`;
- `data-model.md`;
- `quickstart.md`;
- `contracts/` and its generated contents;
- `tasks.md`;
- every other official artifact produced by the compatible SpecKit version for that feature.

The set is dynamic, not a fixed checklist. The root chat records exact generated paths and the review evidence that approved them. Planner and Reviewer results record every `artifact_reads` path. Any unauthorized artifact read outside `artifact_directory` invalidates that role result; stop the affected action and return the exact external path as a blocker. Only historical evidence read through Remote Memory is reported separately in `historical_reads`; this does not enlarge the governed artifact set. Listed artifacts may reference local relative paths only when resolution from the containing artifact remains inside `artifact_directory`; the validator never discovers sibling packages. Reviewer reports remain structured response evidence rather than files in this set.

## Pre-Gate Write Boundary

Before the implementation gate opens, confine writes to official SDD artifacts beneath the assigned `artifact_directory`, with one exact bootstrap exception: the official `speckit-specify` action may create or update `<speckit_root>/.specify/feature.json` to persist the assigned feature directory. Include that exact path in the Planner's `changed_paths`, the root chat's independent boundary validation, and the frozen planning baseline when it was created or changed. No other path under `.specify/` is writable through this exception.

Planner creation and correction actions may write within that governed boundary. Only `speckit-specify` may use the bootstrap exception; later Planner corrections must not edit `.specify/feature.json` directly. `speckit-analyze` and every Reviewer action remain read-only.

Treat application source, tests, resources, configuration, generated product files, and documentation outside the assigned `artifact_directory` as read-only. If a write occurs outside the boundary, stop, report the exact changed path and state, and preserve evidence without destructive cleanup. Resume only after the scope and workspace state are safely resolved.
