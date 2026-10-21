"""Run the actual global dispatcher and Markdown checker in temporary repos."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "git/.config/git/hooks/pre-commit"
CHECKER = HOOK.parent / "lib/check-md-zh-tw-ratio.mjs"


class GlobalGitHookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.env = dict(os.environ, HOME=self.temp.name, GIT_CONFIG_NOSYSTEM="1",
                        GIT_CONFIG_GLOBAL=os.devnull)
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("commit", "--allow-empty", "-qm", "seed")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env,
                              capture_output=True, text=True, check=True)

    def test_common_hook_runs_in_main_and_linked_worktree(self):
        linked = Path(self.temp.name) / "linked"
        self.git("worktree", "add", "--detach", str(linked))
        local_hook = self.repo / ".git/hooks/pre-commit"
        local_hook.write_text("#!/bin/sh\necho repository-hook\nexit 9\n")
        local_hook.chmod(0o755)
        for cwd in (self.repo, linked):
            result = subprocess.run(["sh", str(HOOK)], cwd=cwd, env=self.env,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 9, result.stdout + result.stderr)
            self.assertIn("repository-hook", result.stdout)

    def test_markdown_names_are_not_quoted_trimmed_or_split(self):
        for name in ("說明.md", " leading space.md", "two\nlines.md"):
            with self.subTest(name=name):
                path = self.repo / name
                path.write_text("Unsupported terminology repeated throughout this otherwise entirely English document. " * 4)
                self.git("add", "--", name)
                result = subprocess.run(["node", str(CHECKER)], cwd=self.repo, env=self.env,
                                        capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0, "Markdown filename escaped the checker")
                self.git("restore", "--staged", "--", name)
                path.unlink()


if __name__ == "__main__":
    unittest.main()
