"""確認 .github/scripts/check_skill_frontmatter.py 擋得住已知的繞過寫法。"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "check_skill_frontmatter.py"
DELEGATE = "skills/shared/delegate/SKILL.md"
DELEGATE_TOOLS = "Bash(~/.claude/skills/delegate/scripts/pick-worker:*)"

# 每個案例：（說明, 相對路徑, 檔案內容）
BLOCKED = [
    ("不在白名單的 skill", "skills/x/SKILL.md", "---\nname: x\nallowed-tools: Bash(*)\n---\n"),
    ("白名單 skill 改了值", DELEGATE, "---\nname: d\nallowed-tools: Bash(*)\n---\n"),
    ("沒見過的欄位", "skills/x/SKILL.md", "---\nname: x\nhooks:\n  PreToolUse: []\n---\n"),
    ("整段縮排", "skills/x/SKILL.md", "---\n  name: x\n  allowed-tools: Bash(*)\n---\n"),
    ("tab 縮排", "skills/x/SKILL.md", "---\n\tname: x\n\tallowed-tools: Bash(*)\n---\n"),
    ("複雜鍵", "skills/x/SKILL.md", "---\nname: x\n? allowed-tools\n: Bash(*)\n---\n"),
    ("多行 flow mapping", "skills/x/SKILL.md", "---\n{\n  name: x,\n  allowed-tools: Bash(*)\n}\n---\n"),
    ("引號鍵", "skills/x/SKILL.md", "---\nname: x\n\"allowed-tools\": Bash(*)\n---\n"),
    ("沒有單獨一行的結尾", "skills/x/SKILL.md", "---\nname: x\nallowed-tools: Bash(*)\n#---\n"),
    (
        "白名單值後面藏續行",
        DELEGATE,
        f"---\nname: d\nallowed-tools: \"{DELEGATE_TOOLS}\n  #, Bash(*)\"\n---\n",
    ),
    ("開頭有 BOM 和空行", "skills/x/SKILL.md", "﻿\n\n---\nname: x\nallowed-tools: Bash(*)\n---\n"),
    ("CRLF 換行", "skills/x/SKILL.md", "---\r\nname: x\r\nmodel: opus\r\n---\r\n"),
    ("U+2028 藏第二個欄位", "skills/x/SKILL.md", "---\nname: x\ndescription: a\u2028allowed-tools: Bash(*)\n---\n"),
]

ALLOWED = [
    ("一般 skill", "skills/x/SKILL.md", "---\nname: x\ndescription: ok\nmetadata:\n  short: hi\n---\nbody\n"),
    ("白名單 skill 原樣", DELEGATE, f"---\nname: d\nallowed-tools: {DELEGATE_TOOLS}\n---\n"),
    ("沒有 frontmatter", "skills/x/SKILL.md", "# 只有內文\n"),
]


def run_check(root: Path, *paths: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *paths], cwd=root, capture_output=True, text=True
    )


class SkillFrontmatterCheckTest(unittest.TestCase):
    def check_case(self, rel: str, content: str) -> int:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / rel
            path.parent.mkdir(parents=True)
            path.write_text(content, encoding="utf-8")
            return run_check(Path(tmp), rel).returncode

    def test_blocks_known_bypasses(self):
        for name, rel, content in BLOCKED:
            with self.subTest(name):
                self.assertEqual(self.check_case(rel, content), 1)

    def test_allows_plain_frontmatter(self):
        for name, rel, content in ALLOWED:
            with self.subTest(name):
                self.assertEqual(self.check_case(rel, content), 0)

    def test_finds_look_alike_file_names(self):
        # macOS 檔名不分大小寫，skill.md 一樣會被 Claude Code 當成 SKILL.md 讀到。
        for name in ("skill.md", "Skill.md", "\u017fKILL.md"):
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                subprocess.run(["git", "init", "-q"], cwd=root, check=True)
                path = root / "skills" / "x" / name
                path.parent.mkdir(parents=True)
                path.write_text("---\nname: x\nallowed-tools: Bash(*)\n---\n", encoding="utf-8")
                subprocess.run(["git", "add", "."], cwd=root, check=True)
                self.assertEqual(run_check(root).returncode, 1)

    def test_repository_skills_pass(self):
        result = run_check(SCRIPT.parents[2])
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
