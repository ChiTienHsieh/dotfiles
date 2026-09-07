#!/usr/bin/env python3
"""Exercise the rename helper's tmux boundary without typing into live tasks."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
NAME_TASK_DIR = REPO_ROOT / "skills/shared/name-task"
RENAME_SCRIPT = NAME_TASK_DIR / "scripts/rename-session.sh"


class RenameSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp = Path(self.temp_dir.name)
        self.log = self.temp / "calls.jsonl"
        fake_tmux = self.temp / "tmux"
        fake_tmux.write_text(
            f"#!{sys.executable}\n"
            "import json, os, sys\n"
            "with open(os.environ['TMUX_TEST_LOG'], 'a') as log:\n"
            "    log.write(json.dumps(sys.argv[1:]) + '\\n')\n"
            "if sys.argv[1] == os.environ.get('TMUX_TEST_FAIL'):\n"
            "    sys.exit(7)\n"
            "if sys.argv[1] == 'display-message':\n"
            "    print(os.environ.get('TMUX_TEST_COMMAND', 'claude'))\n"
        )
        fake_tmux.chmod(0o755)
        self.env = dict(os.environ, PATH=f"{self.temp}{os.pathsep}{os.environ['PATH']}",
                        TMUX_PANE="%42", TMUX_TEST_LOG=str(self.log))
        self.env.pop('TMUX_TEST_FAIL', None)
        self.env.pop('TMUX_TEST_COMMAND', None)

    def run_script(self, title):
        result = subprocess.run(["bash", str(RENAME_SCRIPT), title],
                                env=self.env, capture_output=True, text=True)
        calls = [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []
        return result, calls

    def test_own_pane_rename_is_literal_and_submitted(self):
        title = '🔧 fixture | C-c Enter ; $(touch NEVER) | "標題"'
        result, calls = self.run_script(title)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls, [
            ['display-message', '-t', '%42', '-p', '#{pane_current_command}'],
            ['send-keys', '-t', '%42', '-l', '/rename ' + title,
             ';', 'send-keys', '-t', '%42', 'Enter'],
        ])
        self.assertEqual(result.stdout, '')

    def test_codex_retains_second_enter(self):
        self.env['TMUX_TEST_COMMAND'] = 'codex'
        result, calls = self.run_script('fixture')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[-1], ['send-keys', '-t', '%42', 'Enter'])

    def test_non_tmux_has_manual_fallback(self):
        self.env.pop('TMUX_PANE')
        result, calls = self.run_script('fixture')
        self.assertEqual(result.returncode, 1)
        self.assertIn('/rename fixture', result.stdout)
        self.assertEqual(calls, [])

    def test_invalid_pane_target_is_rejected(self):
        for target in ['other-session', '%42;kill-server', '%42\n']:
            with self.subTest(target=target):
                self.env['TMUX_PANE'] = target
                result, calls = self.run_script('fixture')
                self.assertEqual(result.returncode, 1)
                self.assertEqual(calls, [])

    def test_control_characters_cannot_inject_input(self):
        for title in ['', 'title\n/clear', 'title\r/clear', 'title\x1b', 'title\t']:
            with self.subTest(title=repr(title)):
                result, calls = self.run_script(title)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(calls, [])

    def test_missing_pane_does_not_send_input(self):
        self.env['TMUX_TEST_FAIL'] = 'display-message'
        result, calls = self.run_script('fixture')
        self.assertEqual(result.returncode, 7)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], 'display-message')

    def test_failed_send_does_not_send_extra_enter(self):
        self.env['TMUX_TEST_COMMAND'] = 'codex'
        self.env['TMUX_TEST_FAIL'] = 'send-keys'
        result, calls = self.run_script('fixture')
        self.assertEqual(result.returncode, 7)
        self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
