# Isolated SDD Cycles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the active chat the sole SDD coordinator, guarantee a new isolated SpecKit package for every new cycle, and reduce routine agent/review overhead.

**Architecture:** The root chat owns the state machine and delegates only planning, implementation, and independent verification. Every cycle is bound to `sdd-cycle.json`, a new explicit `SPECIFY_FEATURE_DIRECTORY`, and a deterministic validator that never discovers historical feature contents. The distribution contains five native agents; the normal path has one planning review, one principal implementer, and one final Reviewer that combines reconciliation and verification.

**Tech Stack:** Codex skills Markdown/YAML, TOML, Python 3.11+ standard library, Bash, SpecKit, Superpowers skill TDD, Git, and fresh Codex agents for behavioral tests.

## Global Constraints

- Approved design: `docs/design.md` on branch `codex/sdd-cycle-isolation`.
- Do not modify official SpecKit skills.
- A new cycle ignores `.specify/feature.json` as selection input and passes a new exact `SPECIFY_FEATURE_DIRECTORY` to `speckit-specify`.
- Do not read consumer planning artifacts outside the selected cycle directory.
- Reuse requires an explicit continuation request plus exact workspace and primary-source identity.
- The root chat is the Orchestrator role and must not dispatch `sdd-orchestrator`.
- Preserve the exact `Approved, implement.` gate, baseline invalidation, Reviewer read-only behavior, Main/High exclusivity, Luna authorization, and the aggregate simple-lane ceiling.
- Keep Planner and Reviewer on GPT-5.6 Sol/high; preserve Main, High, and Simple on Terra medium/high/low.
- Final source inventory: exactly 24 files—remove one Orchestrator TOML and add one runtime validator.
- Store evidence only below `/tmp/codex-sdd-cycle-isolation-evidence`.
- Install globally only after tests and independent review pass; back up the retired installed Orchestrator.
- Preserve every unmanaged agent.
- Do not push without separate user authorization.

## File Map

- Create `skills/sdd-workflow/scripts/validate_cycle.py`: validate one exact cycle without sibling discovery.
- Modify `skills/sdd-workflow/SKILL.md`: root-chat authority, isolation and efficient normal path.
- Modify references `orchestrator.md`, `sources-and-artifacts.md`, `contracts.md`, `planner.md`, `reviewer.md`, `lifecycle-and-gates.md`, and `implementers.md`.
- Preserve `luna-lane.md` unless a regression proves an incompatibility.
- Delete `agents/sdd-orchestrator.toml`.
- Modify `agents/sdd-planner.toml` and `agents/sdd-reviewer.toml`.
- Preserve three implementer TOMLs unless a failing test requires wording changes.
- Modify `scripts/validate.py`, `scripts/install.sh`, `tests/test_validate.py`, `tests/test_install.sh`, `README.md`, and final documentation status.

---

### Task 1: Add the Deterministic Cycle Validator

**Files:**
- Create: `skills/sdd-workflow/scripts/validate_cycle.py`
- Modify: `tests/test_validate.py`
- Modify: `scripts/validate.py`

**Interfaces:**
- CLI: `python validate_cycle.py --manifest PATH --expected-workspace PATH --expected-cycle-id ID --expected-speckit-root PATH --expected-source TEAM-123 --expected-source-id TEAM-123 [--expected-source-id TEAM-456 ...] --expected-artifact-directory specs/ID-feature (--new-cycle | --expected-continuation-of ID) [--require-tasks]`
- Manifest keys: `schema_version`, `cycle_id`, `workspace_root`, `speckit_root`, `primary_source`, `source_ids`, `artifact_directory`, `artifacts`, `continuation_of`.
- Success: exit 0 and `Cycle validation passed.`; failure: exit 1 and actionable `ERROR:` lines.

- [ ] **Step 1: Write fixture helpers and failing tests**

Add `CycleValidatorTests` to `tests/test_validate.py`. Its fixture uses:

```text
fixture/
├── .specify/feature.json
├── mobile-app/
└── specs/20260806-143500-mobile-app-team-123-feature/
    ├── sdd-cycle.json
    ├── spec.md
    └── tasks.md
```

Use this manifest:

```python
manifest = {
    "schema_version": 1,
    "cycle_id": "20260806-143500",
    "workspace_root": str(workspace.resolve()),
    "speckit_root": str(root.resolve()),
    "primary_source": "TEAM-123",
    "source_ids": ["TEAM-123"],
    "artifact_directory": "specs/20260806-143500-mobile-app-team-123-feature",
    "artifacts": ["spec.md", "tasks.md"],
    "continuation_of": None,
}
```

Add tests named:

```python
test_valid_isolated_cycle_passes
test_active_feature_mismatch_fails
test_workspace_identity_mismatch_fails
test_primary_source_mismatch_fails
test_unlisted_artifact_fails
test_cross_spec_reference_fails
test_foreign_jira_key_fails
test_tasks_must_start_at_t001
test_artifact_symlink_escape_fails
```

- [ ] **Step 2: Run RED**

```bash
python3 -B -m unittest -v tests.test_validate.CycleValidatorTests
```

Expected: failure because `validate_cycle.py` is absent.

- [ ] **Step 3: Implement the minimal script**

Define:

```python
JIRA_KEY = re.compile(r"\b[A-Z][A-Z0-9]+-[0-9]+\b")

def load_json(path: Path) -> dict[str, object]: ...
def resolve_inside(root: Path, relative: str) -> Path: ...
def actual_artifacts(artifact_dir: Path) -> set[str]: ...
def referenced_spec_paths(text: str) -> set[str]: ...
def validate_cycle(
    manifest_path: Path,
    expected_workspace: Path,
    expected_source: str,
    expected_cycle_id: str,
    expected_speckit_root: Path,
    expected_artifact_directory: str,
    expected_source_ids: list[str],
    expected_continuation_of: str | None,
    require_tasks: bool,
) -> list[str]: ...
def main() -> int: ...
```

The implementation must require the exact schema; compare every root-supplied identity, complete source-ID set, and exclusive new/continuation mode; resolve all paths inside the declared roots; reject symlinks; compare `artifacts` with actual files except `sdd-cycle.json`; read only listed files; reject cross-package `specs/` references, local relative references that escape the containing package, and unauthorized Jira keys; verify `.specify/feature.json`; and require the first task ID to be `T001` when `--require-tasks` is set. It must never enumerate sibling feature directories.

- [ ] **Step 4: Register the runtime file**

Add `Path("skills/sdd-workflow/scripts/validate_cycle.py")` to `EXPECTED_FILES`. The intermediate tree has 25 files until Task 4 removes the old agent.

- [ ] **Step 5: Run GREEN and regressions**

```bash
python3 -B -m unittest -v tests.test_validate.CycleValidatorTests
python3 -B -m unittest -v tests/test_validate.py
python3 -B scripts/validate.py
```

- [ ] **Step 6: Commit**

```bash
git add skills/sdd-workflow/scripts/validate_cycle.py tests/test_validate.py scripts/validate.py
git commit -m "feat: validate isolated SDD cycles"
```

---

### Task 2: Move Orchestration to the Root Chat and Enforce Isolation

**Files:**
- Modify: `skills/sdd-workflow/SKILL.md`
- Modify: `skills/sdd-workflow/references/orchestrator.md`
- Modify: `skills/sdd-workflow/references/sources-and-artifacts.md`
- Modify: `skills/sdd-workflow/references/contracts.md`
- Modify: `skills/sdd-workflow/references/planner.md`
- Modify: `agents/sdd-planner.toml`
- Modify: `agents/sdd-reviewer.toml`
- Test: `tests/test_validate.py`
- Evidence: `/tmp/codex-sdd-cycle-isolation-evidence/task-2/`

**Interfaces:**
- Planner/Reviewer result fields: `cycle_id`, `source_ids`, `artifact_directory`, `artifact_reads`, `changed_paths`, `cycle_validation_command`, `cycle_validation_result`.

- [ ] **Step 1: Preserve a sanitized RED incident**

Record:

```text
New source: TEAM-807
Previously active package: TEAM-790 with T001-T067
Wrong decision: reuse the related active package and append T068-T080
Wrong ownership: root chat and configured Orchestrator were treated as competing coordinators
```

Do not copy consumer code, private ticket text or absolute paths.

- [ ] **Step 2: Add failing structural tests**

```python
test_root_chat_is_declared_as_sole_orchestrator
test_root_chat_must_not_dispatch_sdd_orchestrator
test_new_cycle_ignores_active_feature_as_selection_input
test_explicit_feature_directory_is_mandatory
test_historical_spec_discovery_is_forbidden
test_planner_and_reviewer_report_artifact_reads
test_continuation_requires_explicit_request_and_identity_match
```

Expected: RED against current source.

- [ ] **Step 3: Rewrite the core authority and sequence**

In `SKILL.md`, add `Root Chat Authority`: the invoking chat owns coordination and user contact, must not dispatch `sdd-orchestrator`, and delegates Planner, implementers and Reviewer. Require cycle identity before artifact reads and the cycle validator at planning completion, pre-review, baseline freeze, pre-implementation, and final reconciliation. Rename the quick-reference row to `Root chat (Orchestrator role)`.

- [ ] **Step 4: Add positive new-cycle and continuation recipes**

New cycle order:

```text
validate request and source access
resolve workspace_root and speckit_root separately
create cycle_id and an absent artifact_directory
delegate manifest creation and speckit-specify with exact SPECIFY_FEATURE_DIRECTORY
validate manifest and active feature output
permit artifact reads only from artifact_directory
```

Continuation is a separate conditional triggered only by explicit user intent. Require manifest, exact path, workspace and primary-source matches before opening the package. Prohibit `find`, `rg`, globbing or equivalent artifact discovery across the feature root.

- [ ] **Step 5: Update contracts and agent instructions**

Planner creates `sdd-cycle.json` as its first control artifact, invokes official `speckit-specify` with the assigned directory, maintains `artifacts`, and reports exact reads/writes. Reviewer receives exact paths and never discovers feature packages. Any external artifact read invalidates the result.

- [ ] **Step 6: Run GREEN**

```bash
python3 -B -m unittest -v tests.test_validate.ValidateDistributionTests
python3 -B scripts/validate.py
```

- [ ] **Step 7: Commit**

```bash
git add skills/sdd-workflow agents/sdd-planner.toml agents/sdd-reviewer.toml tests/test_validate.py
git commit -m "feat: isolate every SDD cycle"
```

---

### Task 3: Reduce Routine Reviews Without Weakening Gates

**Files:**
- Modify: `skills/sdd-workflow/SKILL.md`
- Modify: references `orchestrator.md`, `lifecycle-and-gates.md`, `planner.md`, `reviewer.md`, `implementers.md`
- Modify only if required by RED: `agents/sdd-reviewer.toml`
- Test: `tests/test_validate.py`

**Interfaces:**
- Normal sequence: `Root chat -> Planner -> planning Reviewer -> exact gate -> Main -> final Reviewer`.
- Intermediate-review triggers: high-risk batch, security, persistence/migration, API contract, critical shared code, Luna pre-integration, Luna post-integration.

- [ ] **Step 1: Add failing review-budget tests**

```python
test_normal_path_has_one_planning_and_one_final_review
test_minor_planning_correction_uses_focused_delta_rereview
test_normal_microtasks_do_not_each_require_independent_review
test_high_risk_batches_still_require_review
test_luna_keeps_pre_and_post_integration_reviews
test_final_reviewer_combines_speckit_analyze_and_final_verdict
```

- [ ] **Step 2: Run RED**

Run the six tests. Expected: current per-native-batch and separate convergence/final-review language fails.

- [ ] **Step 3: Implement the planning budget**

Use one full planning review. Bounded corrections return to Planner and the same Reviewer performs a focused delta re-review. Require another full review only after material changes to scope, architecture, acceptance criteria, source set or artifact identity.

- [ ] **Step 4: Implement coherent execution batches**

Main owns a coherent dependency-ready batch by default, not one agent per task entry. Simple or Luna are allowed only when isolation yields net savings. High replaces Main. Normal batches use implementer verification until final review.

- [ ] **Step 5: Merge reconciliation and final review**

The final Reviewer runs read-only `speckit-analyze` and returns the integrated verdict in the same action. Existing-task gaps return to an implementer; missing task coverage returns to Planner and invalidates the baseline. Do not schedule an identical whole-package review afterward.

- [ ] **Step 6: Run GREEN and commit**

```bash
python3 -B -m unittest -v tests/test_validate.py
python3 -B scripts/validate.py
git add skills/sdd-workflow tests/test_validate.py agents/sdd-reviewer.toml
git commit -m "refactor: reduce routine SDD review overhead"
```

Omit `agents/sdd-reviewer.toml` if unchanged.

---

### Task 4: Migrate the Distribution from Six Agents to Five

**Files:**
- Delete: `agents/sdd-orchestrator.toml`
- Modify: `scripts/validate.py`, `scripts/install.sh`
- Modify: `tests/test_validate.py`, `tests/test_install.sh`
- Modify: `README.md`

**Interfaces:**
- Active agents: Planner, Main, High, Simple, Reviewer.
- Retired managed agent: `sdd-orchestrator.toml`.
- Installer must back up the retired file before removing only that exact active path.

- [ ] **Step 1: Add failing migration tests**

Update canonical expectations to five. Add installer tests:

```text
fresh install has five agents and no Orchestrator
upgrade backs up exact previous Orchestrator bytes and retires it
dry-run reports retirement but writes nothing
unmanaged agents remain byte-identical
```

Expected: RED while six-agent management remains.

- [ ] **Step 2: Delete the source Orchestrator and update inventory**

Remove its TOML and canonical entry. Keep `references/orchestrator.md` for the root chat. Include the runtime validator in `EXPECTED_FILES`; final source count returns to 24.

- [ ] **Step 3: Implement recoverable retirement**

Use:

```bash
agent_names=(
  sdd-planner.toml
  sdd-implementer-main.toml
  sdd-implementer-high.toml
  sdd-implementer-simple.toml
  sdd-reviewer.toml
)
retired_agent_names=(sdd-orchestrator.toml)
```

Back up skill, active agents and existing retired agents before mutation. Install current files, then remove only exact retired paths. Dry-run reports both actions without writes.

- [ ] **Step 4: Update README**

Document root-chat coordination, Sol-medium recommendation, five agents, isolated package by default, explicit continuation, validator use, upgrade backup, rollback, and unchanged implementation gate.

- [ ] **Step 5: Run GREEN**

```bash
python3 -B -m unittest -v tests/test_validate.py
SDD_PYTHON=python3 bash tests/test_install.sh
python3 -B scripts/validate.py
bash -n scripts/install.sh tests/test_install.sh
git ls-files | wc -l
```

Expected: all pass and count 24.

- [ ] **Step 6: Commit**

```bash
git add -A agents scripts tests README.md skills/sdd-workflow
git commit -m "feat: move SDD coordination to the root chat"
```

---

### Task 5: Forward-Test the Real Failure Modes

**Files:**
- Modify only when evidence requires it: skill/reference files and Planner/Reviewer TOMLs
- Evidence: `/tmp/codex-sdd-cycle-isolation-evidence/task-5/`

**Interfaces:**
- Root behavior model: GPT-5.6 Sol/medium, fresh context.
- Evidence: exact prompt, agent identity, raw output and manual score.

- [ ] **Step 1: Define two combined pressure prompts**

Isolation prompt pressures the agent to reuse an active TEAM-790 feature for new TEAM-807 because names are related, most old tasks are complete, and the deadline is near. PASS requires root ownership, a new explicit directory, no historical artifact read and no task append.

Review-budget prompt supplies a normal low-risk batch with 12 microtasks. PASS requires implementer verification plus one final Reviewer, not 12 reviews.

- [ ] **Step 2: Run five no-guidance controls per prompt**

Preserve ten raw outputs. Classify controls that pass as non-regression, never causal RED.

- [ ] **Step 3: Run five guided cases per prompt**

Require ten fresh agents to read the source skill first. All guided cases must pass.

- [ ] **Step 4: Test continuation**

Run one guided matching-manifest continuation and one mismatched-workspace continuation. Expected: exact reuse, then blocking.

- [ ] **Step 5: Apply only demonstrated refinements**

Use positive recipes for wrong shape, required fields for omissions and concise prohibitions only for observed discipline violations.

- [ ] **Step 6: Re-run affected variants and validation**

```bash
python3 -B -m unittest -v tests/test_validate.py
python3 -B scripts/validate.py
python3 -B "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" skills/sdd-workflow
```

- [ ] **Step 7: Commit only if source changed**

```bash
git add skills/sdd-workflow agents/sdd-planner.toml agents/sdd-reviewer.toml
git commit -m "fix: harden SDD cycle isolation"
```

---

### Task 6: Independent Review and Global Migration

**Files:**
- Inspect: all 24 source files
- Install: global skill and five agent TOMLs
- Retire: global `sdd-orchestrator.toml`
- Evidence: `/tmp/codex-sdd-cycle-isolation-evidence/task-6/`

**Interfaces:**
- Produces source/install byte parity, retired-agent backup and unchanged unmanaged hashes.

- [ ] **Step 1: Verify source**

```bash
python3 -B -m unittest -v tests/test_validate.py
SDD_PYTHON=python3 bash tests/test_install.sh
python3 -B scripts/validate.py
python3 -B "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" skills/sdd-workflow
bash -n scripts/install.sh tests/test_install.sh
git diff --check
```

- [ ] **Step 2: Obtain independent read-only review**

Use one fresh `sdd-reviewer` with design, plan, source, raw evidence and acceptance criteria. Do not install with Critical/Important findings open. Send confirmed findings through one bounded correction and one focused re-review.

- [ ] **Step 3: Snapshot global state**

Hash every global agent. Copy current skill and Orchestrator to `/tmp/codex-sdd-cycle-isolation-evidence/task-6/pre-install-backup/`.

- [ ] **Step 4: Dry-run and install**

Run `./scripts/install.sh --dry-run`, verify five installs plus retirement, then run the tested installer with Python 3.11+.

- [ ] **Step 5: Verify migration**

Confirm skill parity, five-agent parity, absent active Orchestrator, backup containing the former Orchestrator, official validation success and unchanged unmanaged hashes.

- [ ] **Step 6: Smoke-test the installed runtime validator**

Create a temporary valid TEAM-123 cycle and require tasks; expect PASS. Point active feature at another path; expect FAIL. Never use real consumer artifacts.

---

### Task 7: Final Documentation and Local Handoff

**Files:**
- Modify: `docs/design.md`
- Modify: `docs/implementation-plan.md`

**Interfaces:**
- Produces a clean local branch ready for separately authorized publication.

- [ ] **Step 1: Update statuses honestly**

Mark design implementation `verificada` only after Task 6. Mark plan checkboxes only with evidence. Keep non-regression distinct from causal improvement.

- [ ] **Step 2: Run final verification**

```bash
python3 -B -m unittest -v tests/test_validate.py
SDD_PYTHON=python3 bash tests/test_install.sh
python3 -B scripts/validate.py
python3 -B "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" skills/sdd-workflow
git ls-files | sort
git diff --check
```

Expected: all checks pass and exactly 24 files are listed.

- [ ] **Step 3: Reconfirm global parity and retirement**

Compare entire skill and five agents byte-for-byte; confirm retired Orchestrator absent and unmanaged hashes unchanged.

- [ ] **Step 4: Commit final documentation**

```bash
git add docs/design.md docs/implementation-plan.md
git commit -m "docs: finalize isolated SDD workflow"
```

- [ ] **Step 5: Verify handoff**

```bash
git status -sb
git log --oneline --decorate main..HEAD
git remote -v
```

Expected: clean local branch, commits ahead of main, remote unchanged, no push.

- [ ] **Step 6: Report and request publication authority**

Report commits, installed paths, backup, exact tests, evidence classification, review verdict and residual risks. Ask whether to merge/push; do not infer authority.
