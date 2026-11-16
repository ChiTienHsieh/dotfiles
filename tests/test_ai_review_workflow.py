"""確認 AI 審查 workflow 的關卡只在該放行時放行，憑證只有 Codex job 拿得到。"""

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
    "CODEX_RESULT": "success",
    "CODEX_VERDICT": "pass",
    "COPILOT_RESULT": "success",
    "COPILOT_VERDICT": "pass",
    "EVENT_NAME": "pull_request_target",
    "HEAD_REPOSITORY": "owner/repo",
    "REPOSITORY": "owner/repo",
}

GATE_BLOCKED = [
    ("Codex 判定需要修改", {"CODEX_VERDICT": "needs-changes"}),
    ("Codex 沒跑起來", {"CODEX_VERDICT": "unavailable"}),
    ("Codex job 被跳過", {"CODEX_RESULT": "skipped", "CODEX_VERDICT": ""}),
    ("Codex job 被取消", {"CODEX_RESULT": "cancelled", "CODEX_VERDICT": ""}),
    ("Codex 有判定但 job 失敗（憑證沒存回去）", {"CODEX_RESULT": "failure"}),
    ("Copilot 判定需要修改", {"COPILOT_VERDICT": "needs-changes"}),
    ("Copilot job 被跳過", {"COPILOT_RESULT": "skipped", "COPILOT_VERDICT": ""}),
    ("fork 來的 PR", {"HEAD_REPOSITORY": "stranger/repo"}),
    ("base 不是 main", {"BASE_REF": "scratch"}),
    ("作者不是 owner 或 collaborator", {"AUTHOR_ASSOCIATION": "CONTRIBUTOR"}),
    (
        "過渡用的 pull_request 觸發，Copilot 沒通過",
        {"EVENT_NAME": "pull_request", "CODEX_RESULT": "skipped", "CODEX_VERDICT": "", "COPILOT_VERDICT": "needs-changes"},
    ),
]

# （說明, Codex 的輸出, 預期判定）
VERDICTS = [
    ("通過", "結論：通過\n\n沒有重要發現。\n", "pass"),
    ("粗體的通過", "**結論：通過**\n", "pass"),
    ("需要修改", "結論：需要修改\n\n- 有問題。\n", "needs-changes"),
    ("不通過不能被當成通過", "結論：不通過\n", "needs-changes"),
    ("沒有結論行", "看起來還可以。\n", "unavailable"),
    ("輸出裡有憑證片段", "結論：通過\n\nSECRET-REFRESH-TOKEN-VALUE-0123456789\n", "unavailable"),
]

FAKE_AUTH = {
    "auth_mode": "chatgpt",
    "OPENAI_API_KEY": None,
    "tokens": {
        "id_token": "aaaaaaaaaaaaaaaaaaaa.bbbbbbbbbbbbbbbbbbbb.cccccccccccccccccccc",
        "access_token": "dddddddddddddddddddd.eeeeeeeeeeeeeeeeeeee.ffffffffffffffffffff",
        "refresh_token": "SECRET-REFRESH-TOKEN-VALUE-0123456789",
        "account_id": "acct",
    },
}

# 假的 codex：把 FAKE_CODEX_OUTPUT 寫進 --output-last-message 指定的檔案。
FAKE_CODEX = """#!/usr/bin/env bash
while [ "$#" -gt 0 ]; do
  if [ "$1" = --output-last-message ]; then printf '%s' "${FAKE_CODEX_OUTPUT}" > "$2"; fi
  shift
done
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
        cls.jobs = load_workflow()["jobs"]
        cls.gate = cls.jobs["ai-review-gate"]["steps"][0]["run"]
        cls.codex = cls.jobs["codex-review"]

    def run_gate(self, overrides):
        env = {"PATH": os.environ["PATH"], **PASSING, **overrides}
        return subprocess.run(["bash", "-c", self.gate], env=env, capture_output=True, text=True).returncode

    def test_gate_passes_when_both_reviewers_pass(self):
        self.assertEqual(self.run_gate({}), 0)

    def test_gate_blocks(self):
        for label, overrides in GATE_BLOCKED:
            with self.subTest(label):
                self.assertNotEqual(self.run_gate(overrides), 0)

    def test_gate_runs_even_when_a_reviewer_is_skipped(self):
        # 被 if 跳過的必要檢查會被 GitHub 當成通過。
        gate = self.jobs["ai-review-gate"]
        self.assertIn("always()", gate["if"])
        self.assertEqual(gate["name"], "ai-review-gate")
        self.assertEqual(sorted(gate["needs"]), ["codex-review", "read-only-review"])

    def test_only_the_codex_job_on_the_trusted_trigger_gets_secrets(self):
        self.assertEqual(self.codex["environment"], "codex-review")
        self.assertIn("github.event_name == 'pull_request_target'", self.codex["if"])
        self.assertIn("head.repo.full_name == github.repository", self.codex["if"])
        for name, job in self.jobs.items():
            if name != "codex-review":
                self.assertNotIn("secrets.", json.dumps(job), name)
                self.assertNotIn("environment", job, name)

    def test_credential_is_restored_only_after_the_sandbox_probe(self):
        self.assertIn("steps.sandbox-probe.outcome == 'success'", step(self.codex, "credential")["if"])
        self.assertNotIn("secrets.", json.dumps(step(self.codex, "sandbox-probe")))
        self.assertNotIn("secrets.", json.dumps(step(self.codex, "review")))

    def run_review(self, outcomes, output=""):
        """跑 Codex 審查步驟的 script，回傳（判定, 留言內容, codex 有沒有被呼叫）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("bin", "ws", "temp", "home"):
                (root / name).mkdir()
            called = root / "codex-called"
            fake = root / "bin" / "codex"
            fake.write_text(FAKE_CODEX + f"touch '{called}'\n")
            fake.chmod(0o755)
            (root / "home" / "auth.json").write_text(json.dumps(FAKE_AUTH))
            # token 片段的 jq 規則是 sandbox 自我檢查那一步寫出來的，照抄它的內容。
            probe = step(self.codex, "sandbox-probe")["run"]
            jq_filter = next(line for line in probe.splitlines() if line.startswith("[.tokens"))
            (root / "temp" / "codex-token-parts.jq").write_text(jq_filter + "\n")
            env = {
                "PATH": f"{root / 'bin'}{os.pathsep}{os.environ['PATH']}",
                "CODEX_HOME": str(root / "home"),
                "RUNNER_TEMP": str(root / "temp"),
                "GITHUB_WORKSPACE": str(root / "ws"),
                "GITHUB_OUTPUT": str(root / "output"),
                "FAKE_CODEX_OUTPUT": output,
                "INSTALL_OUTCOME": "success",
                "PROBE_OUTCOME": "success",
                "CREDENTIAL_OUTCOME": "success",
                **outcomes,
            }
            done = subprocess.run(
                ["bash", "-c", step(self.codex, "review")["run"]], cwd=root / "ws", env=env, capture_output=True, text=True
            )
            self.assertEqual(done.returncode, 0, done.stderr)
            verdict = (root / "output").read_text().strip().removeprefix("verdict=")
            return verdict, (root / "ws" / "review-comment.md").read_text(), called.exists()

    @unittest.skipUnless(shutil.which("jq") and shutil.which("timeout"), "需要 jq 和 timeout")
    def test_codex_verdicts(self):
        for label, output, expected in VERDICTS:
            with self.subTest(label):
                verdict, comment, called = self.run_review({}, output)
                self.assertEqual(verdict, expected)
                self.assertTrue(called)
                self.assertTrue(comment.startswith("<!-- dotfiles-codex-review -->"))
                self.assertNotIn(FAKE_AUTH["tokens"]["refresh_token"], comment)

    def test_codex_is_not_run_when_an_earlier_step_failed(self):
        for failed in ("INSTALL_OUTCOME", "PROBE_OUTCOME", "CREDENTIAL_OUTCOME"):
            with self.subTest(failed):
                verdict, comment, called = self.run_review({failed: "failure"}, "結論：通過\n")
                self.assertEqual(verdict, "unavailable")
                self.assertFalse(called)
                self.assertIn("審查沒有跑起來", comment)

    def run_persist(self, refreshed=True, gh_exit=0, token="writeback", auth=FAKE_AUTH):
        """跑存回憑證的 script，回傳（exit code, gh 收到的內容或 None, 憑證目錄還在不在）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("bin", "ws", "temp", "home"):
                (root / name).mkdir()
            received = root / "gh-received"
            gh = root / "bin" / "gh"
            gh.write_text(f"#!/usr/bin/env bash\necho \"$*\" > '{received}'\ncat >> '{received}'\nexit {gh_exit}\n")
            gh.chmod(0o755)
            probe = step(self.codex, "sandbox-probe")["run"]
            jq_filter = next(line for line in probe.splitlines() if line.startswith("[.tokens"))
            (root / "temp" / "codex-token-parts.jq").write_text(jq_filter + "\n")
            auth_file = root / "home" / "auth.json"
            if auth is not None:
                auth_file.write_text(json.dumps(auth))
            before = json.dumps({**FAKE_AUTH, "last_refresh": "old"}) if refreshed else json.dumps(auth)
            digest = subprocess.run(["sha256sum"], input=before, capture_output=True, text=True, check=True).stdout
            (root / "temp" / "codex-auth.sha256").write_text(digest)
            env = {
                "PATH": f"{root / 'bin'}{os.pathsep}{os.environ['PATH']}",
                "CODEX_HOME": str(root / "home"),
                "RUNNER_TEMP": str(root / "temp"),
                "GH_TOKEN": token,
                "REPOSITORY": "owner/repo",
            }
            done = subprocess.run(
                ["bash", "-c", step(self.codex, "persist")["run"]], cwd=root / "ws", env=env, capture_output=True, text=True
            )
            return done.returncode, received.read_text() if received.exists() else None, (root / "home").exists()

    @unittest.skipUnless(shutil.which("jq") and shutil.which("sha256sum"), "需要 jq 和 sha256sum")
    def test_refreshed_login_is_stored_back(self):
        with self.subTest("沒換 token 就不動 secret"):
            code, received, home_left = self.run_persist(refreshed=False)
            self.assertEqual((code, received, home_left), (0, None, False))
        with self.subTest("換了 token 就存回 environment secret"):
            code, received, home_left = self.run_persist()
            self.assertEqual(code, 0)
            self.assertIn("secret set CODEX_AUTH_JSON --env codex-review --repo owner/repo", received)
            self.assertIn(FAKE_AUTH["tokens"]["refresh_token"], received)
            self.assertFalse(home_left)
        for label, kwargs in [
            ("存回失敗", {"gh_exit": 1}),
            ("沒有存回用的 token", {"token": ""}),
            ("登入在執行中失效", {"auth": None}),
        ]:
            with self.subTest(label):
                code, _, home_left = self.run_persist(**kwargs)
                self.assertNotEqual(code, 0)
                self.assertFalse(home_left)


if __name__ == "__main__":
    unittest.main()
