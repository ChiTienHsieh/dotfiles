"""確認 AI 審查 workflow 的關卡只在該放行時放行，憑證只有 Claude 的審查 job 拿得到。"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "copilot-review.yml"

# 一條該放行的 PR；每個案例只改其中幾項。
PASSING = {
    "AUTHOR_ASSOCIATION": "COLLABORATOR",
    "BASE_REF": "main",
    "CLAUDE_RESULT": "success",
    "CLAUDE_VERDICT": "pass",
    # Copilot 只在過渡用的 pull_request 觸發跑，平常是被跳過的。
    "COPILOT_RESULT": "skipped",
    "COPILOT_VERDICT": "",
    "EVENT_NAME": "pull_request_target",
    "HEAD_REPOSITORY": "owner/repo",
    "REPOSITORY": "owner/repo",
}

COPILOT_PASSED = {"COPILOT_RESULT": "success", "COPILOT_VERDICT": "pass"}

# 過渡用的 pull_request 觸發：拿不到憑證，Claude 被跳過，由 Copilot 代審。
TRANSITIONAL = {
    "EVENT_NAME": "pull_request",
    "CLAUDE_RESULT": "skipped",
    "CLAUDE_VERDICT": "",
    **COPILOT_PASSED,
}

GATE_BLOCKED = [
    ("Claude 判定需要修改", {"CLAUDE_VERDICT": "needs-changes"}),
    ("Claude 沒跑起來", {"CLAUDE_VERDICT": "unavailable"}),
    ("Claude job 被跳過", {"CLAUDE_RESULT": "skipped", "CLAUDE_VERDICT": ""}),
    ("Claude job 被取消", {"CLAUDE_RESULT": "cancelled", "CLAUDE_VERDICT": ""}),
    ("Claude 有判定但 job 失敗", {"CLAUDE_RESULT": "failure"}),
    ("只有 Copilot 通過不算數", {"CLAUDE_RESULT": "skipped", "CLAUDE_VERDICT": "", **COPILOT_PASSED}),
    ("fork 來的 PR", {"HEAD_REPOSITORY": "stranger/repo"}),
    ("base 不是 main", {"BASE_REF": "scratch"}),
    ("作者不是 owner 或 collaborator", {"AUTHOR_ASSOCIATION": "CONTRIBUTOR"}),
    ("過渡用的 pull_request 觸發，Copilot 沒通過", {**TRANSITIONAL, "COPILOT_VERDICT": "needs-changes"}),
    ("過渡用的 pull_request 觸發，Copilot 被跳過", {**TRANSITIONAL, "COPILOT_RESULT": "skipped", "COPILOT_VERDICT": ""}),
]

# （說明, 審查者的輸出, 預期判定）
VERDICTS = [
    ("通過", "結論：通過\n\n沒有重要發現。\n", "pass"),
    ("粗體的通過", "**結論：通過**\n", "pass"),
    ("需要修改", "結論：需要修改\n\n- 有問題。\n", "needs-changes"),
    ("不通過不能被當成通過", "結論：不通過\n", "needs-changes"),
    ("沒有結論行", "看起來還可以。\n", "unavailable"),
]

TOKEN = "fake-claude-oauth-token-0123456789"

# 假的 claude：記下參數和 stdin，印出 FAKE_CLAUDE_STDOUT，用 FAKE_CLAUDE_EXIT 結束。
FAKE_CLAUDE = """#!/usr/bin/env bash
printf '%s\\0' "$@" > "${FAKE_CLAUDE_RECORD}.args"
cat > "${FAKE_CLAUDE_RECORD}.stdin"
printf '%s' "${FAKE_CLAUDE_STDOUT}"
exit "${FAKE_CLAUDE_EXIT}"
"""

def load_workflow():
    dumped = subprocess.run(
        ["ruby", "-ryaml", "-rjson", "-e", "puts JSON.generate(YAML.load_file(ARGV[0]))", str(WORKFLOW)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return json.loads(dumped)


def step(job, step_id):
    return next(s for s in job["steps"] if s.get("id") == step_id)


class AiReviewWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        workflow = load_workflow()
        cls.jobs = workflow["jobs"]
        cls.rules = {name: workflow["env"][name] for name in ("REVIEW_RULES", "REVIEW_FILES_NOTE")}
        cls.claude = cls.jobs["claude-review"]
        cls.gate = cls.jobs["ai-review-gate"]["steps"][0]["run"]

    def run_gate(self, overrides):
        env = {"PATH": os.environ["PATH"], **PASSING, **overrides}
        return subprocess.run(["bash", "-c", self.gate], env=env, capture_output=True, text=True).returncode

    def test_gate_passes_when_claude_passes(self):
        self.assertEqual(self.run_gate({}), 0)

    def test_gate_passes_on_the_transitional_trigger_when_copilot_passes(self):
        self.assertEqual(self.run_gate(TRANSITIONAL), 0)

    def test_gate_blocks(self):
        for label, overrides in GATE_BLOCKED:
            with self.subTest(label):
                self.assertNotEqual(self.run_gate(overrides), 0)

    def test_gate_runs_even_when_the_reviewer_is_skipped(self):
        # 被 if 跳過的必要檢查會被 GitHub 當成通過。
        gate = self.jobs["ai-review-gate"]
        self.assertIn("always()", gate["if"])
        self.assertEqual(gate["name"], "ai-review-gate")
        self.assertEqual(sorted(gate["needs"]), ["claude-review", "read-only-review"])

    def test_only_the_claude_job_on_the_trusted_trigger_gets_secrets(self):
        for name, job in self.jobs.items():
            with self.subTest(name):
                if name == "claude-review":
                    self.assertEqual(job["environment"], "ai-review")
                    self.assertIn("github.event_name == 'pull_request_target'", job["if"])
                    self.assertIn("head.repo.full_name == github.repository", job["if"])
                else:
                    self.assertNotIn("secrets.", json.dumps(job))
                    self.assertNotIn("environment", job)

    def test_copilot_only_runs_on_the_transitional_trigger(self):
        self.assertIn("github.event_name == 'pull_request'", self.jobs["read-only-review"]["if"])

    def run_claude(self, output="", *, exit_code=0, is_error=False, token=TOKEN, install="success"):
        """跑 Claude 審查步驟的 script，回傳（判定, 留言內容, claude 收到的參數或 None, claude 收到的 stdin）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("bin", "ws", "temp"):
                (root / name).mkdir()
            fake = root / "bin" / "claude"
            fake.write_text(FAKE_CLAUDE)
            fake.chmod(0o755)
            (root / "ws" / "pr-review-input.md").write_text("# Pull request diff\n+新增的一行\n")
            record = root / "record"
            env = {
                "PATH": f"{root / 'bin'}{os.pathsep}{os.environ['PATH']}",
                "CLAUDE_CODE_OAUTH_TOKEN": token,
                "CLAUDE_CONFIG_DIR": str(root / "temp" / "claude-home"),
                "RUNNER_TEMP": str(root / "temp"),
                "GITHUB_OUTPUT": str(root / "output"),
                "INSTALL_OUTCOME": install,
                "FAKE_CLAUDE_RECORD": str(record),
                "FAKE_CLAUDE_STDOUT": json.dumps({"is_error": is_error, "result": output}),
                "FAKE_CLAUDE_EXIT": str(exit_code),
                **self.rules,
            }
            done = subprocess.run(
                ["bash", "-c", step(self.claude, "review")["run"]], cwd=root / "ws", env=env, capture_output=True, text=True
            )
            self.assertEqual(done.returncode, 0, done.stderr)
            verdict = (root / "output").read_text().strip().removeprefix("verdict=")
            args_file = Path(f"{record}.args")
            args = args_file.read_text().split("\0")[:-1] if args_file.exists() else None
            stdin = Path(f"{record}.stdin").read_text() if args is not None else ""
            return verdict, (root / "ws" / "review-comment.md").read_text(), args, stdin

    @unittest.skipUnless(shutil.which("jq") and shutil.which("timeout"), "需要 jq 和 timeout")
    def test_claude_verdicts(self):
        for label, output, expected in VERDICTS + [("輸出裡有 token", f"結論：通過\n\n{TOKEN}\n", "unavailable")]:
            with self.subTest(label):
                verdict, comment, args, stdin = self.run_claude(output)
                self.assertEqual(verdict, expected)
                self.assertTrue(comment.startswith("<!-- dotfiles-claude-review -->"))
                self.assertNotIn(TOKEN, comment)
                # diff 從 stdin 進去，Claude 沒有任何工具。
                self.assertIn("+新增的一行", stdin)
                self.assertEqual(args[args.index("--tools") + 1], "")
                self.assertEqual(args[args.index("--system-prompt") + 1], self.rules["REVIEW_RULES"])
                self.assertNotIn("bypassPermissions", args)

    @unittest.skipUnless(shutil.which("jq") and shutil.which("timeout"), "需要 jq 和 timeout")
    def test_claude_failures_block(self):
        for label, kwargs, called in [
            ("CLI 沒裝起來", {"install": "failure"}, False),
            ("沒有 token", {"token": ""}, False),
            ("CLI 失敗結束", {"exit_code": 1}, True),
            ("CLI 回報錯誤", {"is_error": True}, True),
            ("沒有輸出", {"output": ""}, True),
        ]:
            with self.subTest(label):
                verdict, comment, args, _ = self.run_claude(**{"output": "結論：通過\n", **kwargs})
                self.assertEqual(verdict, "unavailable")
                self.assertEqual(args is not None, called)
                self.assertIn("審查沒有跑起來", comment)


if __name__ == "__main__":
    unittest.main()
