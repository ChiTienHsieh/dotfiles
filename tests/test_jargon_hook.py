#!/usr/bin/env python3
"""Tests for the jargon pre-commit hook section."""

from __future__ import annotations

import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = REPO_ROOT / "hooks" / "pre-commit"
ALLOWLIST_PATH = REPO_ROOT / "hooks" / "jargon-allowlist.yml"


def run_hook_with_diff(
    staged_content: str,
    filename: str = "test.md",
    allowlist: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Set up a temp git repo, stage a file, and run the hook."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir) / "repo"
        repo.mkdir()

        # Init repo
        env = {**os.environ, "HOME": tmpdir, "GIT_CONFIG_NOSYSTEM": "1"}
        run = lambda cmd, **kw: subprocess.run(
            cmd, cwd=repo, capture_output=True, text=True, env=env, **kw
        )
        run(["git", "init", "-b", "main"])
        run(["git", "config", "user.email", "test@test.invalid"])
        run(["git", "config", "user.name", "Test"])

        # Initial commit so we have something to diff against
        (repo / "README.md").write_text("init\n")
        run(["git", "add", "README.md"])
        run(["git", "commit", "-m", "init"])

        # Set up hooks dir with allowlist
        hooks_dir = repo / "hooks"
        hooks_dir.mkdir()
        if allowlist is None:
            allowlist = ALLOWLIST_PATH.read_text(encoding="utf-8")
        (hooks_dir / "jargon-allowlist.yml").write_text(allowlist, encoding="utf-8")

        # Copy hook
        hook_content = HOOK_PATH.read_text(encoding="utf-8")
        hook_file = repo / ".git" / "hooks" / "pre-commit"
        hook_file.write_text(hook_content)
        hook_file.chmod(0o755)

        # Stage the test file
        (repo / filename).write_text(staged_content)
        run(["git", "add", filename])

        # Run commit (which triggers the hook)
        result = run(
            ["git", "commit", "-m", "test commit"],
            timeout=10,
        )
        return result


class JargonRejectTests(unittest.TestCase):
    def test_reject_list_word_in_comment_blocks_commit(self) -> None:
        content = "# Check idempotent behavior here\n"
        result = run_hook_with_diff(content)
        self.assertNotEqual(result.returncode, 0)
        output = result.stdout + result.stderr
        self.assertIn("idempotent", output)
        self.assertIn("重跑安全", output)

    def test_reject_list_word_case_insensitive(self) -> None:
        content = "# Observability is important\n"
        result = run_hook_with_diff(content)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("observability", result.stdout.lower() + result.stderr.lower())


class JargonAllowTests(unittest.TestCase):
    def test_allow_list_word_passes_silently(self) -> None:
        content = "# This uses the API and CLI\n"
        result = run_hook_with_diff(content)
        self.assertEqual(result.returncode, 0)

    def test_allow_list_mixed_case_passes(self) -> None:
        content = "# Check the SSOT and QoL settings\n"
        result = run_hook_with_diff(content)
        self.assertEqual(result.returncode, 0)


class JargonWarningTests(unittest.TestCase):
    def test_unknown_abbreviation_warns_but_does_not_block(self) -> None:
        content = "# Make sure the XYZZY flag is set\n"
        result = run_hook_with_diff(content)
        self.assertEqual(result.returncode, 0)
        output = result.stdout + result.stderr
        self.assertIn("XYZZY", output)
        self.assertIn("not in allowlist", output)


class JargonIgnoreTests(unittest.TestCase):
    def test_non_comment_lines_are_ignored(self) -> None:
        content = "orchestration = true\n"
        result = run_hook_with_diff(content)
        self.assertEqual(result.returncode, 0)

    def test_code_only_lines_not_flagged(self) -> None:
        content = "config_value = 'some_forbidden_word'\nother = 42\n"
        result = run_hook_with_diff(content, filename="config.py")
        self.assertEqual(result.returncode, 0)

    def test_hex_values_not_flagged(self) -> None:
        content = "# Color code: #FF00AA\n"
        result = run_hook_with_diff(content)
        self.assertEqual(result.returncode, 0)
        output = result.stdout + result.stderr
        # FF00AA should not appear as unknown abbreviation
        self.assertNotIn("FF00AA", output)


class JargonAllowlistParsingTests(unittest.TestCase):
    def test_custom_allowlist(self) -> None:
        allowlist = textwrap.dedent("""\
            allow:
              - FOO
              - BAR

            reject:
              - baz|巴茲 (baz)
        """)
        content = "# Check FOO and BAR\n"
        result = run_hook_with_diff(content, allowlist=allowlist)
        self.assertEqual(result.returncode, 0)

    def test_custom_reject(self) -> None:
        allowlist = textwrap.dedent("""\
            allow:
              - FOO

            reject:
              - baz|巴茲 (baz)
        """)
        content = "# Use baz for this\n"
        result = run_hook_with_diff(content, allowlist=allowlist)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("巴茲", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
