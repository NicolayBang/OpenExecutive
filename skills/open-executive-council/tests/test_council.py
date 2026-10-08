import importlib.util
import json
import tempfile
from types import SimpleNamespace
from pathlib import Path
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("council", Path(__file__).resolve().parents[1] / "scripts/council.py")
council = importlib.util.module_from_spec(spec)
spec.loader.exec_module(council)


def item(**fields):
    return {"type": "item.completed", "item": fields}


def transcript():
    return [
        {"type": "thread.started", "thread_id": "real-thread"},
        {"type": "turn.started"},
        item(type="agent_message", text="Preserve the cash buffer."),
        {"type": "turn.completed"},
    ]


class CouncilTests(unittest.TestCase):
    def test_requires_recorded_session_and_completed_turn(self):
        report, thread = council.verify_events(transcript())
        self.assertIn("cash buffer", report)
        self.assertEqual(thread, "real-thread")
        for incomplete in (transcript()[1:], transcript()[:-1]):
            with self.assertRaises(ValueError):
                council.verify_events(incomplete)

    def test_refuses_failed_turn_after_an_answer(self):
        events = transcript() + [{"type": "turn.failed"}]
        with self.assertRaises(ValueError):
            council.verify_events(events)

    def test_rejects_output_after_completion_or_a_second_turn(self):
        for event in (item(type="agent_message", text="Unfinished later answer"),
                      {"type": "turn.started"}):
            with self.assertRaises(ValueError):
                council.verify_events(transcript() + [event])

    def test_rejects_action_tools_and_extra_sessions(self):
        for event in (item(type="command_execution", command="unexpected"),
                      {"type": "thread.started", "thread_id": "second-thread"}):
            with self.assertRaises(ValueError):
                council.verify_events(transcript() + [event])

    def test_failed_specialist_prevents_synthesis_and_keeps_partial_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory)
            (task / "brief.md").write_text("A fictional decision.")
            args = SimpleNamespace(task=task, output=task / "out", roles="finance,product", codex=None)
            with patch.object(council, "find_codex", return_value="codex"), \
                    patch.object(council, "run_cli", return_value=SimpleNamespace(returncode=0, stdout="Logged in using ChatGPT", stderr="")), \
                    patch.object(council, "run_turn", side_effect=[("Finance report", "finance-id"), ValueError("Product failed")]) as turn:
                with self.assertRaisesRegex(ValueError, "Product failed"):
                    council.run_council(args)
            metadata = json.loads((args.output / "result.json").read_text())
            self.assertEqual(metadata["status"], "failed")
            self.assertEqual(metadata["agents"], {"finance": "finance-id"})
            self.assertFalse((args.output / "report.md").exists())
            self.assertEqual(turn.call_count, 2)

    def test_local_process_receives_brief_on_stdin_in_neutral_directory(self):
        with patch.object(council.subprocess, "Popen") as start:
            process = start.return_value
            process.communicate.return_value = ("answer", "")
            process.returncode = 0
            result = council.run_cli("codex", ["exec", "-"], input_text="private brief")
            self.assertEqual(result.stdout, "answer")
            self.assertEqual(start.call_args.args[0], ["codex", "exec", "-"])
            self.assertNotEqual(Path(start.call_args.kwargs["cwd"]), Path.cwd())
            self.assertFalse(start.call_args.kwargs.get("shell", False))
            process.communicate.assert_called_once_with("private brief", timeout=1200)

    def test_existing_api_key_variables_do_not_reach_cli(self):
        with patch.dict(council.os.environ, {"CODEX_API_KEY": "test-only", "OPENAI_API_KEY": "test-only"}), \
                patch.object(council.subprocess, "Popen") as start:
            start.return_value.communicate.return_value = ("", "")
            council.run_cli("codex", ["exec", "-"])
            environment = start.call_args.kwargs["env"]
            self.assertNotIn("CODEX_API_KEY", environment)
            self.assertNotIn("OPENAI_API_KEY", environment)

    def test_synthesis_uses_independent_reports_and_requires_its_own_session(self):
        for coordinator in ("executive-id", "finance-id"):
            with self.subTest(coordinator=coordinator), tempfile.TemporaryDirectory() as directory:
                task = Path(directory)
                (task / "brief.md").write_text("A fictional decision.")
                args = SimpleNamespace(task=task, output=task / "out", roles="finance,product", codex=None)
                with patch.object(council, "find_codex", return_value="codex"), \
                        patch.object(council, "run_cli", return_value=SimpleNamespace(returncode=0, stdout="Logged in using ChatGPT", stderr="")), \
                        patch.object(council, "run_turn", side_effect=[("Finance evidence", "finance-id"), ("Product evidence", "product-id"), ("Final recommendation", coordinator)]) as turn:
                    if coordinator == "finance-id":
                        with self.assertRaisesRegex(ValueError, "reused"):
                            council.run_council(args)
                    else:
                        council.run_council(args)
                    self.assertIn("Finance evidence", turn.call_args.args[1])
                    self.assertIn("Product evidence", turn.call_args.args[1])
                complete = coordinator == "executive-id"
                metadata = json.loads((args.output / "result.json").read_text())
                self.assertEqual(metadata["status"], "complete" if complete else "failed")
                self.assertEqual((args.output / "report.md").exists(), complete)

    def test_timeout_stops_only_the_process_tree_started_by_this_run(self):
        with patch.object(council.subprocess, "Popen") as start, \
                patch.object(council.subprocess, "run") as stop, \
                patch.object(council.os, "killpg", create=True) as kill_group:
            process = start.return_value
            process.pid = 12345
            process.poll.return_value = None
            process.communicate.side_effect = council.subprocess.TimeoutExpired("codex", 1200)
            stop.return_value.returncode = 0
            with self.assertRaises(council.subprocess.TimeoutExpired):
                council.run_cli("codex", ["exec", "-"])
            if council.os.name == "nt":
                self.assertEqual(stop.call_args.args[0], ["taskkill", "/PID", "12345", "/T", "/F"])
            else:
                kill_group.assert_called_once_with(12345, council.signal.SIGKILL)

    def test_explicit_cli_path_is_respected(self):
        with patch.object(council.shutil, "which", return_value="/custom/codex") as find:
            self.assertEqual(council.find_codex("/custom/codex"), "/custom/codex")
            find.assert_called_once_with("/custom/codex")


if __name__ == "__main__":
    unittest.main()
