#!/usr/bin/env python3
"""Validate the portable SDD Workflow distribution without modifying it."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "sdd-workflow"
AGENTS = ROOT / "agents"
REFERENCE_NAMES = (
    "contracts.md",
    "implementers.md",
    "lifecycle-and-gates.md",
    "luna-lane.md",
    "orchestrator.md",
    "planner.md",
    "reviewer.md",
    "sources-and-artifacts.md",
)
CANONICAL_AGENTS = {
    "sdd-orchestrator.toml": ("sdd-orchestrator", "gpt-5.6-sol", "high", "read-only"),
    "sdd-planner.toml": ("sdd-planner", "gpt-5.6-sol", "high", "workspace-write"),
    "sdd-implementer-main.toml": ("sdd-implementer-main", "gpt-5.6-terra", "medium", "workspace-write"),
    "sdd-implementer-high.toml": ("sdd-implementer-high", "gpt-5.6-terra", "high", "workspace-write"),
    "sdd-implementer-simple.toml": ("sdd-implementer-simple", "gpt-5.6-terra", "low", "workspace-write"),
    "sdd-reviewer.toml": ("sdd-reviewer", "gpt-5.6-sol", "high", "read-only"),
}
EXPECTED_FILES = (
    Path("README.md"),
    Path(".gitignore"),
    Path("docs/design.md"),
    Path("docs/implementation-plan.md"),
    Path("skills/sdd-workflow/SKILL.md"),
    Path("skills/sdd-workflow/agents/openai.yaml"),
    *(Path("skills/sdd-workflow/references") / name for name in REFERENCE_NAMES),
    *(Path("agents") / name for name in CANONICAL_AGENTS),
    Path("scripts/install.sh"),
    Path("scripts/validate.py"),
    Path("tests/test_validate.py"),
    Path("tests/test_install.sh"),
)
USER_PATH = re.compile(r"/(?:Users|home)/[^/\\\s]+")
PROJECT_PLACEHOLDER = re.compile(r"<(?:PROJECT|REPOSITORY|TEAM|USER)[A-Z0-9_-]*>")


def distribution_files() -> set[Path]:
    return {
        path.relative_to(ROOT)
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(ROOT).parts
    }


def check_layout(errors: list[str]) -> None:
    expected = set(EXPECTED_FILES)
    actual = distribution_files()
    for path in sorted(expected - actual):
        if not (ROOT / path).is_file():
            errors.append(f"missing required file: {path}")
    for path in sorted(actual - expected):
        errors.append(f"unexpected distribution file: {path}")

    actual_agents = {path.name for path in AGENTS.glob("sdd-*.toml")} if AGENTS.is_dir() else set()
    expected_agents = set(CANONICAL_AGENTS)
    if actual_agents != expected_agents:
        errors.append(
            "canonical agent set mismatch: "
            f"expected {', '.join(sorted(expected_agents))}; "
            f"found {', '.join(sorted(actual_agents)) or '(none)'}"
        )


def check_skill_frontmatter(errors: list[str]) -> None:
    skill_md = SKILL / "SKILL.md"
    if not skill_md.is_file():
        return
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(?P<frontmatter>.*?)\n---\n", text, re.DOTALL)
    if not match:
        errors.append("invalid SKILL.md frontmatter: expected YAML delimiters")
        return
    fields = {}
    for line in match.group("frontmatter").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    if fields.get("name") != "sdd-workflow":
        errors.append("invalid SKILL.md frontmatter: name must be sdd-workflow")
    if not fields.get("description"):
        errors.append("invalid SKILL.md frontmatter: description is required")


def check_agents(errors: list[str]) -> None:
    for filename, expected in CANONICAL_AGENTS.items():
        path = AGENTS / filename
        if not path.is_file():
            continue
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as error:
            errors.append(f"invalid TOML in {filename}: {error}")
            continue
        actual = tuple(data.get(key) for key in ("name", "model", "model_reasoning_effort", "sandbox_mode"))
        if actual != expected:
            errors.append(
                f"invalid canonical agent settings in {filename}: expected {expected}, found {actual}"
            )


def check_references(errors: list[str]) -> None:
    skill_md = SKILL / "SKILL.md"
    if not skill_md.is_file():
        return
    content = skill_md.read_text(encoding="utf-8")
    for reference in REFERENCE_NAMES:
        if f"references/{reference}" not in content:
            errors.append(f"SKILL.md does not directly reference: references/{reference}")


def check_portability(errors: list[str]) -> None:
    for relative_path in sorted(distribution_files()):
        path = ROOT / relative_path
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if USER_PATH.search(content):
            errors.append(f"absolute user path in versioned content: {relative_path}")
        if PROJECT_PLACEHOLDER.search(content):
            errors.append(f"project-specific placeholder in versioned content: {relative_path}")


def resolve_quick_validator() -> Path | None:
    configured = os.environ.get("SKILL_CREATOR_VALIDATE")
    candidates = [Path(configured)] if configured else []
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    candidates.append(codex_home / "skills/.system/skill-creator/scripts/quick_validate.py")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def check_official_validator(errors: list[str]) -> None:
    validator = resolve_quick_validator()
    if validator is None:
        return
    result = subprocess.run(
        [sys.executable, str(validator), str(SKILL)], text=True, capture_output=True, check=False
    )
    if result.returncode:
        message = (result.stderr or result.stdout).strip().replace("\n", " ")
        errors.append(f"official skill validation failed: {message}")


def main() -> int:
    errors: list[str] = []
    check_layout(errors)
    check_skill_frontmatter(errors)
    check_agents(errors)
    check_references(errors)
    check_portability(errors)
    if not errors:
        check_official_validator(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Validation passed: sdd-workflow distribution is portable and complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
