#!/usr/bin/env bash
# Install only the managed SDD Workflow skill and canonical agents.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
dry_run=false

usage() {
  printf 'Usage: %s [--dry-run]\n' "${0##*/}" >&2
}

case ${1:-} in
  '') ;;
  --dry-run) dry_run=true ;;
  -h|--help) usage; exit 0 ;;
  *) usage; exit 2 ;;
esac

resolve_python() {
  local candidate version
  is_compatible_python() {
    version=$("$1" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null) || return 1
    [[ $version =~ ^([0-9]+)\.([0-9]+)$ ]] || return 1
    [[ ${BASH_REMATCH[1]} -gt 3 || ( ${BASH_REMATCH[1]} -eq 3 && ${BASH_REMATCH[2]} -ge 11 ) ]]
  }
  if [[ -n ${SDD_PYTHON:-} ]]; then
    candidate=$SDD_PYTHON
    if ! command -v "$candidate" >/dev/null 2>&1 && [[ ! -x $candidate ]]; then
      printf 'ERROR: SDD_PYTHON is not executable: %s\n' "$candidate" >&2
      return 1
    fi
    if ! is_compatible_python "$candidate"; then
      printf 'ERROR: SDD_PYTHON must provide Python 3.11+; got an incompatible interpreter: %s\n' "$candidate" >&2
      return 1
    fi
    printf '%s\n' "$candidate"
    return
  fi
  for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      if is_compatible_python "$candidate"; then
        printf '%s\n' "$candidate"
        return
      fi
    fi
  done
  printf 'ERROR: Python 3.11+ is required; set SDD_PYTHON to a compatible interpreter.\n' >&2
  return 1
}

python=$(resolve_python)
"$python" "$repo_root/scripts/validate.py"

codex_home=${CODEX_HOME:-"$HOME/.codex"}
skill_source="$repo_root/skills/sdd-workflow"
skill_destination="$codex_home/skills/sdd-workflow"
agent_names=(
  sdd-planner.toml
  sdd-implementer-main.toml
  sdd-implementer-high.toml
  sdd-implementer-simple.toml
  sdd-reviewer.toml
)
retired_agent_names=(sdd-orchestrator.toml)

if $dry_run; then
  printf 'Dry run: would install %s and %d managed agents into %s.\n' \
    "$skill_source" "${#agent_names[@]}" "$codex_home"
  for agent in "${retired_agent_names[@]}"; do
    printf 'Dry run: would retire %s from %s/agents.\n' "$agent" "$codex_home"
  done
  exit 0
fi

backup_root="$codex_home/backups/sdd-workflow-$(date -u +%Y%m%dT%H%M%SZ)-$$"
has_backup=false
backup_path() {
  local source=$1 relative=$2
  if [[ -e $source ]]; then
    mkdir -p "$(dirname "$backup_root/$relative")"
    cp -R "$source" "$backup_root/$relative"
    has_backup=true
  fi
}

backup_path "$skill_destination" 'skills/sdd-workflow'
for agent in "${agent_names[@]}"; do
  backup_path "$codex_home/agents/$agent" "agents/$agent"
done
for agent in "${retired_agent_names[@]}"; do
  backup_path "$codex_home/agents/$agent" "agents/$agent"
done

mkdir -p "$codex_home/skills" "$codex_home/agents"
if [[ -e $skill_destination ]]; then
  rm -rf "$skill_destination"
fi
cp -R "$skill_source" "$skill_destination"
for agent in "${agent_names[@]}"; do
  cp "$repo_root/agents/$agent" "$codex_home/agents/$agent"
done
for agent in "${retired_agent_names[@]}"; do
  rm -f "$codex_home/agents/$agent"
done

if $has_backup; then
  printf 'Installed sdd-workflow; backup saved to %s\n' "$backup_root"
else
  printf 'Installed sdd-workflow.\n'
fi
