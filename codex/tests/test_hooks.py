from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


CODEX_DIR = Path(__file__).resolve().parents[1]
HOOKS_DIR = CODEX_DIR / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import request_thread_title  # noqa: E402
import set_thread_title  # noqa: E402
import stop_dirty_worktree  # noqa: E402
import stop_dispatcher  # noqa: E402


class ThreadTitleValidationTests(unittest.TestCase):
    def test_accepts_all_supported_states(self) -> None:
        for emoji in ("⏸️", "⏳", "🔎", "📦"):
            title = f"{emoji} dotfiles｜自動改 thread 名｜測試完成"
            self.assertEqual(set_thread_title.validate_title(title), title)

    def test_rejects_wrong_shape_or_emoji(self) -> None:
        invalid = (
            "✅ dotfiles｜自動改名｜完成",
            "📦 dotfiles｜只有兩欄",
            "📦 dotfiles｜太｜多｜欄",
            "📦 dotfiles | 自動改名 | 完成",
        )
        for title in invalid:
            with self.subTest(title=title), self.assertRaises(ValueError):
                set_thread_title.validate_title(title)

    def test_enforces_hard_cap(self) -> None:
        title = "📦 dotfiles｜自動改名｜" + ("完" * 40)
        with self.assertRaisesRegex(ValueError, "hard cap"):
            set_thread_title.validate_title(title)

    def test_protocol_uses_name_set_only(self) -> None:
        messages = set_thread_title.protocol_request_messages(
            "019fcfbd-8a09-7c31-ba17-8ac72a59d44d",
            "📦 dotfiles｜自動改 thread 名｜測試完成",
        )
        self.assertEqual(
            [message["method"] for message in messages],
            ["initialize", "initialized", "thread/name/set"],
        )
        self.assertNotIn("thread/archive", json.dumps(messages))

    def test_rejects_unsafe_or_blank_display_fields(self) -> None:
        invalid = (
            "📦 repo｜目的\t注入｜完成",
            "📦 repo｜目的\u2028注入｜完成",
            "📦 repo｜\u2066目的｜完成",
            "📦   ｜目的｜完成",
            "📦 repo｜   ｜完成",
        )
        for title in invalid:
            with self.subTest(title=title), self.assertRaises(ValueError):
                set_thread_title.validate_title(title)

    @mock.patch.object(set_thread_title.shutil, "which", return_value="/usr/bin/codex")
    @mock.patch.object(set_thread_title, "wait_for_response")
    @mock.patch.object(set_thread_title.subprocess, "Popen")
    def test_app_server_success(
        self, popen: mock.Mock, wait: mock.Mock, _which: mock.Mock
    ) -> None:
        process = popen.return_value
        process.stdin = mock.Mock()
        process.stdout = mock.Mock()
        process.stderr = None
        process.poll.return_value = None
        wait.side_effect = [{"id": 0, "result": {}}, {"id": 1, "result": {}}]
        set_thread_title.set_thread_title(
            "019fcfbd-8a09-7c31-ba17-8ac72a59d44d",
            "📦 dotfiles｜自動改 thread 名｜測試完成",
        )
        command = popen.call_args.args[0]
        self.assertEqual(command, ["/usr/bin/codex", "app-server", "--stdio"])
        self.assertEqual(wait.call_args_list[0].args[1], 0)
        self.assertEqual(wait.call_args_list[1].args[1], 1)

    @mock.patch.object(set_thread_title.shutil, "which", return_value="/usr/bin/codex")
    @mock.patch.object(set_thread_title, "wait_for_response")
    @mock.patch.object(set_thread_title.subprocess, "Popen")
    def test_app_server_error_is_nonzero(
        self, popen: mock.Mock, wait: mock.Mock, _which: mock.Mock
    ) -> None:
        process = popen.return_value
        process.stdin = mock.Mock()
        process.stdout = mock.Mock()
        process.stderr = None
        process.poll.return_value = None
        wait.side_effect = [
            {"id": 0, "result": {}},
            {"id": 1, "error": {"code": -1, "message": "not found"}},
        ]
        with self.assertRaisesRegex(RuntimeError, "not found"):
            set_thread_title.set_thread_title(
                "019fcfbd-8a09-7c31-ba17-8ac72a59d44d",
                "📦 dotfiles｜自動改 thread 名｜測試完成",
            )


class ThreadTitleRequestTests(unittest.TestCase):
    def test_private_request_round_trip_is_one_shot(self) -> None:
        thread_id = "019fcfbd-8a09-7c31-ba17-8ac72a59d44d"
        title = "📦 dotfiles｜自動改 thread 名｜測試完成"
        with tempfile.TemporaryDirectory() as temporary_directory, mock.patch.object(
            request_thread_title,
            "REQUEST_ROOT",
            Path(temporary_directory) / "requests",
        ):
            request_path = request_thread_title.prepare_title_request(thread_id)
            request_path.write_text(title + "\n", encoding="utf-8")
            self.assertEqual(
                request_thread_title.take_title_request(thread_id),
                (thread_id, title),
            )
            self.assertIsNone(request_thread_title.take_title_request(thread_id))

    def test_unedited_request_is_a_quiet_skip(self) -> None:
        thread_id = "019fcfbd-8a09-7c31-ba17-8ac72a59d44d"
        with tempfile.TemporaryDirectory() as temporary_directory, mock.patch.object(
            request_thread_title,
            "REQUEST_ROOT",
            Path(temporary_directory) / "requests",
        ):
            request_thread_title.prepare_title_request(thread_id)
            self.assertIsNone(request_thread_title.take_title_request(thread_id))

    def test_shell_metacharacters_are_only_data(self) -> None:
        thread_id = "019fcfbd-8a09-7c31-ba17-8ac72a59d44d"
        title = "📦 repo｜處理 user's input｜$(id);完成"
        with tempfile.TemporaryDirectory() as temporary_directory, mock.patch.object(
            request_thread_title,
            "REQUEST_ROOT",
            Path(temporary_directory) / "requests",
        ):
            request_path = request_thread_title.prepare_title_request(thread_id)
            request_path.write_text(title + "\n", encoding="utf-8")
            self.assertEqual(
                request_thread_title.take_title_request(thread_id),
                (thread_id, title),
            )


class StopDispatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = {
            "hook_event_name": "Stop",
            "session_id": "019fcfbd-8a09-7c31-ba17-8ac72a59d44d",
            "cwd": "/tmp",
            "stop_hook_active": False,
            "last_assistant_message": "done",
        }

    def test_first_stop_requests_exactly_one_checkpoint(self) -> None:
        with mock.patch.object(
            stop_dispatcher, "build_dirty_worktree_followup", return_value=None
        ), mock.patch.object(
            stop_dispatcher,
            "prepare_title_request",
            return_value=Path("/tmp/title-request.txt"),
        ) as prepare:
            result = stop_dispatcher.build_stop_result(self.payload)
        self.assertEqual(result["decision"], "block")
        reason = str(result["reason"])
        self.assertIn("Thread 標題檢查", reason)
        self.assertIn("apply_patch", reason)
        self.assertIn("/tmp/title-request.txt", reason)
        self.assertNotIn("--title", reason)
        self.assertIn("24–32", reason)
        self.assertIn("只能改標題", reason)
        self.assertNotIn("thread/name/set", reason)
        self.assertLess(len(stop_dispatcher.TITLE_CHECKPOINT), 750)
        self.assertNotIn("stop_hook_active", reason)
        prepare.assert_called_once_with(self.payload["session_id"])

    def test_second_stop_is_unconditionally_allowed(self) -> None:
        payload = {**self.payload, "stop_hook_active": True}
        with mock.patch.object(
            stop_dispatcher, "build_dirty_worktree_followup"
        ) as dirty, mock.patch.object(
            stop_dispatcher, "take_title_request", return_value=None
        ) as take:
            result = stop_dispatcher.build_stop_result(payload)
        self.assertEqual(result, {"continue": True})
        dirty.assert_not_called()
        take.assert_called_once_with(payload["session_id"])

    def test_second_stop_applies_one_queued_title(self) -> None:
        payload = {**self.payload, "stop_hook_active": True}
        request = (payload["session_id"], "📦 dotfiles｜自動改 thread 名｜測試完成")
        with mock.patch.object(
            stop_dispatcher, "take_title_request", return_value=request
        ), mock.patch.object(stop_dispatcher, "set_thread_title") as set_title:
            result = stop_dispatcher.build_stop_result(payload)
        self.assertEqual(result, {"continue": True})
        set_title.assert_called_once_with(*request)

    def test_second_stop_failure_warns_without_continuing_again(self) -> None:
        payload = {**self.payload, "stop_hook_active": True}
        with mock.patch.object(
            stop_dispatcher, "take_title_request", side_effect=RuntimeError("boom")
        ):
            result = stop_dispatcher.build_stop_result(payload)
        self.assertEqual(result["continue"], True)
        self.assertNotIn("decision", result)
        self.assertIn("已略過", str(result["systemMessage"]))

    def test_dirty_policy_is_composed_into_same_reason(self) -> None:
        with mock.patch.object(
            stop_dispatcher,
            "build_dirty_worktree_followup",
            return_value="工作區整理：提供整理選項。",
        ):
            result = stop_dispatcher.build_stop_result(self.payload)
        reason = str(result["reason"])
        self.assertEqual(reason.count("Thread 標題檢查"), 1)
        self.assertEqual(reason.count("工作區整理"), 2)
        self.assertIn("提供整理選項。", reason)

    def test_post_tool_use_tracks_without_continuation(self) -> None:
        payload = {**self.payload, "hook_event_name": "PostToolUse"}
        with mock.patch.object(stop_dispatcher, "track_touched_worktrees") as track:
            result = stop_dispatcher.handle_payload(payload)
        self.assertEqual(result, {"continue": True})
        track.assert_called_once_with(payload)


class DirtyWorktreeCompatibilityTests(unittest.TestCase):
    def test_dirty_prompt_is_lean_zh_tw(self) -> None:
        root = Path("/tmp/repo")
        payload = {"last_assistant_message": "done", "cwd": str(root)}
        with mock.patch.object(
            stop_dirty_worktree, "load_tracked_roots", return_value={root}
        ), mock.patch.object(
            stop_dirty_worktree, "git_root_for_path", return_value=root
        ), mock.patch.object(
            stop_dirty_worktree,
            "dirty_roots_for",
            return_value=[(root, [" M file.txt"])],
        ):
            reason = stop_dirty_worktree.build_dirty_worktree_followup(payload)
        self.assertIsNotNone(reason)
        self.assertIn("工作區整理", reason)
        self.assertIn("目前狀態", reason)
        self.assertIn("除非使用者已授權，不得自行", reason)
        self.assertIn("保留 dirty", reason)
        self.assertNotIn("One or more git worktrees", reason)

    def test_level_up_checkpoint_skips_dirty_prompt(self) -> None:
        message = "Level 4\n**問題:** pick one\nA) a\nB) b\nC) c\nD) d"
        payload = {"last_assistant_message": message, "cwd": "/tmp"}
        self.assertIsNone(stop_dirty_worktree.build_dirty_worktree_followup(payload))


class HookConfigurationTests(unittest.TestCase):
    def test_global_config_uses_one_dispatcher(self) -> None:
        config = json.loads((CODEX_DIR / "hooks.json").read_text(encoding="utf-8"))
        hooks = config["hooks"]
        self.assertEqual(set(hooks), {"PostToolUse", "Stop"})
        commands = [
            handler["command"]
            for event in hooks.values()
            for group in event
            for handler in group["hooks"]
        ]
        self.assertEqual(len(commands), 2)
        self.assertTrue(all("stop_dispatcher.py" in command for command in commands))


if __name__ == "__main__":
    unittest.main()
