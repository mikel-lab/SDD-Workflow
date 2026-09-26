"""Static regression guards for delegation instructions and their contracts.

These tests inspect the shipped policy, not a live Codex session. They cannot
prove model selection, context isolation, agent compliance, or usage savings.
"""

from __future__ import annotations

import re
import runpy
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills/sdd-workflow/references"
EXPECTED_AGENTS = {
    "sdd-planner.toml": ("sdd-planner", "gpt-6-sol", "high", "workspace-write"),
    "sdd-implementer-main.toml": ("sdd-implementer-main", "gpt-6-sol", "medium", "workspace-write"),
    "sdd-implementer-high.toml": ("sdd-implementer-high", "gpt-6-sol", "high", "workspace-write"),
    "sdd-implementer-simple.toml": ("sdd-implementer-simple", "gpt-6-luna", "high", "workspace-write"),
    "sdd-reviewer.toml": ("sdd-reviewer", "gpt-6-sol", "high", "read-only"),
}


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
        cls.lifecycle = (REFERENCES / "lifecycle-and-gates.md").read_text(encoding="utf-8")
        cls.skill = (ROOT / "skills/sdd-workflow/SKILL.md").read_text(encoding="utf-8")
        cls.policy = section(cls.orchestrator, "Agent Spawn Policy")
        cls.record = section(cls.contracts, "Delegation Record")
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.validator = runpy.run_path(str(ROOT / "scripts/validate.py"))

    def test_self_contained_tasks_explicitly_disable_history(self) -> None:
        self.assertIn("Self-contained assignments start without parent history", self.policy)
        self.assertIn("`fork_context=false`", self.policy)
        self.assertIn('`fork_turns="none"`', self.policy)

    def test_spawn_arguments_follow_the_exposed_schema(self) -> None:
        self.assertIn("exposed tool schema", self.policy)
        self.assertIn("Never send both", self.policy)
        self.assertIn("Do not rely on omitted-argument defaults", self.policy)
        self.assertIn("spawn arguments, not agent TOML settings", self.policy)

    def test_history_exceptions_are_limited_and_justified(self) -> None:
        self.assertIn("positive integer string", self.policy)
        self.assertIn("Full history requires a recorded task-specific reason", self.policy)
        self.assertIn("Do not inherit unrelated cycles", self.policy)

    def test_unknown_context_control_is_not_presented_as_isolation(self) -> None:
        self.assertIn("cannot control history", self.policy)
        self.assertIn("not verified", self.policy)
        self.assertIn("cycle isolation cannot be maintained", self.policy)

    def test_context_reduction_preserves_required_inputs(self) -> None:
        for required in (
            "explicit user decisions", "mandatory skill", "Cycle Identity Handoff",
            "owned and prohibited paths", "checks", "required result contract",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.policy)
        self.assertIn("byte for byte", self.policy)

    def test_role_selection_is_not_just_a_prompt_label(self) -> None:
        self.assertIn("role-selection control", self.policy)
        self.assertIn("not a configuration change", self.policy)
        self.assertIn("cannot apply the required profile", self.policy)
        self.assertIn("before delegating", self.policy)

    def test_parent_maximum_effort_does_not_replace_role_routing(self) -> None:
        self.assertIn("Do not inherit maximum effort", self.policy)
        self.assertIn("canonical TOML", self.policy)
        self.assertIn("Main/High exclusion", self.policy)

    def test_canonical_model_and_effort_matrix_matches_role_profiles(self) -> None:
        # Both the validator and actual TOMLs must implement the approved policy.
        self.assertEqual(self.validator["CANONICAL_AGENTS"], EXPECTED_AGENTS)
        for filename, expected in EXPECTED_AGENTS.items():
            with self.subTest(filename=filename):
                data = tomllib.loads((ROOT / "agents" / filename).read_text(encoding="utf-8"))
                actual = tuple(data.get(key) for key in (
                    "name", "model", "model_reasoning_effort", "sandbox_mode",
                ))
                self.assertEqual(actual, expected)

    def test_effective_configuration_requires_runtime_evidence(self) -> None:
        self.assertIn("runtime metadata", self.policy)
        self.assertIn("self-report", self.policy)
        self.assertIn("not verified", self.policy)
        self.assertIn("confirmed mismatch", self.policy)
        self.assertIn("preserve evidence", self.policy)

    def test_missing_metadata_does_not_create_an_approval_gate(self) -> None:
        self.assertIn("Missing runtime metadata alone does not add an approval gate", self.policy)
        self.assertIn("not Reviewer verdicts", self.record)

    def test_review_context_is_neutral_without_restart_on_small_deltas(self) -> None:
        self.assertIn("neutral review brief", self.policy)
        self.assertIn("desired verdict", self.policy)
        self.assertIn("same Reviewer", self.policy)
        self.assertIn("focused delta re-review", self.policy)

    def test_progress_updates_do_not_ping_the_active_agent(self) -> None:
        monitoring = section(self.orchestrator, "Delegated Action Monitoring")
        self.assertIn("User-facing status updates do not require messages to the active agent", monitoring)
        self.assertIn("Do not send routine progress messages", monitoring)
        self.assertIn("Prefer non-interrupting follow-ups", monitoring)
        self.assertIn("timeout is not a failure", monitoring)
        self.assertIn("Never interrupt, close, or replace", monitoring)

    def test_delegation_record_separates_requested_and_effective_values(self) -> None:
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
        self.assertIn("in the root chat", self.record)
        self.assertIn("not a new governed artifact", self.record)
        self.assertIn("Do not create another agent or review", self.record)
        self.assertIn("delegation:", section(self.contracts, "Orchestrator Status"))

    def test_literal_cycle_identity_handoff_is_preserved(self) -> None:
        handoff = section(self.contracts, "Cycle Identity Handoff")
        self.assertIn("reuse it byte for byte", handoff)
        self.assertIn("must not be abbreviated", handoff)
        for field in (
            "manifest", "cycle_id", "workspace_root", "speckit_root", "primary_source",
            "source_ids", "artifact_directory", "identity_mode", "cycle_validation_command",
        ):
            self.assertIn(f"{field}:", handoff)

    def test_distribution_inventory_matches_native_only_package(self) -> None:
        inventory = self.validator["EXPECTED_FILES"]
        self.assertIn(Path("tests/test_delegation_policy.py"), inventory)
        self.assertIn(Path(".github/workflows/validate.yml"), inventory)
        self.assertEqual(len(inventory), len(set(inventory)))
        self.assertEqual(len(inventory), 27)
        self.assertEqual(len(self.validator["REFERENCE_NAMES"]), 8)
        self.assertIn("27-file distribution", self.readme)
        self.assertIn("eight direct skill references", self.readme)

    def test_readme_runs_all_python_tests_and_states_their_limits(self) -> None:
        self.assertIn("python3 -m unittest discover -s tests -v", self.readme)
        self.assertIn("not a live Codex execution", self.readme)

    def test_plan_review_validation_and_freeze_open_implementation_automatically(self) -> None:
        gate = section(self.orchestrator, "Freeze and Begin Implementation")
        self.assertIn("proceed directly to implementation", gate)
        self.assertIn("Do not request user approval of the plan", gate)
        self.assertIn("frozen artifact set is unchanged", gate)
        self.assertIn("invalidates the review and implementation eligibility", gate)

    def test_retired_external_execution_contract_is_absent(self) -> None:
        # The old mechanism must disappear, not merely be renamed or disabled.
        self.assertFalse((REFERENCES / "luna-lane.md").exists())
        paths = [ROOT / "README.md", *ROOT.glob("docs/*.md"),
                 *ROOT.glob("agents/*.toml"), *ROOT.glob("skills/**/*.md")]
        retired = re.compile(
            r"luna[- ]lane|visible Luna|isolated Luna|Luna pre-integration|"
            r"Luna post-integration|gpt-5\.6|Approved,\s*implement",
            re.IGNORECASE,
        )
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIsNone(retired.search(path.read_text(encoding="utf-8")))

    def test_root_profile_is_sol_medium_without_another_coordinator(self) -> None:
        for content in (self.readme, self.skill, self.orchestrator):
            with self.subTest(content=content[:40]):
                self.assertIn("gpt-6-sol", content)
                self.assertIn("medium", content)
        self.assertFalse((ROOT / "agents/sdd-orchestrator.toml").exists())

    def test_simple_is_native_and_cannot_delegate_recursively(self) -> None:
        implementers = (REFERENCES / "implementers.md").read_text(encoding="utf-8")
        self.assertIn("at most two concurrent Simple", implementers)
        self.assertIn("Only the root chat may dispatch", self.policy)
        self.assertIn("Do not enable automatic delegation", self.policy)
        self.assertIn("native subagent", implementers)
        self.assertIn("gpt-6-luna", implementers)

    def test_user_attention_requires_an_unavoidable_user_owned_blocker(self) -> None:
        autonomy = section(self.lifecycle, "Autonomous Execution and User Attention")
        for rule in (
            "The task request authorizes", "Do not request a confirmation phrase",
            "safe in-scope recovery", "only the user can supply", "before the affected action",
            "explicit user pause", "access controls",
        ):
            self.assertIn(rule, autonomy)
        attention = section(self.contracts, "User Attention Request")
        for field in ("blocker", "evidence", "attempted_recovery", "why_user", "required_input", "affected_scope"):
            self.assertIn(f"{field}:", attention)

    def test_retry_limit_triggers_internal_escalation_not_plan_approval(self) -> None:
        repeated = section(self.lifecycle, "Repeated Conditions")
        self.assertIn("three", repeated)
        self.assertIn("internal escalation", repeated)
        self.assertIn("not a user-approval gate", repeated)
        self.assertIn("Do not repeat an unchanged failing strategy", repeated)
        self.assertIn("User Attention", repeated)

    def test_operational_checkpoint_does_not_mutate_approved_artifacts(self) -> None:
        checkpoint = section(self.contracts, "Orchestrator Checkpoint")
        for field in ("cycle_id", "state", "baseline", "decisions", "assignments", "dependencies", "reviews", "next_transition"):
            self.assertIn(f"{field}:", checkpoint)
        self.assertIn("not a governed planning artifact", checkpoint)
        self.assertIn("Do not redispatch", checkpoint)
        self.assertIn("Orchestrator Checkpoint", self.orchestrator)

    def test_write_producing_checks_return_to_implementer_without_user_prompt(self) -> None:
        reviewer = (REFERENCES / "reviewer.md").read_text(encoding="utf-8")
        self.assertIn("write-producing checks", reviewer)
        self.assertIn("assigned implementer", reviewer)
        self.assertIn("unchanged reviewed baseline", reviewer)
        self.assertIn("not a reason to ask the user", reviewer)


if __name__ == "__main__":
    unittest.main()
