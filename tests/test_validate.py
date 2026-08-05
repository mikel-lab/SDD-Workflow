"""Behavioral tests for the standalone distribution validator.

Each test names the repository break it must catch; the validator is run as a
real command against a disposable copy of the full distribution.
"""

from __future__ import annotations

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
        orchestrator_agent = (self.root / "agents/sdd-orchestrator.toml").read_text(
            encoding="utf-8"
        )

        for content in (sources, planner, orchestrator, planner_agent, orchestrator_agent):
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
        orchestrator_agent = (self.root / "agents/sdd-orchestrator.toml").read_text(
            encoding="utf-8"
        )

        for content in (skill, planner, reviewer, orchestrator_agent):
            self.assertIn("speckit-tasks", content)
            self.assertIn("speckit-implement", content)
        self.assertIn("always runs `speckit-analyze`", reviewer)
        self.assertIn("fresh planning review and exact approval", planner)

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


if __name__ == "__main__":
    unittest.main()
