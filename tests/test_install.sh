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
  # Break caught: a fresh install omits managed content.
  local home="$temp_root/fresh"
  run_install "$home"
  assert_file "$home/skills/sdd-workflow/SKILL.md"
  local count
  count=$(find "$home/agents" -maxdepth 1 -name 'sdd-*.toml' -type f | wc -l | tr -d ' ')
  [[ $count == 6 ]] || fail "expected six managed agents, got $count"
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

test_unmanaged_agents_are_unchanged() {
  # Break caught: install rewrites an agent it does not own.
  local home="$temp_root/unmanaged"
  mkdir -p "$home/agents"
  printf 'unmanaged\nbytes\n' >"$home/agents/keep-me.toml"
  local before
  before=$(cksum "$home/agents/keep-me.toml")
  run_install "$home"
  [[ $(cksum "$home/agents/keep-me.toml") == "$before" ]] || fail 'unmanaged agent changed'
}

test_dry_run_writes_nothing() {
  # Break caught: dry-run changes the filesystem.
  local home="$temp_root/dry-run"
  run_install "$home" --dry-run
  assert_not_exists "$home"
}

test_validation_precedes_writes
test_incompatible_explicit_python_fails_before_validation_or_writes
test_fresh_install
test_reinstall_backs_up_managed_destinations
test_unmanaged_agents_are_unchanged
test_dry_run_writes_nothing
printf 'install tests passed\n'
