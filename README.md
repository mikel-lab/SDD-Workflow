# SDD Workflow

`sdd-workflow` is a portable Codex skill for an autonomous, governed
Specification-Driven Development lifecycle. The invoking root chat coordinates
planning, independent review, validated implementation, corrections, and final
verification. SpecKit owns the planning artifacts; this package owns workflow
rules and native role definitions.

## Roles

| Role | Model | Effort | Purpose |
| --- | --- | --- | --- |
| Root chat / Orchestrator | `gpt-6-sol` | `medium` | Owns coordination, lifecycle, and user contact. |
| `sdd-planner` | `gpt-6-sol` | `high` | Creates and corrects the planning artifact set. |
| `sdd-implementer-main` | `gpt-6-sol` | `medium` | Delivers non-trivial work, integrations, and Simple corrections. |
| `sdd-implementer-high` | `gpt-6-sol` | `high` | Replaces Main for evidenced complex work. |
| `sdd-implementer-simple` | `gpt-6-luna` | `high` | Delivers isolated, dependency-ready work with direct checks. |
| `sdd-reviewer` | `gpt-6-sol` | `high` | Independently reviews planning, risk-triggered batches, and final output. |

There are five configured native agents. The root chat is the sole coordinator,
not a sixth agent: do not dispatch `sdd-orchestrator`. Its model is a session
recommendation; the skill cannot switch the active root model merely by naming
it. The distribution validator enforces the five TOML profiles.

Simple describes the task's complexity, not a requirement for low effort.
Use it for well-specified, isolated changes following existing patterns. Use Main
when non-trivial engineering decisions remain or isolation is uncertain. High
replaces Main, never runs alongside it. Up to two Simple assignments may run
concurrently when dependencies and exclusive paths permit it. All writers must
have non-overlapping ownership. Only the root chat dispatches agents.

## Automatic execution

A task submitted to `sdd-workflow` authorizes the complete in-scope cycle unless
the user explicitly requests planning only, pauses, cancels, or imposes a narrower
limit. The normal path is:

```text
Intake -> Planner -> independent planning review
       -> successful cycle validation and frozen baseline
       -> native implementation and focused verification
       -> independent final review with speckit-analyze -> complete
```

Implementation begins automatically after the independent Reviewer returns
`approved`, cycle validation passes, and the exact reviewed baseline is frozen.
The workflow does not ask the user to approve the plan or write a confirmation
phrase. Corrections, verification handoffs, task-coverage repairs, re-reviews, and
internal routing also proceed automatically within the requested scope.

An internal `approved` verdict is still required; incomplete verification is not
approval. Changed planning artifacts invalidate their baseline and return through
review and validation before implementation resumes automatically. Normal batches
use implementer checks until final review; intermediate independent reviews apply
only to the documented risk categories.

The root chat requests user attention only for an unavoidable blocker: a necessary
action cannot safely proceed, available evidence and authorized recovery cannot
resolve it, and an essential decision, source, access, or authority must come from
the user. It asks before the affected action and identifies the smallest required
input. Retry counts and routine technical choices do not create approval gates.
After three unsuccessful cycles for the same condition, diagnose and escalate
internally instead of repeating the same failing strategy. Report an irreducible
technical blocker honestly when the user has no actionable decision.

Autonomy preserves scope, independent verification, source isolation, explicit
user constraints, access controls, and sandbox protections. It does not silently
authorize publication, deployment, destructive changes, or acceptance of risk.
Existing authority for the same action and scope is not requested again.

## Efficient delegation

The [spawn policy](skills/sdd-workflow/references/orchestrator.md#agent-spawn-policy)
requires supported runtime controls to select the actual configured role.
Writing a model name inside a task prompt is not configuration.

Self-contained assignments receive a complete bounded brief without parent
history. Inspect the exposed tool schema: use `fork_context=false` where
supported or `fork_turns="none"` on that interface, never both. Inherit history
only for a recorded task-specific need within the cycle boundary. Keep the same
Reviewer for bounded delta corrections. Do not interrupt active agents merely
because a wait timed out or to request routine progress.

The [Delegation Record](skills/sdd-workflow/references/contracts.md#delegation-record)
separates requested settings from runtime-observed model and effort. Unavailable
metadata is `not verified`; it is not guessed and does not create an approval
gate. Confirmed mismatches or unsupported required profiles are reported and
recovered through supported controls, not silently substituted.

The [Orchestrator Checkpoint](skills/sdd-workflow/references/contracts.md#orchestrator-checkpoint)
keeps the current cycle, baseline, decisions, assignments, dependencies, reviews,
and next transition recoverable in the root chat or session-scoped runtime
storage. It does not modify frozen planning artifacts. After compaction, recover
evidence and existing owners rather than redispatching completed or active work.

These are workflow instructions, not a runtime interceptor. The regression tests
check their presence and contracts, not a live Codex execution or usage savings.
Verify actual model selection, effort, context handling, and runtime behavior in
the installed client. No cost or quality improvement is claimed from static tests.

## Remote documentation memory

Each project can keep its SDD history in a separate private repository, without
cloning that repository onto the developer's computer. The running agent uploads
the current task's artifacts and updates a remote `INDEX.md` at task closure.
There are no new GitHub Actions, hooks, PR checks, merge synchronization or services.

The only permanent project-side pointer is `.sdd/config.json`. Example:

```json
{
  "schema_version": 1,
  "project_id": "example-app",
  "source_repository": "example/app",
  "documentation": {
    "repository": "example/app-knowledge",
    "branch": "main",
    "root": ".",
    "index": "INDEX.md",
    "cleanup_local_after_verification": false
  }
}
```

Choose and authorize the real destination once per project, and provide the agent
with authenticated GitHub read/write access. No credentials belong in this file.
Set the optional cleanup flag to true only when authorizing deletion of verified,
closed-cycle local copies. Upload or index failures retain local files. The agent
verifies remote file contents and the catalog before claiming successful archival.

The remote index is a short catalog, not a startup reading list. Agents consult it
only to answer a concrete question that current sources do not resolve, then read
selected documents at a pinned revision. Historical reads are recorded separately
and never reactivate old cycles or override current requirements. Reading the index
to append a new archive entry or recover an exact PR reference is administrative
work, not historical task context; it does not authorize reading old specs.

Existing untracked local SDD folders can be imported in a separately requested,
bounded migration, one project/package at a time. Originals are preserved; unknown
integration state is explicitly unverified. Active tasks, configuration and
unverified local copies are not removed. No Git history rewrite is needed.

For already versioned artifacts, explicitly request a **tracked-artifact migration**.
The agent verifies the remote archive before previewing bounded untracking, checks
actual build dependencies (including Xcode resources when applicable), and adds
narrow ignore rules. Routine cleanup and its config flag do not grant this authority.
Installing or invoking the workflow does not migrate or untrack files automatically.

When already authorized to prepare a PR containing SDD work, include one direct
commit-pinned package link per cycle and its documented code identity. Do not paste
every artifact or link only the global index. Before archival or when evidence is
missing/stale, report pending status or the limitation; no new check, merge gate
or automatic PR creation is added.

Keep the procedure here rather than duplicating it in each project. An optional
brief referral in the project's `AGENTS.md` can cover a later session:

> For SDD work, follow `sdd-workflow` for archival and PR documentation references,
> including PR preparation in a later session. The destination is `.sdd/config.json`.
> Run tracked-artifact migration only on an explicit maintenance request.

This is suggested project guidance, not an automatic edit of consumer `AGENTS.md`.

See [Remote Memory](skills/sdd-workflow/references/remote-memory.md) for setup,
publication, lookup, import, tracked migration, PR references and cleanup contracts.
Installing the skill does not configure
consumer projects, create their documentation repositories, or migrate
local history; these require their own authorized setup/import request. This is
an agent-operated protocol, not a runtime interceptor or a bundled publishing
service. The policy regressions do not prove live uploads or model compliance.

## Requirements

- Bash and Python 3.11 or newer, including `tomllib`; use `SDD_PYTHON` to select a
  compatible interpreter explicitly.
- PyYAML when the optional official skill validator is available.
- Installed SpecKit skills: `speckit-specify`, `speckit-clarify`,
  `speckit-checklist`, `speckit-plan`, `speckit-tasks`, and `speckit-analyze`.
- A Codex runtime that exposes the configured native roles and supported model,
  effort, and delegation controls. Missing effective metadata alone is not proof
  of incompatibility.

`speckit-converge` is conditional. Use it only when `speckit-implement` executed
the current task list or a future converge contract explicitly supports the
actual executor. Native SDD deliveries normally repair missing approved-scope
task coverage through the `speckit-tasks` contract.

The applicable Superpowers practices remain required when their conditions occur:
`test-driven-development`, `systematic-debugging`, `receiving-code-review`,
`verification-before-completion`, and `dispatching-parallel-agents`. They do not
create a competing planning workflow, recursive delegation, or another user gate.

For source-backed requests, provide a Jira connector or authenticated browser
session when Jira is authoritative. Provide Figma access when visual or
interaction evidence is essential. An inaccessible optional Figma source is
recorded as a limitation rather than invented or treated as an automatic blocker.

## Validate

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py
```

The validator checks the exact 27-file distribution, all five canonical agent
TOMLs, the skill frontmatter, eight direct skill references, full-tree
portability, and the optional official skill validator when resolvable.

## Install and update

Preview managed writes without modifying the destination:

```bash
bash scripts/install.sh --dry-run
```

Install or update the managed files:

```bash
bash scripts/install.sh
```

The destination defaults to `${CODEX_HOME:-$HOME/.codex}`. Set `CODEX_HOME` for a
different installation, and `SDD_PYTHON` when Python discovery needs an override.

Validation runs before any installation write. A reinstall backs up the entire
previous managed skill directory and managed agent files, including an existing
`sdd-orchestrator.toml`, under
`$CODEX_HOME/backups/sdd-workflow-<timestamp>-<process-id>/`.
The installer replaces the complete managed skill directory, so files removed
from the distribution do not remain active after an upgrade. Their previous bytes
remain in the backup. It installs the five active TOMLs, retires only the exact
former Orchestrator agent path, and leaves unmanaged agents and other Codex files
untouched. Restore a previous version from the corresponding backup when needed.

Installing the package does not change the root session's selected model or the
client's global security settings. This repository's CI tests use temporary
installations; they do not update a user's active Codex installation.

Each runtime cycle creates an isolated artifact package by default. Reuse requires
an explicit continuation request and matching directory, workspace, and source
identity; an old active feature never selects the next task's package.

## Repository structure

```text
.github/workflows/      Read-only continuous validation
agents/                 Five canonical Codex agent definitions
docs/                   Current design and implementation/verification plan
scripts/                Distribution validator and installer
skills/sdd-workflow/    Skill core, metadata, seven role references, conditional remote memory
tests/                  Policy, validator, and installer regression tests
```

## Tests

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
bash tests/test_install.sh
bash -n scripts/install.sh tests/test_install.sh
git diff --check
```

The GitHub Actions workflow runs policy regressions, distribution validation, the
full Python suite, and installer/upgrade checks on pull requests and main pushes.
Installer tests always use a temporary `CODEX_HOME`; they test backup and removal
of obsolete managed files without touching an active installation.

## Repository

The canonical repository is [mikel-lab/SDD-Workflow](https://github.com/mikel-lab/SDD-Workflow).
