from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLAUDE_DIR = REPO_ROOT / "claude"
GUARD = CLAUDE_DIR / "hooks" / "hook-bypass-guard.py"

DENY = [
    "git commit --no-verify -m wip",
    "git commit -m wip --no-verify",
    'git commit -m "fix: tidy" --no-verify',
    "git commit -n -m wip",
    "git commit -nm wip",
    "git commit -anm wip",
    "git commit -C HEAD -n",
    "git am -n < fix.patch",
    "git push --no-verify origin main",
    "git merge --no-verify feature",
    "git -C repo commit -n",
    "/usr/bin/git commit --no-verify",
    "cd repo && git commit --no-verify -m wip",
    "git status\ngit commit --no-verify -m wip",
    "git commit -m wip \\\n  --no-verify",
    "git -c core.hooksPath=/dev/null commit -m wip",
    'git -c "core.hooksPath=/dev/null" commit -m wip',
    "git -c core.hookspath= push",
    "git --config-env=core.hooksPath=EMPTY commit -m wip",
]

ALLOW = [
    'git commit -m "fix: stop suggesting --no-verify"',
    "git commit -m 'never use git commit -n'",
    "git commit -m \"$(cat <<'EOF'\nfix: drop --no-verify and -n hints\nit's \"quoted\" text\nEOF\n)\"",
    "git commit -F - <<'EOF'\ngit commit --no-verify is banned\nEOF",
    "git commit -m wip # don't add --no-verify\necho -n done",
    "git commit -m wip 2>&1 | tail -n 3",
    "git push -n origin main",
    "git commit -mn",
    "git commit -m -n",
    "git commit -am wip",
    "git commit -- -n",
    "git rebase -n main",
    "git cherry-pick -n abc123",
    "git log --grep=--no-verify",
    "git grep -n -e --no-verify",
    "grep -n -- --no-verify hooks/pre-commit",
    "git config --get core.hooksPath",
    "git -c user.name=x commit -m wip",
    "echo 'git commit --no-verify'",
    'gh pr create --body "drop the --no-verify hint"',
]


def run_guard(stdin: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GUARD)],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def decision(command: str) -> str:
    result = run_guard(json.dumps({"tool_input": {"command": command}}))
    if result.returncode != 0:
        raise AssertionError(f"guard exited {result.returncode}: {result.stderr}")
    if not result.stdout.strip():
        return "allow"
    return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"]


class HookBypassGuardTests(unittest.TestCase):
    def test_denies_hook_bypass(self) -> None:
        for command in DENY:
            with self.subTest(command=command):
                self.assertEqual(decision(command), "deny")

    def test_allows_mentions_and_unrelated_flags(self) -> None:
        for command in ALLOW:
            with self.subTest(command=command):
                self.assertEqual(decision(command), "allow")

    def test_fails_open_on_unparsable_input(self) -> None:
        for stdin in ("not json", json.dumps({"tool_input": {"command": "git commit -m 'oops"}})):
            with self.subTest(stdin=stdin):
                result = run_guard(stdin)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")


class ClaudeSettingsHookTests(unittest.TestCase):
    def test_bash_pre_tool_use_runs_guard_from_repo_hooks(self) -> None:
        settings = json.loads((CLAUDE_DIR / "settings.json").read_text(encoding="utf-8"))
        commands = [
            hook["command"]
            for entry in settings["hooks"]["PreToolUse"]
            if entry.get("matcher") == "Bash"
            for hook in entry["hooks"]
        ]
        self.assertIn("python3 ~/.claude/hooks/hook-bypass-guard.py", commands)
        for command in commands:
            if "~/.claude/hooks/" not in command:
                continue
            script = command.split("~/.claude/hooks/", 1)[1].split()[0]
            with self.subTest(script=script):
                self.assertTrue((CLAUDE_DIR / "hooks" / script).is_file())


if __name__ == "__main__":
    unittest.main()
