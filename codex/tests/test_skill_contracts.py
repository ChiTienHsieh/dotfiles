from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
NAME_TASK = REPO_ROOT / "skills" / "codex" / "name-task" / "SKILL.md"
WRAP = REPO_ROOT / "skills" / "shared" / "wrap" / "SKILL.md"


class ArchiveSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.name_task = NAME_TASK.read_text(encoding="utf-8")
        cls.wrap = WRAP.read_text(encoding="utf-8")

    def test_wrap_reads_name_task_without_running_its_workflow(self) -> None:
        self.assertIn("~/dotfiles/skills/codex/name-task/SKILL.md", self.wrap)
        self.assertIn("不得執行 `name-task` 的完整流程", self.wrap)
        self.assertNotIn("Call the Skill tool with `name-task`.", self.wrap)

    def test_workflow_handoffs_use_the_skill_tool(self) -> None:
        self.assertIn("明確呼叫 `$wrap`", self.name_task)
        self.assertIn("Call the Skill tool with `wrap`.", self.name_task)
        self.assertIn("明確呼叫 `$tidy-workspace`", self.wrap)
        self.assertIn("Call the Skill tool with `tidy-workspace`.", self.wrap)

    def test_archive_status_requires_a_passed_target_specific_check(self) -> None:
        self.assertIn("只進行封存前檢查並回傳結果，不要更新標題", self.name_task)
        self.assertIn("該 task 的同等封存前檢查已通過", self.name_task)

    def test_status_update_preserves_a_complete_title(self) -> None:
        self.assertIn("替換開頭既有的分類 emoji", self.name_task)
        self.assertIn("若沒有，就在最前面插入", self.name_task)
        self.assertIn("不得把完整標題縮成單一 emoji", self.name_task)


if __name__ == "__main__":
    unittest.main()
