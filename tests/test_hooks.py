from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_DIR = REPO_ROOT / "codex"
HOOKS_DIR = CODEX_DIR / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import private_temp_state  # noqa: E402
import stop_dirty_worktree  # noqa: E402


class PrivateTempStateTests(unittest.TestCase):
    def test_rejects_precreated_symlink_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            parent = Path(temporary_directory)
            target = parent / "target"
            target.mkdir()
            root = parent / "state"
            root.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "not owned"):
                private_temp_state.ensure_private_directory(root)

    def test_corrects_same_owner_directory_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "state"
            root.mkdir(mode=0o755)
            private_temp_state.ensure_private_directory(root)
            self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o700)

    def test_atomic_write_replaces_symlink_without_following_it(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "state"
            private_temp_state.ensure_private_directory(root)
            target = Path(temporary_directory) / "target.txt"
            target.write_text("keep\n", encoding="utf-8")
            path = root / "session.json"
            path.symlink_to(target)
            private_temp_state.atomic_write_private(path, "private\n")
            self.assertFalse(path.is_symlink())
            self.assertEqual(path.read_text(encoding="utf-8"), "private\n")
            self.assertEqual(target.read_text(encoding="utf-8"), "keep\n")
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_rejects_wrong_owner_metadata(self) -> None:
        metadata = mock.Mock(st_mode=stat.S_IFREG | 0o600, st_uid=os.getuid() + 1)
        with mock.patch.object(Path, "lstat", return_value=metadata):
            with self.assertRaisesRegex(RuntimeError, "unsafe"):
                private_temp_state.validate_private_file(Path("/tmp/state.json"))


class DirtyWorktreeStateTests(unittest.TestCase):
    def test_private_atomic_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory, mock.patch.object(
            stop_dirty_worktree,
            "TRACK_DIR",
            Path(temporary_directory) / "tracked",
        ):
            roots = {Path("/tmp/repo-a"), Path("/tmp/repo-b")}
            stop_dirty_worktree.save_tracked_roots("session", roots)
            path = stop_dirty_worktree.session_track_path("session")
            self.assertIsNotNone(path)
            assert path is not None
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(stop_dirty_worktree.load_tracked_roots("session"), roots)

    def test_recent_scan_ignores_symlinks_and_public_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory, mock.patch.object(
            stop_dirty_worktree,
            "TRACK_DIR",
            Path(temporary_directory) / "tracked",
        ):
            root = private_temp_state.ensure_private_directory(
                stop_dirty_worktree.TRACK_DIR
            )
            safe = root / "safe.json"
            private_temp_state.atomic_write_private(safe, '{"roots": []}\n')
            public = root / "public.json"
            public.write_text('{"roots": []}\n', encoding="utf-8")
            public.chmod(0o644)
            target = Path(temporary_directory) / "target.json"
            target.write_text('{"roots": []}\n', encoding="utf-8")
            (root / "link.json").symlink_to(target)
            self.assertEqual(stop_dirty_worktree.recent_track_paths(), [safe])


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
    def test_global_config_combines_dirty_worktree_and_tmux_hooks(self) -> None:
        config = json.loads((CODEX_DIR / "hooks.json").read_text(encoding="utf-8"))
        hooks = config["hooks"]
        self.assertEqual(set(hooks), {"PostToolUse", "Stop"})
        commands = [
            handler["command"]
            for event in hooks.values()
            for group in event
            for handler in group["hooks"]
        ]
        self.assertEqual(len(commands), 4)
        self.assertEqual(
            sum("stop_dirty_worktree.py" in command for command in commands), 2
        )
        self.assertEqual(
            sum("track_tmux_workers.py" in command for command in commands), 2
        )
        self.assertTrue(all("thread_title" not in command for command in commands))

    def test_legacy_dispatcher_is_a_dirty_worktree_compatibility_shim(self) -> None:
        dispatcher = (CODEX_DIR / "hooks" / "stop_dispatcher.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("from stop_dirty_worktree import main", dispatcher)
        self.assertNotIn("request_thread_title", dispatcher)
        self.assertNotIn("TITLE_CHECKPOINT", dispatcher)


if __name__ == "__main__":
    unittest.main()
