# SDD Workflow

A portable distribution for specification-driven development. Main is the invoking session and owns understanding, specification, planning, implementation and verification. Only independent Reviewer is mandatory. The skill does not configure Main's model/effort, and validation is not a runtime interceptor.

## Guarantees and execution
Spec before product edits; plan before implementation; source/spec/task/change/check traceability; implementation verification; independent final review for every cycle; Main corrects and the same Reviewer rechecks; evidence before completion; scope protection.

Normal flow: Main plans → validates/freezes → implements/verifies → independent final Reviewer → complete or correction. High-risk flow adds independent planning review before implementation. Auth/permissions, security, persistence/schema migration, destructive operations, external contracts, critical infrastructure, major architecture, cross-system consistency and data-loss/privacy triggers cannot be bypassed. Main may escalate others. Optional readers/writers need concrete benefit; writers have exclusive complete briefs and cannot overlap Main. Only Main dispatches, no default recursion.

## Skill and dependencies
Install sdd-workflow with only agents/sdd-reviewer.toml. Current configurable Reviewer default is GPT-6.1 Sol/high/read-only. Other available agents are optional capabilities, not managed Planner/implementer roles. Runtime observability must be reported honestly; a configuration declaration is not proof of independence.

SpecKit owns official planning artifacts: speckit-specify, necessary speckit-clarify, speckit-checklist, speckit-plan, speckit-tasks and read-only speckit-analyze. speckit-converge is conditional on its documented executor compatibility. Generated artifacts are dynamic, with exact cycle identity and inventory.

Compatible Superpowers execution skills: test-driven-development, systematic-debugging, receiving-code-review, verification-before-completion, using-git-worktrees, executing-plans and Main-only dispatching-parallel-agents when useful. They cannot create duplicate brainstorming/writing-plans, required per-task agents/reviews, self-review fallback or extra user approval. Jira/Figma access is needed only when essential source content is required; never invent unavailable content.

## Local records and validation
.sdd/cycles/<cycle_id>/ holds Main-written state/events/evidence separately from frozen SpecKit artifacts. Local means the current execution workspace; it does not require Git commits or publication. Do not blanket-ignore .sdd/, auto-edit consumer config or recreate missing approvals. Atomic checkpoint commit references immutable hash-linked events; orphan candidates are not committed approvals.

validate_cycle.py preserves identity/inventory/source/path isolation. validate_state.py is read-only and checks typed state/history/evidence, risk gates, current planning/product snapshots, review/findings/coverage and ownership. Capture modes emit JSON without writing. Product capture uses a fixed snapshot-scope JSON file inside exact cycle evidence, actual dirty/untracked/dependency input coverage and exact exclusions, never the workspace/SpecKit root. Unsupported or incomplete input fails explicitly. See the shipped schema, CLI help and references/contracts.md. Local structural checks do not authenticate Reviewer independence or discover every semantic dependency.

## Install and upgrade
Requires Python 3.11+; the optional official skill validator requires its existing PyYAML dependency. Configure SDD_PYTHON when needed; no global Python changes are necessary.

```sh
bash scripts/install.sh --dry-run
bash scripts/install.sh
```

Source validation happens before destination mutation. Install backs up the managed skill, current Reviewer and exact historical profiles, then retires Planner, Main/Simple implementers, Orchestrator and High implementer. Other profiles remain byte-for-byte intact; a similar custom name is not managed. Dry-run lists actions without writes. Installation does not configure consumer projects or migrate historical documents.

Rollback: inspect the reported backup, restore its managed skill and exact backed-up agent files to the same configured destination, and remove a newly installed managed Reviewer only if the old installation had none. Preserve all unrelated profiles and later changes; do not recursively delete the global agents directory. Check restored bytes against the backup. No new helper or background updater is required.

## Verification
```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
SDD_PYTHON=python3 bash tests/test_install.sh
bash -n scripts/install.sh tests/test_install.sh
git diff --check
```

This portable distribution has identity, state/snapshot and temporary-destination installer regressions. Static policy guards are not a live Codex execution; independent bounded behavioral exercises and final review assess actual compliance. Local results are distinct from remote CI and release. No token/time savings are claimed.

## Remote memory (optional)
A project may explicitly configure .sdd/config.json and an authorized documentation repository/INDEX.md. Detailed remote-memory.md procedure is loaded only for configured closure archival, justified history, storage/import or tracked-artifact migration, or already authorized PR references. No intake archive search, GitHub automation or background synchronization. Missing config preserves local data and does not change task verdict.

Keep a brief referral to the installed skill in project AGENTS.md instead of copying its body. Setup does not configure a destination automatically and does not migrate or untrack existing artifacts. A PR may include one direct verified package link per represented cycle; a later session recovers only bounded receipt/index metadata unless substantive history is justified. Archive publication/cleanup remain separately authorized and verified.
