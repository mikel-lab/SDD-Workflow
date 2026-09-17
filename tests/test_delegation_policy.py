"""Static regression guards for delegation instructions and their contracts.

These tests inspect the shipped policy, not a live Codex session. They cannot
prove model selection, context isolation, agent compliance, or usage savings.
"""

from __future__ import annotations

import re
import runpy
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills/sdd-workflow/references"


def section(text: str, heading: str) -> str:
    """Return one level-two section, or empty text for a missing section."""
    marker = f"## {heading}\n"
    if marker not in text:
        return ""
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


class DelegationPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.orchestrator = (REFERENCES / "orchestrator.md").read_text(encoding="utf-8")
        cls.contracts = (REFERENCES / "contracts.md").read_text(encoding="utf-8")
        cls.policy = section(cls.orchestrator, "Agent Spawn Policy")
        cls.record = section(cls.contracts, "Delegation Record")
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        # The validator's __main__ is not executed; this loads its real inventory.
        cls.validator = runpy.run_path(str(ROOT / "scripts/validate.py"))

    def test_self_contained_tasks_explicitly_disable_history(self) -> None:
        # Regression: a compact prompt still forks the entire parent history.
        self.assertIn("Self-contained assignments start without parent history", self.policy)
        self.assertIn("`fork_context=false`", self.policy)
        self.assertIn('`fork_turns="none"`', self.policy)

    def test_spawn_arguments_follow_the_exposed_schema(self) -> None:
        # Regression: a V1 argument is sent to V2, or a default is assumed.
        self.assertIn("exposed tool schema", self.policy)
        self.assertIn("Never send both", self.policy)
        self.assertIn("Do not rely on omitted-argument defaults", self.policy)
        self.assertIn("spawn arguments, not agent TOML settings", self.policy)

    def test_history_exceptions_are_limited_and_justified(self) -> None:
        # Regression: every difficult task silently inherits all conversation.
        self.assertIn("positive integer string", self.policy)
        self.assertIn("Full history requires a recorded task-specific reason", self.policy)
        self.assertIn("Do not inherit unrelated cycles", self.policy)

    def test_unknown_context_control_is_not_presented_as_isolation(self) -> None:
        # Regression: an unsupported context flag becomes an isolation claim.
        self.assertIn("cannot control history", self.policy)
        self.assertIn("not verified", self.policy)
        self.assertIn("cycle isolation cannot be maintained", self.policy)

    def test_context_reduction_preserves_required_inputs(self) -> None:
        # Regression: shortening the handoff removes authority or decisions.
        for required in (
            "explicit user decisions", "mandatory skill", "Cycle Identity Handoff",
            "owned and prohibited paths", "checks", "required result contract",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.policy)
        self.assertIn("byte for byte", self.policy)

    def test_role_selection_is_not_just_a_prompt_label(self) -> None:
        # Regression: a generic agent is labelled as a configured SDD role.
        self.assertIn("role-selection control", self.policy)
        self.assertIn("not a configuration change", self.policy)
        self.assertIn("cannot apply the required profile", self.policy)
        self.assertIn("before delegating", self.policy)

    def test_parent_maximum_effort_does_not_replace_role_routing(self) -> None:
        # Regression: the parent's maximum effort replaces task-based routing.
        self.assertIn("Do not inherit maximum effort", self.policy)
        self.assertIn("canonical TOML", self.policy)
        self.assertIn("Main/High exclusion", self.policy)

    def test_canonical_model_and_effort_matrix_is_unchanged(self) -> None:
        # Regression: this efficiency change silently changes model profiles.
        self.assertEqual(self.validator["CANONICAL_AGENTS"], {
            "sdd-planner.toml": ("sdd-planner", "gpt-6-astra", "low", "workspace-write"),
            "sdd-implementer-main.toml": ("sdd-implementer-main", "gpt-5.6-terra", "medium", "workspace-write"),
            "sdd-implementer-high.toml": ("sdd-implementer-high", "gpt-5.6-terra", "high", "workspace-write"),
            "sdd-implementer-simple.toml": ("sdd-implementer-simple", "gpt-5.6-terra", "low", "workspace-write"),
            "sdd-reviewer.toml": ("sdd-reviewer", "gpt-6-astra", "low", "read-only"),
        })

    def test_effective_configuration_requires_runtime_evidence(self) -> None:
        # Regression: TOML declarations or model self-report become proof.
        self.assertIn("runtime metadata", self.policy)
        self.assertIn("self-report", self.policy)
        self.assertIn("not verified", self.policy)
        self.assertIn("confirmed mismatch", self.policy)
        self.assertIn("preserve evidence", self.policy)

    def test_missing_metadata_does_not_create_an_approval_gate(self) -> None:
        # Regression: unavailable telemetry blocks otherwise supported work.
        self.assertIn("Missing runtime metadata alone does not add an approval gate", self.policy)
        self.assertIn("not Reviewer verdicts", self.record)

    def test_review_context_is_neutral_without_restart_on_small_deltas(self) -> None:
        # Regression: reviewers inherit advocacy, or every delta starts afresh.
        self.assertIn("neutral review brief", self.policy)
        self.assertIn("desired verdict", self.policy)
        self.assertIn("same Reviewer", self.policy)
        self.assertIn("focused delta re-review", self.policy)

    def test_progress_updates_do_not_ping_the_active_agent(self) -> None:
        # Regression: informing the user generates routine subagent messages.
        monitoring = section(self.orchestrator, "Delegated Action Monitoring")
        self.assertIn("User-facing status updates do not require messages to the active agent", monitoring)
        self.assertIn("Do not send routine progress messages", monitoring)
        self.assertIn("Prefer non-interrupting follow-ups", monitoring)
        self.assertIn("at most one non-interrupting status request", monitoring)
        self.assertIn("timeout is not a failure", monitoring)
        self.assertIn("Never interrupt, close, or replace", monitoring)

    def test_delegation_record_separates_requested_and_effective_values(self) -> None:
        # Regression: requested configuration is reported as observed state.
        match = re.search(r"```text\n(.*?)\n```", self.record, re.DOTALL)
        self.assertIsNotNone(match, "Missing Delegation Record template")
        fields = re.findall(r"^([a-z_]+):", match.group(1), re.MULTILINE)
        self.assertEqual(fields, [
            "agent_id", "requested_role", "requested_model", "requested_effort",
            "selection_evidence", "context_policy", "context_argument", "context_reason",
            "effective_model", "effective_effort", "runtime_evidence", "configuration_status",
        ])
        self.assertIn("verified | not verified | mismatch | blocked", self.record)

    def test_record_stays_in_root_chat_without_extra_artifacts(self) -> None:
        # Regression: telemetry creates a new governed artifact or review pass.
        self.assertIn("in the root chat", self.record)
        self.assertIn("not a new governed artifact", self.record)
        self.assertIn("Do not create another agent or review", self.record)
        status = section(self.contracts, "Orchestrator Status")
        self.assertIn("delegation:", status)

    def test_literal_cycle_identity_handoff_is_preserved(self) -> None:
        # Regression: context minimization abbreviates the cycle identity.
        handoff = section(self.contracts, "Cycle Identity Handoff")
        self.assertIn("reuse it byte for byte", handoff)
        self.assertIn("must not be abbreviated", handoff)
        for field in (
            "manifest", "cycle_id", "workspace_root", "speckit_root", "primary_source",
            "source_ids", "artifact_directory", "identity_mode", "cycle_validation_command",
        ):
            self.assertIn(f"{field}:", handoff)

    def test_distribution_inventory_includes_policy_tests_once(self) -> None:
        # Regression: the installer rejects the newly shipped regression tests.
        inventory = self.validator["EXPECTED_FILES"]
        self.assertIn(Path("tests/test_delegation_policy.py"), inventory)
        self.assertEqual(len(inventory), len(set(inventory)))
        self.assertEqual(len(inventory), 25)
        self.assertIn("25-file distribution", self.readme)

    def test_readme_runs_all_python_tests_and_states_their_limits(self) -> None:
        # Regression: the documented command silently skips the new test file.
        self.assertIn("python3 -m unittest discover -s tests -v", self.readme)
        self.assertIn("not a live Codex execution", self.readme)

    def test_efficiency_does_not_weaken_existing_approval_gates(self) -> None:
        # Regression: efficiency recommendations become authority to skip gates.
        gate = section(self.orchestrator, "Freeze and Exact Approval Gate")
        self.assertIn("case- and punctuation-sensitive string `Approved, implement.`", gate)
        self.assertIn("frozen artifact set is unchanged", gate)
        self.assertIn("invalidates the review and derived authorization", gate)

    def test_luna_keeps_its_separate_execution_contract(self) -> None:
        # Regression: Luna is silently treated as a native Simple subagent.
        self.assertIn("Luna remains governed by", self.policy)
        self.assertIn("[Luna Lane](luna-lane.md)", self.policy)


if __name__ == "__main__":
    unittest.main()
