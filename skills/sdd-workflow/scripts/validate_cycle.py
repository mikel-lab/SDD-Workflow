#!/usr/bin/env python3
"""Validate one explicitly selected SDD cycle without feature discovery."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


JIRA_KEY = re.compile(r"\b[A-Z][A-Z0-9]+-[0-9]+\b")
MANIFEST_KEYS = {
    "schema_version",
    "cycle_id",
    "workspace_root",
    "speckit_root",
    "primary_source",
    "source_ids",
    "artifact_directory",
    "artifacts",
    "continuation_of",
}
SPEC_PATH = re.compile(r"(?<![A-Za-z0-9_.-])(specs/[A-Za-z0-9_./-]+)")
TASK_ID = re.compile(r"\bT[0-9]+\b")


def load_json(path: Path) -> dict[str, object]:
    """Load a JSON object, rejecting missing and non-object documents."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON file {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return value


def resolve_inside(root: Path, relative: str) -> Path:
    """Resolve a relative path only when every component remains in *root*."""
    candidate = Path(relative)
    if candidate.is_absolute() or not relative or relative == ".":
        raise ValueError(f"path must be a non-empty relative path: {relative!r}")

    resolved_root = root.resolve()
    current = resolved_root
    for part in candidate.parts:
        if part in (".", ".."):
            raise ValueError(f"path traversal is not allowed: {relative!r}")
        current /= part
        if current.is_symlink():
            raise ValueError(f"symlink is not allowed: {current}")
    try:
        current.resolve(strict=False).relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"path escapes its declared root: {relative!r}") from error
    return current


def actual_artifacts(artifact_dir: Path) -> set[str]:
    """Return files in the selected package, excluding its control manifest."""
    if artifact_dir.is_symlink():
        raise ValueError(f"symlink is not allowed: {artifact_dir}")
    if not artifact_dir.is_dir():
        raise ValueError(f"artifact directory does not exist: {artifact_dir}")

    artifacts: set[str] = set()
    for path in artifact_dir.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed: {path}")
        relative_path = path.relative_to(artifact_dir).as_posix()
        if path.is_file() and relative_path != "sdd-cycle.json":
            artifacts.add(relative_path)
    return artifacts


def referenced_spec_paths(text: str) -> set[str]:
    """Return explicit specs/ paths mentioned by a governed artifact."""
    return set(SPEC_PATH.findall(text))


def validate_cycle(
    manifest_path: Path,
    expected_workspace: Path,
    expected_source: str,
    require_tasks: bool,
) -> list[str]:
    errors: list[str] = []
    try:
        manifest = load_json(manifest_path)
    except ValueError as error:
        return [str(error)]

    if set(manifest) != MANIFEST_KEYS:
        return [
            "manifest schema keys must be exactly: "
            + ", ".join(sorted(MANIFEST_KEYS))
        ]
    if manifest["schema_version"] != 1:
        errors.append("manifest schema_version must be 1")
    if not isinstance(manifest["cycle_id"], str) or not manifest["cycle_id"]:
        errors.append("manifest cycle_id must be a non-empty string")
    if manifest["continuation_of"] is not None and not isinstance(manifest["continuation_of"], str):
        errors.append("manifest continuation_of must be a string or null")

    string_fields = ("workspace_root", "speckit_root", "primary_source", "artifact_directory")
    for field in string_fields:
        if not isinstance(manifest[field], str) or not manifest[field]:
            errors.append(f"manifest {field} must be a non-empty string")
    source_ids = manifest["source_ids"]
    artifacts = manifest["artifacts"]
    if not isinstance(source_ids, list) or not all(isinstance(value, str) and value for value in source_ids):
        errors.append("manifest source_ids must be a list of non-empty strings")
    if not isinstance(artifacts, list) or not all(isinstance(value, str) and value for value in artifacts):
        errors.append("manifest artifacts must be a list of non-empty strings")
    if errors:
        return errors

    workspace = Path(manifest["workspace_root"])
    speckit_root = Path(manifest["speckit_root"])
    artifact_relative = manifest["artifact_directory"]
    declared_artifacts = artifacts
    allowed_sources = set(source_ids)

    if workspace.resolve() != expected_workspace.resolve():
        errors.append("workspace identity does not match --expected-workspace")
    if manifest["primary_source"] != expected_source:
        errors.append("primary source does not match --expected-source")
    if manifest["primary_source"] not in allowed_sources:
        errors.append("primary source must be included in source_ids")
    if len(declared_artifacts) != len(set(declared_artifacts)):
        errors.append("manifest artifacts must not contain duplicates")

    if not speckit_root.is_dir():
        errors.append(f"speckit root does not exist: {speckit_root}")
        return errors
    try:
        artifact_dir = resolve_inside(speckit_root, artifact_relative)
    except ValueError as error:
        return [*errors, str(error)]
    if manifest_path.resolve() != (artifact_dir / "sdd-cycle.json").resolve():
        errors.append("manifest must be sdd-cycle.json in its declared artifact directory")

    try:
        listed_paths = {relative: resolve_inside(artifact_dir, relative) for relative in declared_artifacts}
        actual = actual_artifacts(artifact_dir)
    except ValueError as error:
        return [*errors, str(error)]
    if set(listed_paths) != actual:
        errors.append(
            "manifest artifacts do not match actual files: "
            f"declared {sorted(listed_paths)}, found {sorted(actual)}"
        )

    feature_path = speckit_root / ".specify/feature.json"
    if feature_path.is_symlink():
        errors.append(f"symlink is not allowed: {feature_path}")
    else:
        try:
            feature = load_json(feature_path)
            active_directory = feature.get("feature_directory")
            if not isinstance(active_directory, str):
                errors.append("active feature file must contain feature_directory")
            elif resolve_inside(speckit_root, active_directory).resolve() != artifact_dir.resolve():
                errors.append("active feature does not match the declared artifact directory")
        except ValueError as error:
            errors.append(str(error))

    for relative, path in listed_paths.items():
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            errors.append(f"cannot read listed artifact {relative}: {error}")
            continue
        for referenced in referenced_spec_paths(text):
            try:
                referenced_path = resolve_inside(speckit_root, referenced)
            except ValueError as error:
                errors.append(str(error))
                continue
            if referenced_path != artifact_dir and artifact_dir not in referenced_path.parents:
                errors.append(f"cross-package specs/ reference in {relative}: {referenced}")
        for key in JIRA_KEY.findall(text):
            if key not in allowed_sources:
                errors.append(f"unauthorized Jira key in {relative}: {key}")

    if require_tasks:
        tasks_path = listed_paths.get("tasks.md")
        if tasks_path is None or not tasks_path.is_file():
            errors.append("tasks.md is required when --require-tasks is set")
        else:
            try:
                first_task = TASK_ID.search(tasks_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError) as error:
                errors.append(f"cannot read tasks.md: {error}")
                return errors
            if first_task is None or first_task.group() != "T001":
                errors.append("the first task ID must be T001")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--expected-workspace", required=True, type=Path)
    parser.add_argument("--expected-source", required=True)
    parser.add_argument("--require-tasks", action="store_true")
    args = parser.parse_args()

    errors = validate_cycle(
        args.manifest,
        args.expected_workspace,
        args.expected_source,
        args.require_tasks,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Cycle validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
