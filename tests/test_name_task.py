#!/usr/bin/env python3
"""Regression tests for name-task title application (A11)."""

from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
NAME_TASK_DIR = REPO_ROOT / "skills" / "shared" / "name-task"
SKILL = NAME_TASK_DIR / "SKILL.md"
RENAME_SCRIPT = NAME_TASK_DIR / "scripts" / "rename-session.sh"
RUNTIMES = NAME_TASK_DIR / "runtimes"


class NameTaskContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.script = RENAME_SCRIPT.read_text(encoding="utf-8")
        cls.runtimes = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(RUNTIMES.glob("*.md"))
        }

    def test_skill_does_not_mint_tmux_authorization(self) -> None:
        self.assertIn("不是 tmux mutation 授權", self.skill)
        self.assertIn("**不會**對 pane `send-keys`", self.skill)
        self.assertIn("不得把 task 內容或其他 prompt 文字嵌入自己的 pane", self.skill)
        self.assertNotIn("script 會自動處理", self.skill)

    def test_runtimes_do_not_equate_own_pane_rename_with_human_auth(self) -> None:
        for name, text in self.runtimes.items():
            with self.subTest(runtime=name):
                self.assertNotIn("視同使用者明確要求", text)
                if name == "codex-app.md":
                    self.assertIn("set_thread_title", text)
                    continue
                self.assertIn("不會對 pane `send-keys`", text)
                self.assertIn("明確要求", text)

    def test_rename_script_never_sends_keys(self) -> None:
        self.assertNotRegex(self.script, r"(?m)^\s*tmux\s+send-keys\b")
        self.assertNotRegex(self.script, r"(?m)^\s*command\s+tmux\s+send-keys\b")
        self.assertIn("Suggested title", self.script)
        self.assertIn("/rename", self.script)
        self.assertIn("does not send-keys", self.script)

    def test_rename_script_prints_suggestion_without_invoking_tmux(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            fake_bin = temp / "bin"
            fake_bin.mkdir()
            fake_tmux = fake_bin / "tmux"
            log_path = temp / "tmux-calls.log"
            fake_tmux.write_text(
                "#!/bin/bash\n"
                f"printf '%s\\n' \"$*\" >> '{log_path}'\n"
                "exit 0\n",
                encoding="utf-8",
            )
            fake_tmux.chmod(fake_tmux.stat().st_mode | stat.S_IXUSR)

            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
            env["TMUX_PANE"] = "%name-task-fixture"
            env["HOME"] = str(temp / "home")
            env["TMPDIR"] = str(temp / "tmp")
            (temp / "home").mkdir()
            (temp / "tmp").mkdir()

            result = subprocess.run(
                ["bash", str(RENAME_SCRIPT), "🔧 fixture | rename safety | suggested"],
                check=False,
                capture_output=True,
                text=True,
                env=env,
                cwd=str(temp),
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "/rename 🔧 fixture | rename safety | suggested", result.stdout
            )
            self.assertFalse(log_path.exists())
            self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
