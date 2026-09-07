# SDD Workflow

`sdd-workflow` is a portable Codex skill for a governed
Specification-Driven Development lifecycle. The invoking root chat coordinates planning, an
independent review, an explicit implementation gate, bounded delivery, and
final verification. SpecKit owns the planning artifacts; this package owns
the workflow rules and role definitions.

## Roles

| Role | Purpose |
| --- | --- |
| `sdd-planner` | Creates and corrects the planning artifact set. |
| `sdd-implementer-main` | Delivers normal non-trivial work and integrations. |
| `sdd-implementer-high` | Replaces Main for explicitly escalated complex work. |
| `sdd-implementer-simple` | Delivers small, isolated, dependency-ready work. |
| `sdd-reviewer` | Independently reviews plans, deliveries, convergence, and final output. |

Planner and Reviewer use `gpt-6-astra` with `low` reasoning effort. Their
canonical settings are enforced by the distribution validator.

The root chat is the sole coordination and user-contact authority; it performs
the Orchestrator role and does not dispatch a second Orchestrator agent. Use
`gpt-5.6-sol` at medium reasoning effort for that root-chat coordination when
available.

The implementation gate opens only after an independent planning review returns
`approved` and the user replies exactly `Approved, implement.`.

## Requirements

- Bash
- Python 3.11 or newer (the installer accepts `SDD_PYTHON` for an explicit
  compatible interpreter)
- Python's `tomllib` module
- PyYAML when the optional official skill validator is available
- Installed SpecKit skills: `speckit-specify`, `speckit-clarify`,
  `speckit-checklist`, `speckit-plan`, `speckit-tasks`, and
  `speckit-analyze`

`speckit-converge` is conditional, not a universal runtime dependency. Use it
only when `speckit-implement` executed the current task list, or when a future
converge contract explicitly supports the executor that produced the current
implementation. Native SDD and Luna deliveries normally repair missing task
coverage through the `speckit-tasks` contract.

The workflow also requires the applicable Superpowers practices when their
condition is reached: `test-driven-development` for implementation changes,
`systematic-debugging` for unexpected behavior or failures,
`receiving-code-review` when acting on review findings,
`verification-before-completion` before success claims, and
`dispatching-parallel-agents` when independent work is actually parallelized.

For source-backed requests, provide a Jira connector or authenticated browser
session when Jira is the authoritative source. Provide Figma access in the same
way when visual or interaction evidence is essential. An inaccessible optional
Figma source is recorded as a limitation rather than invented or treated as an
automatic blocker.

## Validate

Run from the repository root:

```bash
python3 scripts/validate.py
```

The validator checks the exact 24-file distribution, all five canonical agent TOMLs,
the skill frontmatter, eight direct skill references, full-tree portability,
and the official skill validator when it can be resolved.

## Install and update

Preview every managed write without changing the destination:

```bash
./scripts/install.sh --dry-run
```

Install or update the managed files:

```bash
./scripts/install.sh
```

The destination defaults to `${CODEX_HOME:-$HOME/.codex}`. Set `CODEX_HOME`
to install into a different Codex home, and set `SDD_PYTHON` when the preferred
Python interpreter is not discovered automatically.

Before every installation, validation runs before any write. Each cycle creates
an isolated artifact package by default; reuse it only after an explicit user
continuation request whose identity matches the existing package. A reinstall backs
up every existing managed destination, including a previous
`sdd-orchestrator.toml`, under
`$CODEX_HOME/backups/sdd-workflow-<timestamp>-<process-id>/`. The installer
copies only `skills/sdd-workflow` and the five active `sdd-*.toml` files, then
retires only that exact former Orchestrator path; unmanaged agents and other
Codex files remain untouched. Restore a previous version by copying its
backed-up skill and managed agent files back to the same locations.

## Repository structure

```text
agents/                 Five canonical Codex agent definitions
docs/                   Approved design and implementation plan
scripts/                Distribution validator and installer
skills/sdd-workflow/    Skill core, metadata, and role references
tests/                  Validator and installer behavioral tests
```

## Tests

```bash
python3 -m unittest -v tests/test_validate.py
bash tests/test_install.sh
```

Installer tests always use a temporary `CODEX_HOME` and do not modify an active
Codex installation.

## Add a remote later

The repository is intentionally usable without a remote. When ready to publish
it, create an empty remote, then add it and push the current branch:

```bash
git remote add origin <remote-url>
git push -u origin <branch-name>
```
