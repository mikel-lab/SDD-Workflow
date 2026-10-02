"""Behavioral tests for the standalone distribution validator.

Each test names the repository break it must catch; the validator is run as a
real command against a disposable copy of the full distribution.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


class ValidateDistributionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / "distribution"
        shutil.copytree(
            SOURCE_ROOT,
            self.root,
            ignore=shutil.ignore_patterns("__pycache__", ".git"),
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def validate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [PYTHON, "scripts/validate.py"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_distribution_succeeds(self) -> None:
        # Break caught: a valid distribution is rejected.
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Validation passed", result.stdout)











    def test_retired_external_reference_is_rejected_by_distribution_validator(self) -> None:
        # Break caught: an old managed reference silently re-enters the package.
        retired = self.root / "skills/sdd-workflow/references/luna-lane.md"
        retired.write_text("# Obsolete external execution contract\n", encoding="utf-8")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected distribution file", result.stderr)
        self.assertIn("luna-lane.md", result.stderr)













    def test_missing_skill_reference_fails(self) -> None:
        # Break caught: a broken direct SKILL.md reference ships unnoticed.
        (self.root / "skills/sdd-workflow/references/contracts.md").unlink()
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required file", result.stderr)
        self.assertIn("contracts.md", result.stderr)

    def test_missing_distribution_artifact_fails(self) -> None:
        # Break caught: a shipped installation artifact is omitted unnoticed.
        (self.root / "README.md").unlink()
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required file", result.stderr)
        self.assertIn("README.md", result.stderr)

    def test_missing_design_doc_fails(self) -> None:
        # Break caught: the published design contract is omitted unnoticed.
        (self.root / "docs/design.md").unlink()
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required file", result.stderr)
        self.assertIn("docs/design.md", result.stderr)

    def test_missing_implementation_plan_fails(self) -> None:
        # Break caught: the published implementation plan is omitted unnoticed.
        (self.root / "docs/implementation-plan.md").unlink()
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required file", result.stderr)
        self.assertIn("docs/implementation-plan.md", result.stderr)

    def test_arbitrary_extra_file_fails(self) -> None:
        # Break caught: an unreviewed file silently expands the distribution.
        (self.root / "notes.txt").write_text("unexpected\n", encoding="utf-8")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected distribution file", result.stderr)
        self.assertIn("notes.txt", result.stderr)

    def test_invalid_agent_toml_fails(self) -> None:
        # Break caught: malformed agent configuration is accepted.
        agent = self.root / "agents/sdd-reviewer.toml"
        agent.write_text("name = [\n", encoding="utf-8")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid TOML", result.stderr)
        self.assertIn("sdd-reviewer.toml", result.stderr)

    def test_absolute_user_path_in_versioned_content_fails(self) -> None:
        # Break caught: a machine-specific user path makes the package nonportable.
        skill = self.root / "skills/sdd-workflow/references/contracts.md"
        leaked_path = "/" + "Users/example/private"
        skill.write_text(skill.read_text(encoding="utf-8") + f"\n{leaked_path}\n", encoding="utf-8")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("absolute user path", result.stderr)

    def test_absolute_user_path_in_docs_fails(self) -> None:
        # Break caught: portability scanning omits published design documents.
        document = self.root / "docs/design.md"
        leaked_path = "/" + "Users/example/private"
        document.write_text(document.read_text(encoding="utf-8") + f"\n{leaked_path}\n", encoding="utf-8")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("absolute user path", result.stderr)
        self.assertIn("docs/design.md", result.stderr)

    def test_absolute_user_path_in_tests_fails(self) -> None:
        # Break caught: portability scanning omits versioned tests.
        test_file = self.root / "tests/test_install.sh"
        leaked_path = "/" + "Users/example/private"
        test_file.write_text(test_file.read_text(encoding="utf-8") + f"\n{leaked_path}\n", encoding="utf-8")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("absolute user path", result.stderr)
        self.assertIn("tests/test_install.sh", result.stderr)

    def test_cache_file_fails(self) -> None:
        # Break caught: generated caches become accepted package contents.
        cache = self.root / "tests/__pycache__/unexpected.pyc"
        cache.parent.mkdir()
        cache.write_bytes(b"cache")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected distribution file", result.stderr)
        self.assertIn("tests/__pycache__/unexpected.pyc", result.stderr)

    def test_wrong_canonical_agent_set_fails(self) -> None:
        # Break caught: a required canonical agent is absent.
        (self.root / "agents/sdd-reviewer.toml").unlink()
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical agent set", result.stderr)

    def test_extra_sdd_agent_fails(self) -> None:
        # Break caught: an unexpected managed SDD agent is silently installed.
        (self.root / "agents/sdd-extra.toml").write_text('name = "sdd-extra"\n', encoding="utf-8")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical agent set", result.stderr)


    def test_invalid_state_schema_is_rejected(self) -> None:
        (self.root / "skills/sdd-workflow/schemas/operational-state.schema.json").write_text("{")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("state schema", result.stderr)


class CycleValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / "fixture"
        self.workspace = self.root / "mobile-app"
        self.workspace.mkdir(parents=True)
        self.artifact_directory = (
            self.root / "specs/20260806-143500-mobile-app-team-123-feature"
        )
        self.artifact_directory.mkdir(parents=True)
        self.manifest_path = self.artifact_directory / "sdd-cycle.json"
        self.manifest = {
            "schema_version": 1,
            "cycle_id": "20260806-143500",
            "workspace_root": str(self.workspace.resolve()),
            "speckit_root": str(self.root.resolve()),
            "primary_source": "TEAM-123",
            "source_ids": ["TEAM-123"],
            "artifact_directory": "specs/20260806-143500-mobile-app-team-123-feature",
            "artifacts": ["spec.md", "tasks.md"],
            "continuation_of": None,
        }
        self.write_manifest()
        (self.artifact_directory / "spec.md").write_text("# Feature\n", encoding="utf-8")
        (self.artifact_directory / "tasks.md").write_text("# Tasks\n\n- [ ] T001 First task\n", encoding="utf-8")
        feature = self.root / ".specify/feature.json"
        feature.parent.mkdir()
        feature.write_text(
            json.dumps({"feature_directory": self.manifest["artifact_directory"]}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_manifest(self) -> None:
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")

    def validate(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return self.run_validator(*self.external_identity_args("--new-cycle", *extra_args))

    def run_validator(
        self, *validator_args: str, expected_source: str = "TEAM-123"
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                PYTHON,
                str(SOURCE_ROOT / "skills/sdd-workflow/scripts/validate_cycle.py"),
                "--manifest",
                str(self.manifest_path),
                "--expected-workspace",
                str(self.workspace),
                "--expected-source",
                expected_source,
                *validator_args,
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def external_identity_args(self, *extra_args: str) -> list[str]:
        return [
            "--expected-cycle-id",
            "20260806-143500",
            "--expected-speckit-root",
            str(self.root),
            "--expected-artifact-directory",
            "specs/20260806-143500-mobile-app-team-123-feature",
            "--expected-source-id",
            "TEAM-123",
            *extra_args,
        ]

    def external_identity_args_for_source(
        self, source_id: str, *extra_args: str
    ) -> list[str]:
        args = self.external_identity_args(*extra_args)
        source_index = args.index("--expected-source-id") + 1
        args[source_index] = source_id
        return args

    def validate_with_external_identity(
        self, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        return self.validate(*extra_args)

    def test_valid_isolated_cycle_passes(self) -> None:
        # Break caught: a valid, self-contained cycle is rejected.
        result = self.validate("--require-tasks")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Cycle validation passed.", result.stdout)

    def test_external_identity_validates_the_complete_cycle(self) -> None:
        # Break caught: the manifest is trusted instead of the root-chat identity.
        result = self.validate_with_external_identity("--require-tasks")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_altered_cycle_id_fails_external_identity_check(self) -> None:
        # Break caught: a substituted manifest cycle ID is accepted.
        self.manifest["cycle_id"] = "20260806-999999"
        self.write_manifest()
        result = self.validate_with_external_identity()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cycle ID", result.stderr)

    def test_altered_speckit_root_fails_external_identity_check(self) -> None:
        # Break caught: a manifest redirects validation to another SpecKit root.
        self.manifest["speckit_root"] = str((self.root / "other-root").resolve())
        self.write_manifest()
        result = self.validate_with_external_identity()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("speckit root", result.stderr)

    def test_altered_artifact_directory_fails_external_identity_check(self) -> None:
        # Break caught: a manifest selects a different package than the assigned one.
        self.manifest["artifact_directory"] = "specs/other-cycle"
        self.write_manifest()
        result = self.validate_with_external_identity()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("artifact directory", result.stderr)

    def test_extra_source_id_fails_external_identity_check(self) -> None:
        # Break caught: an unassigned source is silently added to the manifest.
        self.manifest["source_ids"] = ["TEAM-123", "TEAM-456"]
        self.write_manifest()
        result = self.validate_with_external_identity()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source IDs", result.stderr)

    def test_missing_source_id_fails_external_identity_check(self) -> None:
        # Break caught: an assigned source is omitted from the manifest.
        self.manifest["source_ids"] = []
        self.write_manifest()
        result = self.validate_with_external_identity()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source IDs", result.stderr)

    def test_duplicate_source_id_fails_external_identity_check(self) -> None:
        # Break caught: duplicate source IDs evade set-only comparison.
        self.manifest["source_ids"] = ["TEAM-123", "TEAM-123"]
        self.write_manifest()
        result = self.validate_with_external_identity()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source IDs", result.stderr)

    def test_continuation_manifest_fails_new_cycle_identity_check(self) -> None:
        # Break caught: a continuation is accepted when a new cycle was assigned.
        self.manifest["continuation_of"] = "20260801-120000"
        self.write_manifest()
        result = self.validate_with_external_identity()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("new-cycle", result.stderr)

    def test_wrong_continuation_identity_fails_external_identity_check(self) -> None:
        # Break caught: a continuation from another cycle is accepted.
        self.manifest["continuation_of"] = "20260801-120000"
        self.write_manifest()
        result = self.run_validator(
            *self.external_identity_args(
                "--expected-continuation-of", "20260801-999999"
            )
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("continuation", result.stderr)

    def test_relative_sibling_package_reference_fails(self) -> None:
        # Break caught: a local ../ reference imports an artifact from another cycle.
        (self.artifact_directory / "spec.md").write_text(
            "See ../other-cycle/spec.md\n", encoding="utf-8"
        )
        result = self.validate_with_external_identity()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("relative artifact reference", result.stderr)

    def test_active_feature_mismatch_fails(self) -> None:
        # Break caught: bootstrap selects a different feature package.
        feature = self.root / ".specify/feature.json"
        feature.write_text(json.dumps({"feature_directory": "specs/other"}), encoding="utf-8")
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("active feature", result.stderr)

    def test_workspace_identity_mismatch_fails(self) -> None:
        # Break caught: the manifest belongs to a different workspace.
        self.manifest["workspace_root"] = str((self.root / "other-app").resolve())
        self.write_manifest()
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("workspace", result.stderr)

    def test_primary_source_mismatch_fails(self) -> None:
        # Break caught: the requested source is not the cycle's primary source.
        self.manifest["primary_source"] = "TEAM-456"
        self.write_manifest()
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("primary source", result.stderr)

    def test_unlisted_artifact_fails(self) -> None:
        # Break caught: an ungoverned file is added to the cycle package.
        (self.artifact_directory / "plan.md").write_text("# Plan\n", encoding="utf-8")
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("artifacts", result.stderr)

    def test_nested_control_manifest_is_an_unlisted_artifact(self) -> None:
        # Break caught: a nested sdd-cycle.json evades the governed inventory.
        nested_manifest = self.artifact_directory / "contracts/sdd-cycle.json"
        nested_manifest.parent.mkdir()
        nested_manifest.write_text("{}", encoding="utf-8")
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("artifacts", result.stderr)

    def test_cross_spec_reference_fails(self) -> None:
        # Break caught: a listed artifact imports planning context from another package.
        (self.artifact_directory / "spec.md").write_text(
            "See specs/other-feature/spec.md\n", encoding="utf-8"
        )
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("cross-package", result.stderr)

    def test_foreign_jira_key_fails(self) -> None:
        # Break caught: a listed artifact cites an unauthorized Jira source.
        (self.artifact_directory / "spec.md").write_text("Depends on TEAM-456\n", encoding="utf-8")
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("unauthorized Jira", result.stderr)

    def test_authorized_jira_url_and_speckit_ids_pass(self) -> None:
        # Regression: PVAPP-807, FR-001, and SC-001 were all rejected as foreign Jira keys.
        jira_url = "https://ports-tech.atlassian.net/browse/PVAPP-807"
        self.manifest["primary_source"] = jira_url
        self.manifest["source_ids"] = [jira_url]
        self.write_manifest()
        (self.artifact_directory / "spec.md").write_text(
            "Ticket PVAPP-807\nRequirement FR-001\nSuccess SC-001\n",
            encoding="utf-8",
        )
        result = self.run_validator(
            *self.external_identity_args_for_source(jira_url, "--new-cycle"),
            expected_source=jira_url,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_other_ticket_from_authorized_jira_project_fails(self) -> None:
        # Regression: isolation must still reject a different ticket in the same project.
        jira_url = "https://ports-tech.atlassian.net/browse/PVAPP-807"
        self.manifest["primary_source"] = jira_url
        self.manifest["source_ids"] = [jira_url]
        self.write_manifest()
        (self.artifact_directory / "spec.md").write_text(
            "Copied from PVAPP-806\n", encoding="utf-8"
        )
        result = self.run_validator(
            *self.external_identity_args_for_source(jira_url, "--new-cycle"),
            expected_source=jira_url,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("unauthorized Jira key", result.stderr)

    def test_tasks_must_start_at_t001(self) -> None:
        # Break caught: a cycle inherits task numbering from another package.
        (self.artifact_directory / "tasks.md").write_text("- [ ] T002 Second task\n", encoding="utf-8")
        result = self.validate("--require-tasks")
        self.assertEqual(result.returncode, 1)
        self.assertIn("T001", result.stderr)

    def test_artifact_symlink_escape_fails(self) -> None:
        # Break caught: a governed artifact resolves outside its package.
        outside = self.root / "outside.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        (self.artifact_directory / "spec.md").unlink()
        (self.artifact_directory / "spec.md").symlink_to(outside)
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("symlink", result.stderr)

    def test_active_feature_symlink_fails(self) -> None:
        # Break caught: the active-feature control path follows a symlink.
        feature = self.root / ".specify/feature.json"
        target = self.root / "feature-target.json"
        target.write_text(feature.read_text(encoding="utf-8"), encoding="utf-8")
        feature.unlink()
        feature.symlink_to(target)
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("ERROR: symlink", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_utf8_manifest_fails_with_actionable_error(self) -> None:
        # Break caught: an invalid manifest encoding escapes the error contract.
        self.manifest_path.write_bytes(b"\xff")
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("ERROR: cannot read JSON file", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_utf8_artifact_fails_with_actionable_error(self) -> None:
        # Break caught: an invalid artifact encoding escapes the error contract.
        (self.artifact_directory / "spec.md").write_bytes(b"\xff")
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("ERROR: cannot read listed artifact spec.md", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_utf8_tasks_fails_with_actionable_error(self) -> None:
        # Break caught: an invalid tasks encoding escapes the error contract.
        (self.artifact_directory / "tasks.md").write_bytes(b"\xff")
        result = self.validate("--require-tasks")
        self.assertEqual(result.returncode, 1)
        self.assertIn("ERROR: cannot read listed artifact tasks.md", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
