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

    def test_evidenced_discipline_guidance_exists(self) -> None:
        # Break caught: demonstrated gate and persistence rationalizations ship
        # without the required rationalization, red-flag, and mistake guidance.
        lifecycle = (self.root / "skills/sdd-workflow/references/lifecycle-and-gates.md").read_text(
            encoding="utf-8"
        )
        sources = (self.root / "skills/sdd-workflow/references/sources-and-artifacts.md").read_text(
            encoding="utf-8"
        )

        for content in (lifecycle, sources):
            self.assertIn("## Common Mistakes", content)
            self.assertIn("### Rationalization Table", content)
            self.assertIn("### Red Flags", content)

        self.assertIn("`approved, go ahead`", lifecycle)
        self.assertIn("safer or more reversible", sources)

    def test_speckit_bootstrap_boundary_is_documented(self) -> None:
        # Break caught: the official speckit-specify bootstrap write is rejected
        # or an unbounded .specify write exception is introduced.
        sources = (self.root / "skills/sdd-workflow/references/sources-and-artifacts.md").read_text(
            encoding="utf-8"
        )
        planner = (self.root / "skills/sdd-workflow/references/planner.md").read_text(
            encoding="utf-8"
        )
        orchestrator = (
            self.root / "skills/sdd-workflow/references/orchestrator.md"
        ).read_text(encoding="utf-8")
        planner_agent = (self.root / "agents/sdd-planner.toml").read_text(encoding="utf-8")

        for content in (sources, planner, orchestrator, planner_agent):
            self.assertIn(".specify/feature.json", content)
        self.assertIn("No other path under `.specify/`", sources)
        self.assertIn("changed_paths", planner)
        self.assertIn("changed_paths", orchestrator)

    def test_external_executor_convergence_is_compatible(self) -> None:
        # Break caught: convergence invokes speckit-converge after a native or
        # Luna executor even though its contract requires speckit-implement.
        skill = (self.root / "skills/sdd-workflow/SKILL.md").read_text(encoding="utf-8")
        planner = (self.root / "skills/sdd-workflow/references/planner.md").read_text(
            encoding="utf-8"
        )
        reviewer = (self.root / "skills/sdd-workflow/references/reviewer.md").read_text(
            encoding="utf-8"
        )

        for content in (skill, planner, reviewer):
            self.assertIn("speckit-tasks", content)
            self.assertIn("speckit-implement", content)
        self.assertIn("always runs `speckit-analyze`", reviewer)
        self.assertIn("fresh planning review and exact approval", planner)

    def test_normal_path_has_one_planning_and_one_final_review(self) -> None:
        # Break caught: the routine path schedules extra implementation or
        # convergence reviews instead of one planning and one final review.
        lifecycle = (
            self.root / "skills/sdd-workflow/references/lifecycle-and-gates.md"
        ).read_text(encoding="utf-8")
        orchestrator = (
            self.root / "skills/sdd-workflow/references/orchestrator.md"
        ).read_text(encoding="utf-8")
        reviewer_agent = (self.root / "agents/sdd-reviewer.toml").read_text(
            encoding="utf-8"
        )

        self.assertIn("planning Reviewer", lifecycle)
        self.assertIn("final Reviewer", lifecycle)
        self.assertIn("Normal batches use implementer verification until final review", orchestrator)
        self.assertNotIn("required independent review after every native batch", orchestrator)
        self.assertIn("Normal batches rely on implementer verification until final review", reviewer_agent)
        self.assertNotIn(
            "Review completed native implementation batches and perform a separate final integrated review when assigned.",
            reviewer_agent,
        )

    def test_minor_planning_correction_uses_focused_delta_rereview(self) -> None:
        # Break caught: a bounded planning fix automatically repeats a whole
        # package review rather than the same Reviewer's focused delta review.
        lifecycle = (
            self.root / "skills/sdd-workflow/references/lifecycle-and-gates.md"
        ).read_text(encoding="utf-8")
        planner = (self.root / "skills/sdd-workflow/references/planner.md").read_text(
            encoding="utf-8"
        )

        for content in (lifecycle, planner):
            self.assertIn("focused delta re-review", content)
        self.assertIn("material changes to scope, architecture, acceptance criteria, source set, or artifact identity", lifecycle)

    def test_normal_microtasks_do_not_each_require_independent_review(self) -> None:
        # Break caught: a normal coherent batch is split into reviewer work for
        # every small task although no risk trigger applies.
        orchestrator = (
            self.root / "skills/sdd-workflow/references/orchestrator.md"
        ).read_text(encoding="utf-8")
        implementers = (
            self.root / "skills/sdd-workflow/references/implementers.md"
        ).read_text(encoding="utf-8")
        reviewer_agent = (self.root / "agents/sdd-reviewer.toml").read_text(
            encoding="utf-8"
        )

        self.assertIn("coherent dependency-ready batch", orchestrator)
        self.assertIn("not one agent per task entry", implementers)
        self.assertIn("do not commission an independent review for each microtask", orchestrator)
        self.assertIn("no intermediate review for normal batches", reviewer_agent)

    def test_high_risk_batches_still_require_review(self) -> None:
        # Break caught: reducing routine review omits independent review for a
        # high-risk, security, migration, API, or critical shared-code batch.
        orchestrator = (
            self.root / "skills/sdd-workflow/references/orchestrator.md"
        ).read_text(encoding="utf-8")
        reviewer = (self.root / "skills/sdd-workflow/references/reviewer.md").read_text(
            encoding="utf-8"
        )
        reviewer_agent = (self.root / "agents/sdd-reviewer.toml").read_text(
            encoding="utf-8"
        )

        for trigger in (
            "high-risk batch",
            "security",
            "persistence/migration",
            "API contract",
            "critical shared code",
        ):
            self.assertIn(trigger, orchestrator)
            self.assertIn(trigger, reviewer_agent)
        self.assertIn("Intermediate-risk batch review", reviewer)

    def test_luna_keeps_pre_and_post_integration_reviews(self) -> None:
        # Break caught: Luna's isolation and integration safeguards are folded
        # into the normal review budget.
        orchestrator = (
            self.root / "skills/sdd-workflow/references/orchestrator.md"
        ).read_text(encoding="utf-8")
        reviewer = (self.root / "skills/sdd-workflow/references/reviewer.md").read_text(
            encoding="utf-8"
        )
        reviewer_agent = (self.root / "agents/sdd-reviewer.toml").read_text(
            encoding="utf-8"
        )

        self.assertIn("Luna pre-integration", orchestrator)
        self.assertIn("Luna post-integration", orchestrator)
        self.assertIn("Before integration", reviewer)
        self.assertIn("After Main integrates", reviewer)
        self.assertIn("Luna pre-integration", reviewer_agent)
        self.assertIn("Luna post-integration", reviewer_agent)

    def test_final_reviewer_combines_speckit_analyze_and_final_verdict(self) -> None:
        # Break caught: reconciliation schedules a duplicate whole-package
        # review rather than returning one integrated final verdict.
        skill = (self.root / "skills/sdd-workflow/SKILL.md").read_text(encoding="utf-8")
        reviewer = (self.root / "skills/sdd-workflow/references/reviewer.md").read_text(
            encoding="utf-8"
        )
        reviewer_agent = (self.root / "agents/sdd-reviewer.toml").read_text(
            encoding="utf-8"
        )

        self.assertIn("final Reviewer runs read-only `speckit-analyze` and returns the integrated verdict in the same action", skill)
        self.assertIn("same final-review action", reviewer)
        self.assertIn("Do not schedule an identical whole-package review afterward", reviewer)
        self.assertIn("final Reviewer runs read-only `speckit-analyze`", reviewer_agent)
        self.assertIn("reconciliation and integrated verdict in the same action", reviewer_agent)

    def test_root_chat_is_declared_as_sole_orchestrator(self) -> None:
        # Break caught: a configured agent competes with the invoking chat for
        # coordination and user contact.
        skill = (self.root / "skills/sdd-workflow/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Root Chat Authority", skill)
        self.assertIn("sole coordination and user-contact authority", skill)

    def test_root_chat_must_not_dispatch_sdd_orchestrator(self) -> None:
        # Break caught: the root chat delegates its governing role to an
        # additional orchestrator agent.
        skill = (self.root / "skills/sdd-workflow/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("must not dispatch `sdd-orchestrator`", skill)

    def test_retired_orchestrator_agent_is_not_distributed(self) -> None:
        # Break caught: root-chat coordination still ships a competing managed
        # sdd-orchestrator agent.
        self.assertFalse((self.root / "agents/sdd-orchestrator.toml").exists())

    def test_new_cycle_ignores_active_feature_as_selection_input(self) -> None:
        # Break caught: a historical active package becomes input for a new
        # request before that request has its own identity and manifest.
        sources = (
            self.root / "skills/sdd-workflow/references/sources-and-artifacts.md"
        ).read_text(encoding="utf-8")
        self.assertIn("must not use an active feature as a selection input", sources)

    def test_explicit_feature_directory_is_mandatory(self) -> None:
        # Break caught: speckit-specify chooses a package implicitly instead
        # of the cycle's explicitly assigned directory.
        planner = (self.root / "skills/sdd-workflow/references/planner.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("SPECIFY_FEATURE_DIRECTORY", planner)
        self.assertIn("assigned artifact_directory", planner)

    def test_historical_spec_discovery_is_forbidden(self) -> None:
        # Break caught: broad filesystem discovery reopens an unrelated
        # historical feature package.
        sources = (
            self.root / "skills/sdd-workflow/references/sources-and-artifacts.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Do not use `find`, `rg`, globbing, or equivalent", sources)

    def test_planner_and_reviewer_report_artifact_reads(self) -> None:
        # Break caught: either role omits a required cycle-isolation result
        # field, including an auditable record of artifact reads and writes.
        contracts = (self.root / "skills/sdd-workflow/references/contracts.md").read_text(
            encoding="utf-8"
        )
        planner_agent = (self.root / "agents/sdd-planner.toml").read_text(encoding="utf-8")
        reviewer_agent = (self.root / "agents/sdd-reviewer.toml").read_text(encoding="utf-8")

        planner_result = contracts.split("## Planner Result", 1)[1].split(
            "## Implementation Brief", 1
        )[0]
        reviewer_result = contracts.split("## Reviewer Result", 1)[1]
        required_fields = (
            "cycle_id",
            "source_ids",
            "artifact_directory",
            "artifact_reads",
            "changed_paths",
            "cycle_validation_command",
            "cycle_validation_result",
        )

        for field in required_fields:
            self.assertIn(f"{field}:", planner_result)
            self.assertIn(f"{field}:", reviewer_result)
            self.assertIn(field, planner_agent)
            self.assertIn(field, reviewer_agent)

    def test_continuation_requires_explicit_request_and_identity_match(self) -> None:
        # Break caught: a related request silently reuses an existing package
        # without a user-directed continuation or matching identity.
        sources = (
            self.root / "skills/sdd-workflow/references/sources-and-artifacts.md"
        ).read_text(encoding="utf-8")
        self.assertIn("only on explicit user continuation intent", sources)
        self.assertIn("workspace and primary-source identities must match", sources)

    def test_readme_documents_runtime_dependencies(self) -> None:
        # Break caught: operators install the workflow without required SpecKit,
        # Superpowers, or connector capabilities being declared.
        readme = (self.root / "README.md").read_text(encoding="utf-8")

        for dependency in (
            "speckit-specify",
            "speckit-clarify",
            "speckit-checklist",
            "speckit-plan",
            "speckit-tasks",
            "speckit-analyze",
            "speckit-converge",
            "test-driven-development",
            "systematic-debugging",
            "receiving-code-review",
            "verification-before-completion",
            "dispatching-parallel-agents",
            "Jira",
            "Figma",
        ):
            self.assertIn(dependency, readme)

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
        agent = self.root / "agents/sdd-planner.toml"
        agent.write_text("name = [\n", encoding="utf-8")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid TOML", result.stderr)
        self.assertIn("sdd-planner.toml", result.stderr)

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
        return subprocess.run(
            [
                PYTHON,
                str(SOURCE_ROOT / "skills/sdd-workflow/scripts/validate_cycle.py"),
                "--manifest",
                str(self.manifest_path),
                "--expected-workspace",
                str(self.workspace),
                "--expected-source",
                "TEAM-123",
                *extra_args,
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_isolated_cycle_passes(self) -> None:
        # Break caught: a valid, self-contained cycle is rejected.
        result = self.validate("--require-tasks")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Cycle validation passed.", result.stdout)

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
        result = subprocess.run(
            [
                PYTHON,
                str(SOURCE_ROOT / "skills/sdd-workflow/scripts/validate_cycle.py"),
                "--manifest",
                str(self.manifest_path),
                "--expected-workspace",
                str(self.workspace),
                "--expected-source",
                "TEAM-456",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
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
