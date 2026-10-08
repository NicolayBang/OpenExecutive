import importlib.util
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("council", Path(__file__).resolve().parents[1] / "scripts/council.py")
council = importlib.util.module_from_spec(spec)
spec.loader.exec_module(council)


def item(**fields):
    return {"type": "item.completed", "item": fields}


def transcript():
    return [
        item(type="collab_tool_call", tool="spawn_agent", status="completed",
             prompt="ROLE=finance\nReview cash.", receiver_thread_ids=["finance-thread"]),
        item(type="collab_tool_call", tool="spawn_agent", status="completed",
             prompt="ROLE=product\nReview roadmap.", receiver_thread_ids=["product-thread"]),
        item(type="collab_tool_call", tool="wait", agents_states={
            "finance-thread": {"status": "completed", "message": "Runway is five months."},
            "product-thread": {"status": "completed", "message": "Pilot first."}}),
        item(type="agent_message", text="Fund a small pilot; preserve the cash buffer."),
        {"type": "turn.completed"},
    ]


class CouncilTests(unittest.TestCase):
    def test_requires_real_independent_completed_specialists(self):
        report, agents = council.verify_events(transcript(), ["finance", "product"])
        self.assertIn("cash buffer", report)
        self.assertEqual(len(set(agents.values())), 2)

    def test_refuses_self_report_and_partial_failure(self):
        fabricated = [item(type="agent_message", text="I consulted everyone."), {"type": "turn.completed"}]
        with self.assertRaises(ValueError):
            council.verify_events(fabricated, ["finance"])
        failed = transcript()
        failed[2]["item"]["agents_states"]["product-thread"]["status"] = "errored"
        with self.assertRaises(ValueError):
            council.verify_events(failed, ["finance", "product"])

    def test_refuses_reusing_one_agent_for_two_roles(self):
        events = transcript()
        events[1]["item"]["receiver_thread_ids"] = ["finance-thread"]
        with self.assertRaises(ValueError):
            council.verify_events(events, ["finance", "product"])

    def test_requires_report_after_specialists_finish(self):
        events = transcript()
        events[2], events[3] = events[3], events[2]
        with self.assertRaises(ValueError):
            council.verify_events(events, ["finance", "product"])

    def test_restarted_or_failed_specialist_is_not_complete(self):
        for state in ("running", "errored", "interrupted"):
            events = transcript()
            events.insert(3, item(type="collab_tool_call", tool="wait", agents_states={
                "product-thread": {"status": state, "message": "Later state"}}))
            with self.assertRaises(ValueError):
                council.verify_events(events, ["finance", "product"])

    def test_rejects_action_tools(self):
        events = transcript()
        events.insert(0, item(type="command_execution", command="unexpected"))
        with self.assertRaises(ValueError):
            council.verify_events(events, ["finance", "product"])

    def test_name_conflict_never_stops_another_container(self):
        with patch.object(council.subprocess, "run") as execute:
            execute.return_value.returncode = 125
            council.container(["login", "status"])
            self.assertEqual(execute.call_count, 1)

    def test_timeout_cleans_only_the_owned_container(self):
        owned = "a" * 64
        def execute(command, **kwargs):
            if command[1] == "run":
                Path(command[command.index("--cidfile") + 1]).write_text(owned)
                raise council.subprocess.TimeoutExpired(command, 1200)
            return SimpleNamespace(returncode=0)
        with patch.object(council.subprocess, "run", side_effect=execute) as run:
            with self.assertRaises(council.subprocess.TimeoutExpired):
                council.container(["exec", "-"])
            self.assertEqual(run.call_args.args[0], ["docker", "rm", "--force", owned])

    def test_cleanup_failure_is_reported_with_owned_id(self):
        owned = "b" * 64
        def execute(command, **kwargs):
            if command[1] == "run":
                Path(command[command.index("--cidfile") + 1]).write_text(owned)
                return SimpleNamespace(returncode=0)
            return SimpleNamespace(returncode=1, stderr="Docker daemon unavailable")
        with patch.object(council.subprocess, "run", side_effect=execute):
            with self.assertRaisesRegex(RuntimeError, owned):
                council.container(["exec", "-"])


if __name__ == "__main__":
    unittest.main()
