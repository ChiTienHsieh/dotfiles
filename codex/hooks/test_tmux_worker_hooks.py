#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path


HOOKS_DIR = Path(__file__).resolve().parent
TRACKER_PATH = HOOKS_DIR.parent / "bin" / "track_tmux_workers.py"
INSTALLER_PATH = HOOKS_DIR / "install_hooks.py"
MANIFEST_PATH = HOOKS_DIR.parent / "hooks.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tracker = load_module("track_tmux_workers", TRACKER_PATH)
installer = load_module("install_hooks", INSTALLER_PATH)


class TmuxWorkerTrackerTests(unittest.TestCase):
    SESSION_OPEN = (
        "tmux new-session -d -P "
        "-F 'CODEX_TMUX_WORKER_OPEN=session:#{session_name}' "
        "-s review-one -c /tmp 'claude --model opus'"
    )
    SESSION_CLOSE = (
        "tmux has-session -t review-one 2>/dev/null || "
        "printf '%s\\n' 'CODEX_TMUX_WORKER_CLOSED=session:review-one'"
    )
    PANE_OPEN = (
        "tmux split-window -h -P "
        "-F 'CODEX_TMUX_WORKER_OPEN=pane:#{pane_id}' "
        "-t controller -c /tmp 'codex --sandbox read-only'"
    )
    PANE_CLOSE = (
        "tmux display-message -p -t %42 '#{pane_id}' >/dev/null 2>&1 || "
        "printf '%s\\n' 'CODEX_TMUX_WORKER_CLOSED=pane:%42'"
    )

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.original_track_dir = tracker.TRACK_DIR
        tracker.TRACK_DIR = Path(self.tempdir.name)
        self.addCleanup(setattr, tracker, "TRACK_DIR", self.original_track_dir)
        self.session_id = "codex-session-1"

    def post(self, command: str, response: str) -> dict[str, object]:
        payload = {
            "hook_event_name": "PostToolUse",
            "session_id": self.session_id,
            "tool_input": {"command": command},
            "tool_response": response,
        }
        output = StringIO()
        with redirect_stdout(output):
            tracker.record_lifecycle(payload)
        return json.loads(output.getvalue())

    def stop(self, message: str, **extra: object) -> dict[str, object]:
        payload = {
            "hook_event_name": "Stop",
            "session_id": self.session_id,
            "last_assistant_message": message,
            **extra,
        }
        output = StringIO()
        with redirect_stdout(output):
            tracker.stop_guard(payload)
        return json.loads(output.getvalue())

    def test_tracks_and_closes_exact_session_marker(self) -> None:
        self.post(
            self.SESSION_OPEN,
            "CODEX_TMUX_WORKER_OPEN=session:review-one\n",
        )
        self.assertEqual(
            tracker.load_workers(self.session_id), {("session", "review-one")}
        )

        self.post(
            self.SESSION_CLOSE,
            "CODEX_TMUX_WORKER_CLOSED=session:review-one\n",
        )
        self.assertEqual(tracker.load_workers(self.session_id), set())
        self.assertFalse(tracker.session_track_path(self.session_id).exists())

    def test_tracks_labeled_split_pane(self) -> None:
        self.post(
            self.PANE_OPEN,
            "CODEX_TMUX_WORKER_OPEN=pane:%42\n",
        )
        self.assertEqual(tracker.load_workers(self.session_id), {("pane", "%42")})

        self.post(
            self.PANE_CLOSE,
            "CODEX_TMUX_WORKER_CLOSED=pane:%42\n",
        )
        self.assertEqual(tracker.load_workers(self.session_id), set())

    def test_ignores_marker_without_matching_tmux_action(self) -> None:
        self.post(
            "sed -n '1,20p' SKILL.md",
            "CODEX_TMUX_WORKER_OPEN=session:not-a-worker\n",
        )
        self.assertEqual(tracker.load_workers(self.session_id), set())

    def test_ignores_closed_marker_for_a_different_target(self) -> None:
        tracker.save_workers(
            self.session_id,
            {("session", "review-one"), ("session", "review-two")},
        )
        self.post(
            "tmux has-session -t review-one 2>/dev/null || "
            "printf '%s\\n' 'CODEX_TMUX_WORKER_CLOSED=session:review-two'",
            "CODEX_TMUX_WORKER_CLOSED=session:review-two\n",
        )
        self.assertEqual(
            tracker.load_workers(self.session_id),
            {("session", "review-one"), ("session", "review-two")},
        )

    def test_ignores_open_marker_for_a_different_session(self) -> None:
        self.post(
            self.SESSION_OPEN,
            "CODEX_TMUX_WORKER_OPEN=session:unrelated\n",
        )
        self.assertEqual(tracker.load_workers(self.session_id), set())

    def test_rejects_forged_open_marker_from_chained_command(self) -> None:
        self.post(
            self.SESSION_OPEN
            + " && printf '%s\\n' 'CODEX_TMUX_WORKER_OPEN=session:review-one'",
            "CODEX_TMUX_WORKER_OPEN=session:review-one\n",
        )
        self.assertEqual(tracker.load_workers(self.session_id), set())

    def test_rejects_custom_tmux_socket(self) -> None:
        command = self.SESSION_OPEN.replace("tmux ", "tmux -L codex ", 1)
        self.post(command, "CODEX_TMUX_WORKER_OPEN=session:review-one\n")
        self.assertEqual(tracker.load_workers(self.session_id), set())

    def test_capture_output_cannot_claim_worker_was_closed(self) -> None:
        tracker.save_workers(self.session_id, {("session", "review-one")})
        self.post(
            "tmux capture-pane -pt review-one -S -80",
            "CODEX_TMUX_WORKER_CLOSED=session:review-one\n",
        )
        self.assertEqual(
            tracker.load_workers(self.session_id), {("session", "review-one")}
        )

    def test_stop_blocks_unresolved_worker(self) -> None:
        tracker.save_workers(self.session_id, {("session", "review-one")})
        decision = self.stop("Done.")
        self.assertEqual(decision["decision"], "block")
        self.assertIn("review-one", decision["reason"])

    def test_stop_allows_explicit_retention_with_target(self) -> None:
        tracker.save_workers(self.session_id, {("session", "review-one")})
        self.assertEqual(
            self.stop("保留中的 tmux worker：review-one（仍在跑測試）"),
            {"continue": True},
        )

    def test_stop_allows_english_retention_with_every_target(self) -> None:
        tracker.save_workers(
            self.session_id,
            {("session", "review-one"), ("pane", "%42")},
        )
        message = (
            "Retained tmux worker: review-one (still reviewing)\n"
            "Retained tmux worker: %42 (waiting for CI)"
        )
        self.assertEqual(self.stop(message), {"continue": True})

    def test_stop_requires_retention_for_every_target(self) -> None:
        tracker.save_workers(
            self.session_id,
            {("session", "review-one"), ("pane", "%42")},
        )
        decision = self.stop("保留中的 tmux worker：review-one（仍在跑測試）")
        self.assertEqual(decision["decision"], "block")
        self.assertIn("%42", decision["reason"])

    def test_stop_does_not_accept_retention_without_reason(self) -> None:
        tracker.save_workers(self.session_id, {("session", "review-one")})
        self.assertEqual(
            self.stop("保留中的 tmux worker：review-one")["decision"], "block"
        )

    def test_recursive_stop_hook_does_not_block_again(self) -> None:
        tracker.save_workers(self.session_id, {("session", "review-one")})
        self.assertEqual(
            self.stop("Done.", stop_hook_active=True),
            {"continue": True},
        )

    def test_corrupt_ledger_blocks_stop(self) -> None:
        path = tracker.session_track_path(self.session_id)
        assert path is not None
        path.write_text("not json\n", encoding="utf-8")
        decision = self.stop("Done.")
        self.assertEqual(decision["decision"], "block")
        self.assertIn("unreadable", decision["reason"])

    def test_tracking_error_is_reported_for_corrupt_ledger(self) -> None:
        path = tracker.session_track_path(self.session_id)
        assert path is not None
        path.write_text("not json\n", encoding="utf-8")
        result = self.post(
            self.SESSION_OPEN,
            "CODEX_TMUX_WORKER_OPEN=session:review-one\n",
        )
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("tracking failed", context)

    def test_ledgers_are_isolated_and_session_ids_are_hashed(self) -> None:
        tracker.save_workers(self.session_id, {("session", "review-one")})
        other_session = "../codex-session-1"
        tracker.save_workers(other_session, {("pane", "%42")})
        self.assertEqual(
            tracker.load_workers(self.session_id), {("session", "review-one")}
        )
        self.assertEqual(tracker.load_workers(other_session), {("pane", "%42")})
        first_path = tracker.session_track_path(self.session_id)
        second_path = tracker.session_track_path(other_session)
        assert first_path is not None and second_path is not None
        self.assertNotEqual(first_path, second_path)
        self.assertNotIn("codex-session-1", first_path.name)


class HookInstallerTests(unittest.TestCase):
    def test_merge_preserves_unmanaged_hooks_and_is_idempotent(self) -> None:
        manifest = installer.load_json(MANIFEST_PATH)
        live = {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "third-party-hook",
                                "timeout": 5,
                            },
                            {
                                "type": "command",
                                "command": installer.MANAGED_COMMAND,
                                "timeout": 1,
                            },
                        ]
                    }
                ]
            }
        }
        once = installer.merge_hooks(live, manifest)
        twice = installer.merge_hooks(once, manifest)
        self.assertEqual(once, twice)
        text = json.dumps(once)
        self.assertIn("third-party-hook", text)
        self.assertEqual(text.count("track_tmux_workers.py"), 2)

    def test_invalid_live_json_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            live_path = Path(tempdir) / "hooks.json"
            live_path.write_text("not json\n", encoding="utf-8")
            with redirect_stderr(StringIO()):
                result = installer.main(
                    ["install_hooks.py", str(MANIFEST_PATH), str(live_path)]
                )
            self.assertEqual(result, 1)
            self.assertEqual(live_path.read_text(encoding="utf-8"), "not json\n")

    def test_structurally_invalid_live_config_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            live_path = Path(tempdir) / "hooks.json"
            original = '{"hooks":{"UserPromptSubmit":"not-a-list"}}\n'
            live_path.write_text(original, encoding="utf-8")
            with redirect_stderr(StringIO()):
                result = installer.main(
                    ["install_hooks.py", str(MANIFEST_PATH), str(live_path)]
                )
            self.assertEqual(result, 1)
            self.assertEqual(live_path.read_text(encoding="utf-8"), original)

    def test_rejects_malformed_hook_handler(self) -> None:
        live = {
            "hooks": {
                "Stop": [
                    {"hooks": [{"type": "command", "command": 42}]},
                ]
            }
        }
        manifest = installer.load_json(MANIFEST_PATH)
        with self.assertRaises(installer.HookConfigError):
            installer.merge_hooks(live, manifest)


if __name__ == "__main__":
    unittest.main()
