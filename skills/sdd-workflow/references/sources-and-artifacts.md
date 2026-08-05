# Sources and Artifacts

## External Source Access

For Jira and Figma, use this access order:

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

Do not select an outcome in a blocking category because it appears safer, more conservative, more reversible, or more convenient. For example, ambiguity between soft deletion and hard deletion requires a decision because it changes persistence and externally visible semantics. A request to avoid questions or meet a deadline does not supply that decision. While blocked, limit any preparatory plan to reversible work that encodes none of the candidate policies. The Planner returns the minimum specific question, the evidence reviewed, and why the answer is necessary; only the Orchestrator asks the user.

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

## Dynamic SpecKit Root

Use the installed SpecKit skills and utilities to locate the repository's `.specify/` root and resolve the active feature artifact directory. Search according to those installed utilities; do not equate the current working directory with the repository or feature root. Record the resolved root and every artifact path. If root or active-feature resolution is missing or ambiguous, stop before writing and report the blocker.

## Dynamic Artifact Set

Treat the official artifacts actually generated for the active feature as one governed set. Depending on the task and compatible SpecKit version, it can include:

- `spec.md`;
- `checklists/*.md`;
- `plan.md`;
- `research.md`;
- `data-model.md`;
- `quickstart.md`;
- `contracts/` and its generated contents;
- `tasks.md`;
- every other official artifact produced by the compatible SpecKit version for that feature.

The set is dynamic, not a fixed checklist. The Orchestrator records exact generated paths and the review evidence that approved them. Reviewer reports remain structured response evidence rather than files in this set.

## Pre-Gate Write Boundary

Before the implementation gate opens, confine writes to official SDD artifacts beneath the resolved active feature artifact directory, with one exact bootstrap exception: the official `speckit-specify` action may create or update `<repository-root>/.specify/feature.json` to persist the resolved active feature directory. Include that exact path in the Planner's `changed_paths`, the Orchestrator's independent boundary validation, and the frozen planning baseline when it was created or changed. No other path under `.specify/` is writable through this exception.

Planner creation and correction actions may write within that governed boundary. Only `speckit-specify` may use the bootstrap exception; later Planner corrections must not edit `.specify/feature.json` directly. `speckit-analyze` and every Reviewer action remain read-only.

Treat application source, tests, resources, configuration, generated product files, and documentation outside the resolved SDD artifact directory as read-only. If a write occurs outside the boundary, stop, report the exact changed path and state, and preserve evidence without destructive cleanup. Resume only after the scope and workspace state are safely resolved.
