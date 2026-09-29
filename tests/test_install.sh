#!/usr/bin/env bash
# Behavioral tests for install.sh. Every destination lives under a temporary
# CODEX_HOME, so the user's Codex installation is never touched.
set -euo pipefail

source_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
temp_root=$(mktemp -d)
trap 'rm -rf "$temp_root"' EXIT
distribution="$temp_root/distribution"
cp -R "$source_root" "$distribution"

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

run_install() {
  local home=$1
  shift
  CODEX_HOME="$home" SDD_PYTHON="${SDD_PYTHON:-python3}" bash "$distribution/scripts/install.sh" "$@"
}

assert_file() {
  [[ -f $1 ]] || fail "expected file: $1"
}

assert_not_exists() {
  [[ ! -e $1 ]] || fail "unexpected path: $1"
}

test_validation_precedes_writes() {
  # Break caught: an invalid source mutates a destination before rejection.
  local home="$temp_root/validation-first"
  printf 'name = [\n' >"$distribution/agents/sdd-planner.toml"
  if run_install "$home" >"$temp_root/validation.out" 2>&1; then
    fail 'invalid distribution unexpectedly installed'
  fi
  assert_not_exists "$home/skills/sdd-workflow"
  assert_not_exists "$home/agents"
  cp "$source_root/agents/sdd-planner.toml" "$distribution/agents/sdd-planner.toml"
}

test_incompatible_explicit_python_fails_before_validation_or_writes() {
  # Break caught: an explicit old interpreter bypasses the Python version gate.
  local home="$temp_root/incompatible-python"
  local fake_python="$temp_root/python-3.10"
  printf '#!/usr/bin/env bash\nprintf "3.10\\n"\n' >"$fake_python"
  chmod +x "$fake_python"
  if CODEX_HOME="$home" SDD_PYTHON="$fake_python" bash "$distribution/scripts/install.sh" >"$temp_root/python.out" 2>&1; then
    fail 'incompatible explicit interpreter unexpectedly installed'
  fi
  grep -F 'Python 3.11+' "$temp_root/python.out" >/dev/null || fail 'missing actionable Python version error'
  assert_not_exists "$home"
}

test_fresh_install() {
  # Break caught: a fresh install retains a retired file or omits an active agent.
  local home="$temp_root/fresh"
  run_install "$home"
  assert_file "$home/skills/sdd-workflow/SKILL.md"
  local count
  count=$(find "$home/agents" -maxdepth 1 -name 'sdd-*.toml' -type f | wc -l | tr -d ' ')
  [[ $count == 4 ]] || fail "expected four managed agents, got $count"
  count=$(find "$home/agents" -maxdepth 1 -name 'sdd-implementer-*.toml' -type f | wc -l | tr -d ' ')
  [[ $count == 2 ]] || fail "expected two implementer profiles, got $count"
  count=$(find "$home/skills/sdd-workflow/references" -maxdepth 1 -name '*.md' -type f | wc -l | tr -d ' ')
  [[ $count == 8 ]] || fail "expected eight references, got $count"
  assert_file "$home/skills/sdd-workflow/references/remote-memory.md"
  cmp -s "$source_root/skills/sdd-workflow/references/remote-memory.md" "$home/skills/sdd-workflow/references/remote-memory.md" || fail 'installed remote memory reference differs from source'
  assert_not_exists "$home/agents/sdd-orchestrator.toml"
  assert_not_exists "$home/agents/sdd-implementer-high.toml"
  assert_not_exists "$home/skills/sdd-workflow/references/luna-lane.md"
}

test_reinstall_backs_up_managed_destinations() {
  # Break caught: reinstall overwrites managed files without a recoverable copy.
  local home="$temp_root/reinstall"
  run_install "$home"
  printf 'previous-skill\n' >"$home/skills/sdd-workflow/previous.txt"
  printf 'previous-agent\n' >"$home/agents/sdd-planner.toml"
  run_install "$home"
  local backup
  backup=$(find "$home/backups" -type d -name 'sdd-workflow-*' -print -quit)
  [[ -n $backup ]] || fail 'expected an installation backup'
  assert_file "$backup/skills/sdd-workflow/previous.txt"
  [[ $(cat "$backup/agents/sdd-planner.toml") == previous-agent ]] || fail 'agent backup lost original bytes'
}

test_upgrade_backs_up_and_retires_orchestrator() {
  # Break caught: an upgrade deletes the exact retired file without backup or
  # leaves it active after installing the four-agent distribution.
  local home="$temp_root/retire-orchestrator"
  local expected="$temp_root/previous-orchestrator.toml"
  mkdir -p "$home/agents"
  printf 'previous-orchestrator\nbytes\n' >"$home/agents/sdd-orchestrator.toml"
  printf 'previous-orchestrator\nbytes\n' >"$expected"
  run_install "$home"
  local backup
  backup=$(find "$home/backups" -type d -name 'sdd-workflow-*' -print -quit)
  [[ -n $backup ]] || fail 'expected a retirement backup'
  cmp -s "$expected" "$backup/agents/sdd-orchestrator.toml" || fail 'retired agent backup lost original bytes'
  assert_not_exists "$home/agents/sdd-orchestrator.toml"
}

test_upgrade_backs_up_and_retires_high_implementer() {
  # Break caught: the third implementer remains active, or its previous bytes
  # and the retained profiles are not preserved during a five-to-four upgrade.
  local home="$temp_root/retire-high"
  local previous="$temp_root/previous-five-agents"
  mkdir -p "$home/agents" "$previous"
  local agent backup count
  for agent in sdd-planner sdd-reviewer sdd-implementer-main sdd-implementer-simple sdd-implementer-high; do
    printf 'previous-%s\noriginal bytes\n' "$agent" >"$previous/$agent.toml"
    cp "$previous/$agent.toml" "$home/agents/$agent.toml"
  done
  run_install "$home"
  backup=$(find "$home/backups" -type d -name 'sdd-workflow-*' -print -quit)
  [[ -n $backup ]] || fail 'expected a five-agent upgrade backup'
  for agent in sdd-planner sdd-reviewer sdd-implementer-main sdd-implementer-simple sdd-implementer-high; do
    cmp -s "$previous/$agent.toml" "$backup/agents/$agent.toml" || fail "upgrade backup lost original bytes: $agent"
  done
  assert_not_exists "$home/agents/sdd-implementer-high.toml"
  count=$(find "$home/agents" -maxdepth 1 -name 'sdd-*.toml' -type f | wc -l | tr -d ' ')
  [[ $count == 4 ]] || fail "upgrade left an incorrect agent count: $count"
  for agent in sdd-planner sdd-reviewer sdd-implementer-main sdd-implementer-simple; do
    cmp -s "$source_root/agents/$agent.toml" "$home/agents/$agent.toml" || fail "upgraded profile differs: $agent"
  done
}

test_upgrade_removes_retired_reference_after_backup() {
  # Break caught: deleting a source reference leaves stale instructions installed.
  local home="$temp_root/retire-reference"
  local expected="$temp_root/previous-reference.md"
  mkdir -p "$home/skills/sdd-workflow/references"
  printf 'retired external execution instructions\noriginal bytes\n' >"$expected"
  cp "$expected" "$home/skills/sdd-workflow/references/luna-lane.md"
  run_install "$home"
  local backup
  backup=$(find "$home/backups" -type d -name 'sdd-workflow-*' -print -quit)
  [[ -n $backup ]] || fail 'expected a managed skill backup'
  cmp -s "$expected" "$backup/skills/sdd-workflow/references/luna-lane.md" || fail 'retired reference backup lost original bytes'
  assert_not_exists "$home/skills/sdd-workflow/references/luna-lane.md"
  cmp -s "$source_root/skills/sdd-workflow/SKILL.md" "$home/skills/sdd-workflow/SKILL.md" || fail 'installed skill differs from source'
  local agent
  for agent in sdd-planner sdd-implementer-main sdd-implementer-simple sdd-reviewer; do
    cmp -s "$source_root/agents/$agent.toml" "$home/agents/$agent.toml" || fail "installed profile differs: $agent"
  done
}

test_unmanaged_agents_are_unchanged() {
  # Break caught: install rewrites an agent it does not own, including a name
  # similar to the exact retired managed path.
  local home="$temp_root/unmanaged"
  mkdir -p "$home/agents"
  printf 'unmanaged\nbytes\n' >"$home/agents/keep-me.toml"
  printf 'custom-high\nbytes\n' >"$home/agents/sdd-implementer-high-custom.toml"
  local before custom_before
  before=$(cksum "$home/agents/keep-me.toml")
  custom_before=$(cksum "$home/agents/sdd-implementer-high-custom.toml")
  run_install "$home"
  [[ $(cksum "$home/agents/keep-me.toml") == "$before" ]] || fail 'unmanaged agent changed'
  [[ $(cksum "$home/agents/sdd-implementer-high-custom.toml") == "$custom_before" ]] || fail 'similarly named unmanaged agent changed'
}

test_dry_run_reports_retirement_and_writes_nothing() {
  # Break caught: dry-run hides retired-agent removal or changes the filesystem.
  local home="$temp_root/dry-run"
  mkdir -p "$home/agents" "$home/skills/sdd-workflow/references"
  printf 'retired-agent\n' >"$home/agents/sdd-orchestrator.toml"
  printf 'retired-high\n' >"$home/agents/sdd-implementer-high.toml"
  printf 'retired-reference\n' >"$home/skills/sdd-workflow/references/luna-lane.md"
  local before reference_before high_before
  before=$(cksum "$home/agents/sdd-orchestrator.toml")
  high_before=$(cksum "$home/agents/sdd-implementer-high.toml")
  reference_before=$(cksum "$home/skills/sdd-workflow/references/luna-lane.md")
  run_install "$home" --dry-run >"$temp_root/dry-run.out"
  grep -F 'would retire sdd-orchestrator.toml' "$temp_root/dry-run.out" >/dev/null || fail 'dry-run did not report orchestrator retirement'
  grep -F 'would retire sdd-implementer-high.toml' "$temp_root/dry-run.out" >/dev/null || fail 'dry-run did not report high implementer retirement'
  grep -F '4 managed agents' "$temp_root/dry-run.out" >/dev/null || fail 'dry-run reported incorrect agent count'
  [[ $(cksum "$home/agents/sdd-orchestrator.toml") == "$before" ]] || fail 'dry-run changed retired agent'
  [[ $(cksum "$home/agents/sdd-implementer-high.toml") == "$high_before" ]] || fail 'dry-run changed retired high implementer'
  [[ $(cksum "$home/skills/sdd-workflow/references/luna-lane.md") == "$reference_before" ]] || fail 'dry-run changed retired reference'
  assert_not_exists "$home/skills/sdd-workflow/SKILL.md"
  assert_not_exists "$home/backups"
}

test_validation_precedes_writes
test_incompatible_explicit_python_fails_before_validation_or_writes
test_fresh_install
test_reinstall_backs_up_managed_destinations
test_upgrade_backs_up_and_retires_orchestrator
test_upgrade_backs_up_and_retires_high_implementer
test_upgrade_removes_retired_reference_after_backup
test_unmanaged_agents_are_unchanged
test_dry_run_reports_retirement_and_writes_nothing
printf 'install tests passed (9 scenarios)\n'
