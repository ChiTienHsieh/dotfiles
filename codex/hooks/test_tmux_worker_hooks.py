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
            "tool_input": {
                "source": f'const r = await tools.exec_command({{"cmd":{json.dumps(command)}}});'
            },
            "tool_response": {"content": [{"type": "text", "text": response}]},
        }
        with redirect_stdout(StringIO()):
            tracker.record_lifecycle(payload)
        return payload

    def test_tracks_and_closes_exact_session_marker(self) -> None:
        self.post(
            "tmux new-session -d -s review-one && printf marker",
            "CODEX_TMUX_WORKER_OPEN=session:review-one\n",
        )
        self.assertEqual(
            tracker.load_workers(self.session_id), {("session", "review-one")}
        )

        self.post(
            "tmux kill-session -t review-one && printf marker",
            "CODEX_TMUX_WORKER_CLOSED=session:review-one\n",
        )
        self.assertEqual(tracker.load_workers(self.session_id), set())
        self.assertFalse(tracker.session_track_path(self.session_id).exists())

    def test_tracks_labeled_split_pane(self) -> None:
        self.post(
            "tmux split-window -h -P -F CODEX_TMUX_WORKER_OPEN=pane:#{pane_id}",
            "CODEX_TMUX_WORKER_OPEN=pane:%42\n",
        )
        self.assertEqual(tracker.load_workers(self.session_id), {("pane", "%42")})

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
            "tmux kill-session -t review-one && printf marker",
            "CODEX_TMUX_WORKER_CLOSED=session:review-two\n",
        )
        self.assertEqual(
            tracker.load_workers(self.session_id),
            {("session", "review-one"), ("session", "review-two")},
        )

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
        payload = {
            "session_id": self.session_id,
            "last_assistant_message": "Done.",
        }
        output = StringIO()
        with redirect_stdout(output):
            tracker.stop_guard(payload)
        decision = json.loads(output.getvalue())
        self.assertEqual(decision["decision"], "block")
        self.assertIn("review-one", decision["reason"])

    def test_stop_allows_explicit_retention_with_target(self) -> None:
        tracker.save_workers(self.session_id, {("session", "review-one")})
        payload = {
            "session_id": self.session_id,
            "last_assistant_message": "保留中的 tmux worker：review-one（仍在跑測試）",
        }
        output = StringIO()
        with redirect_stdout(output):
            tracker.stop_guard(payload)
        self.assertEqual(json.loads(output.getvalue()), {"continue": True})

    def test_stop_does_not_accept_retention_without_reason(self) -> None:
        tracker.save_workers(self.session_id, {("session", "review-one")})
        payload = {
            "session_id": self.session_id,
            "last_assistant_message": "保留中的 tmux worker：review-one",
        }
        output = StringIO()
        with redirect_stdout(output):
            tracker.stop_guard(payload)
        self.assertEqual(json.loads(output.getvalue())["decision"], "block")


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
                                "command": "old/track_tmux_workers.py",
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


if __name__ == "__main__":
    unittest.main()
