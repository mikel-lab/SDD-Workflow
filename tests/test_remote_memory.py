"""Regression contracts for agent-operated remote memory, not live agent tests."""

from __future__ import annotations

import json
import re
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills/sdd-workflow/references"


class RemoteMemoryPolicyTests(unittest.TestCase):
    def text(self, relative: str) -> str:
        path = ROOT / relative
        self.assertTrue(path.is_file(), f"Missing workflow contract: {relative}")
        return path.read_text(encoding="utf-8")

    def memory(self) -> str:
        return self.text("skills/sdd-workflow/references/remote-memory.md")

    def test_remote_reference_is_conditional_not_a_role_startup_dependency(self):
        # Break caught: every role loads the detailed archival procedure routinely.
        skill = self.text("skills/sdd-workflow/SKILL.md")
        self.assertIn("## Remote Memory (Conditional)", skill)
        self.assertIn("references/remote-memory.md", skill)
        self.assertNotIn("remote-memory.md", skill.split("## Quick Reference", 1)[1])
        self.assertIn("Do not read the remote index at intake", skill)

    def test_example_config_is_parseable_and_has_an_explicit_destination(self):
        # Break caught: the documented setup cannot identify a bounded destination.
        matches = re.findall(r"```json\n(.*?)\n```", self.memory(), re.S)
        self.assertTrue(matches, "No JSON configuration example")
        config = json.loads(matches[0])
        self.assertEqual(config["schema_version"], 1)
        self.assertTrue(config["project_id"])
        self.assertRegex(config["source_repository"], r"^[^/]+/[^/]+$")
        docs = config["documentation"]
        self.assertRegex(docs["repository"], r"^[^/]+/[^/]+$")
        self.assertNotEqual(config["source_repository"], docs["repository"])
        self.assertEqual(docs["index"], "INDEX.md")
        self.assertEqual(docs["root"], ".")
        self.assertTrue(docs["branch"])
        self.assertIs(docs["cleanup_local_after_verification"], False)
        self.assertNotRegex(json.dumps(config).lower(), r'"(?:token|password|secret)"')

    def test_setup_checks_identity_authority_and_path_boundaries(self):
        text = self.memory()
        for term in (
            "workspace_root", "source_repository", "authorized destination",
            "Do not guess", "private", "absolute paths", "..", "symlinks",
            "credentials", "fork", "not_configured",
        ):
            with self.subTest(term=term):
                self.assertIn(term, " ".join(text.split()))

    def test_lookup_requires_a_question_and_stops_when_answered(self):
        text = self.memory()
        for term in (
            "concrete unresolved question", "current request, code and tests",
            "only the selected", "Stop when the question is answered",
            "read-only", "not instructions",
        ):
            with self.subTest(term=term):
                self.assertIn(term, " ".join(text.split()))

    def test_history_provenance_is_separate_from_active_artifacts(self):
        contracts = self.text("skills/sdd-workflow/references/contracts.md")
        for heading in ("## Planner Result", "## Implementer Result", "## Reviewer Result"):
            section = contracts.split(heading, 1)[1].split("\n## ", 1)[0]
            self.assertIn("historical_reads:", section)
        self.assertIn("## Historical Read Record", contracts)
        for field in ("question:", "repository:", "revision:", "paths:", "conclusion:"):
            self.assertIn(field, contracts)
        self.assertIn("Do not add historical reads to `source_ids`", contracts)

    def test_existing_source_boundaries_have_only_the_named_exception(self):
        sources = self.text("skills/sdd-workflow/references/sources-and-artifacts.md")
        self.assertIn("must not use an active feature as a selection input", sources)
        self.assertIn("Do not use `find`, `rg`, globbing, or equivalent", sources)
        self.assertIn("only exception", sources)
        self.assertIn("historical_reads", sources)
        self.assertIn("validator never discovers sibling packages", sources)
        self.assertIn("No other path under `.specify/`", sources)

    def test_planner_and_root_keep_separate_read_channels(self):
        for path in (
            "skills/sdd-workflow/references/planner.md",
            "skills/sdd-workflow/references/orchestrator.md",
            "agents/sdd-planner.toml",
            "agents/sdd-reviewer.toml",
        ):
            with self.subTest(path=path):
                text = self.text(path)
                self.assertIn("historical_reads", text)
                self.assertIn("artifact_reads", text)
                self.assertIn("remote-memory.md", text)

    def test_historical_consultation_never_reactivates_a_cycle(self):
        text = self.memory()
        for term in (
            "never continuation", "Do not copy an old manifest",
            "frozen baseline", "normal planning review",
            "Do not forward the full archive",
        ):
            with self.subTest(term=term):
                self.assertIn(term, " ".join(text.split()))

    def test_archive_runs_in_session_without_github_automation_or_clone(self):
        text = self.memory()
        for term in (
            "same session", "No GitHub Actions", "no PR synchronization",
            "Do not clone", "single publishing owner", "authenticated GitHub",
        ):
            with self.subTest(term=term):
                self.assertIn(term, " ".join(text.split()))

    def test_archive_and_index_are_verified_before_any_cleanup(self):
        text = self.memory()
        for term in (
            "SHA-256", "read back", "remote commit", "index entry",
            "retain local files", "Keep unrelated index entries",
            "never force-push", "archive_status", "immutable",
        ):
            with self.subTest(term=term):
                self.assertIn(term, " ".join(text.split()))
        self.assertLess(text.index("### Verify"), text.index("### Local cleanup"))

    def test_cleanup_is_opt_in_bounded_and_never_breaks_active_work(self):
        text = self.memory()
        for term in (
            "cleanup_local_after_verification", "default false", "still active",
            "tracked files", "exact inventoried", "Never recursively delete",
            "configuration", "templates", "excluded",
        ):
            with self.subTest(term=term):
                self.assertIn(term, " ".join(text.split()))

    def test_import_is_explicit_bounded_and_does_not_invent_implementation_state(self):
        text = self.memory()
        for term in (
            "## Explicit Local History Import", "one project at a time",
            "user-authorized local roots", "outside a development cycle",
            "integration unverified", "original structure", "Do not rerun",
            "Do not rewrite Git history",
        ):
            with self.subTest(term=term):
                self.assertIn(term, " ".join(text.split()))

    def test_archive_metadata_does_not_modify_frozen_cycle_files(self):
        text = self.memory()
        for term in (
            "archive.json", "source_revision", "source_state", "unknown",
            "artifacts/", "original `sdd-cycle.json`", "dirty",
        ):
            with self.subTest(term=term):
                self.assertIn(term, " ".join(text.split()))

    def test_completion_reports_archive_failures_without_faking_task_failure(self):
        lifecycle = self.text("skills/sdd-workflow/references/lifecycle-and-gates.md")
        self.assertIn("## Remote Archive at Closure", lifecycle)
        self.assertIn("archive_status", lifecycle)
        self.assertIn("does not change the final Reviewer verdict", lifecycle)
        self.assertIn("same session", lifecycle)
        self.assertIn("pending", lifecycle)

    def test_distribution_includes_new_reference_and_regressions(self):
        data = runpy.run_path(str(ROOT / "scripts/validate.py"))
        self.assertIn("remote-memory.md", data["REFERENCE_NAMES"])
        files = data["EXPECTED_FILES"]
        self.assertIn(Path("tests/test_remote_memory.py"), files)
        self.assertIn(Path("skills/sdd-workflow/references/remote-memory.md"), files)
        self.assertEqual(len(files), len(set(files)))
        self.assertEqual(len(files), 27)

    def test_readme_explains_activation_and_limits(self):
        text = self.text("README.md")
        for term in (
            ".sdd/config.json", "INDEX.md", "remote-memory.md",
            "does not configure", "not a runtime interceptor", "27-file",
        ):
            with self.subTest(term=term):
                self.assertIn(term, " ".join(text.split()))


if __name__ == "__main__":
    unittest.main()
