import os
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS = REPO_ROOT / "codex" / "AGENTS.md"
NAME_TASK = REPO_ROOT / "skills" / "codex" / "name-task" / "SKILL.md"
TIDY_WORKSPACE = REPO_ROOT / "skills" / "shared" / "tidy-workspace" / "SKILL.md"
WRAP = REPO_ROOT / "skills" / "shared" / "wrap" / "SKILL.md"
SYNC_SKILLS = REPO_ROOT / "scripts" / "sync-skills.sh"


class ArchiveSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.name_task = NAME_TASK.read_text(encoding="utf-8")
        cls.wrap = WRAP.read_text(encoding="utf-8")

    def test_wrap_reads_name_task_without_running_its_workflow(self) -> None:
        self.assertIn("名稱精確為 `name-task` 的唯一項目", self.wrap)
        self.assertIn("不得執行 `name-task` 的完整流程", self.wrap)
        self.assertNotIn("Call the Skill tool with `name-task`.", self.wrap)
        self.assertNotIn("~/dotfiles/skills/codex/name-task/SKILL.md", self.wrap)

    def test_name_task_uses_the_bounded_archive_check(self) -> None:
        self.assertIn("名稱精確為 `wrap` 的唯一項目", self.name_task)
        self.assertIn("找不到、不唯一或缺少該流程時停止", self.name_task)
        self.assertIn("只執行其中的「封存前檢查」流程", self.name_task)
        self.assertIn("不得完成未竟工作、修改文件、呼叫 `$tidy-workspace`", self.wrap)
        self.assertIn("變更 Git 或遠端狀態", self.wrap)
        self.assertNotIn("~/dotfiles/skills/shared/wrap/SKILL.md", self.name_task)

    def test_shared_handoff_has_a_runtime_neutral_fallback(self) -> None:
        self.assertIn("Call the Skill tool with `tidy-workspace`.", self.wrap)
        self.assertIn("完整讀取 `../tidy-workspace/SKILL.md`", self.wrap)

    def test_archive_status_requires_a_passed_target_specific_check(self) -> None:
        self.assertIn("檢查通過才可繼續", self.name_task)
        self.assertIn("該 task 的同等封存前檢查已通過", self.name_task)

    def test_status_update_preserves_a_complete_title(self) -> None:
        self.assertIn("替換開頭既有 emoji", self.name_task)
        self.assertIn("若沒有，就在最前面插入", self.name_task)
        self.assertIn("不得把完整標題縮成單一 emoji", self.name_task)

    def test_domain_emoji_and_pin_are_independent(self) -> None:
        self.assertIn("可用 domain emoji 表示長期 workstream", self.name_task)
        self.assertIn("Pin 是「使用者目前要持續注意」的唯一依據", self.name_task)
        self.assertIn("標題與 pin 是兩項獨立資訊", self.name_task)

    def test_title_remains_human_readable(self) -> None:
        self.assertIn("不了解內部 schema、tab 名稱或 agent workflow", self.name_task)


class GitCleanupContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.agents = AGENTS.read_text(encoding="utf-8")
        cls.tidy = TIDY_WORKSPACE.read_text(encoding="utf-8")
        cls.tidy_flat = " ".join(cls.tidy.split())
        cls.wrap = WRAP.read_text(encoding="utf-8")

    def test_global_contract_assigns_terminal_responsibility(self) -> None:
        self.assertIn("建立者或目前 controller", self.agents)
        self.assertIn("branch、worktree 與 PR 負責到終態", self.agents)
        self.assertIn("以 `tidy-workspace` skill 為準", self.agents)

    def test_tidy_requires_complete_cleanup_evidence(self) -> None:
        for evidence in (
            "precisely identified",
            "no active task, process, or worktree",
            "no dirty, untracked, stashed, or unpushed unique data",
            "verified copy is sufficient to recover",
            "readback confirming the target state",
        ):
            self.assertIn(evidence, self.tidy_flat)

    def test_tidy_covers_squash_and_stop_conditions(self) -> None:
        self.assertIn(
            "For squash merges, Git ancestry alone is not proof", self.tidy_flat
        )
        self.assertIn("PR head OID", self.tidy_flat)
        self.assertIn(
            "deleting a remote copy also requires another verified recovery copy",
            self.tidy_flat,
        )
        self.assertIn("permits exact-target `git branch -D`", self.tidy_flat)
        self.assertIn("is not history rewriting", self.tidy_flat)
        self.assertIn(
            "Age or staleness alone never proves deletion is safe", self.tidy_flat
        )
        self.assertIn("Leave user and other-agent artifacts untouched", self.tidy_flat)
        for stop_condition in (
            "worktree is dirty",
            "active task or agent still owns or uses the target",
            "evidence conflicts",
            "force-push, history rewriting",
        ):
            self.assertIn(stop_condition, self.tidy_flat)
        self.assertIn(
            "current task remaining live for wrap-up or reporting is not target use",
            self.tidy_flat,
        )

    def test_wrap_delegates_terminal_cleanup_without_recursion(self) -> None:
        self.assertIn("Git artifacts 收到 terminal cleanup", self.wrap)
        self.assertIn("可完成的 terminal cleanup 不得留給未來 session", self.wrap)
        self.assertIn("證據不足時視為未完成責任並回報 blocker", self.wrap)
        self.assertIn("cleanup 判斷都以該 skill 為準", self.wrap)
        self.assertNotIn("`$wrap`", self.tidy)


class SkillSyncTests(unittest.TestCase):
    def test_sync_routes_skills_and_preserves_unrelated_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            home = temp / "home"
            backup = temp / "backup"
            legacy = temp / "legacy-claude-skills"
            legacy_codex = temp / "legacy-codex-skills"
            external = temp / "external-skill"

            (legacy / "external-claude").mkdir(parents=True)
            (legacy / "external-claude" / "SKILL.md").write_text("external\n")
            external.mkdir()
            (external / "SKILL.md").write_text("external\n")
            (legacy_codex / ".system").mkdir(parents=True)
            (legacy_codex / "external-codex").symlink_to(external)

            (home / ".claude").mkdir(parents=True)
            (home / ".claude" / "skills").symlink_to(legacy)
            (home / ".codex").mkdir(parents=True)
            (home / ".codex" / "skills").symlink_to(legacy_codex)
            (home / ".agents" / "skills").mkdir(parents=True)
            (home / ".agents" / "skills" / "retired").symlink_to(
                REPO_ROOT / "skills" / "shared" / "retired"
            )
            collision = home / ".agents" / "skills" / "learn-my-voice"
            collision.mkdir(parents=True)
            (collision / "marker").write_text("keep me\n")

            env = os.environ.copy()
            env.update(
                HOME=str(home),
                TMPDIR=str(temp),
                DOTFILES_BACKUP_DIR=str(backup),
            )
            for _ in range(2):
                result = subprocess.run(
                    [str(SYNC_SKILLS)],
                    check=True,
                    capture_output=True,
                    env=env,
                    text=True,
                )
                self.assertIn("Skills synced.", result.stdout)

            expected = {
                home / ".claude" / "skills": (
                    REPO_ROOT / "skills" / "shared",
                    REPO_ROOT / "skills" / "claude",
                ),
                home / ".codex" / "skills": (
                    REPO_ROOT / "skills" / "shared",
                    REPO_ROOT / "skills" / "codex",
                ),
                home / ".agents" / "skills": (
                    REPO_ROOT / "skills" / "shared",
                    REPO_ROOT / "skills" / "codex",
                ),
            }
            for destination, source_dirs in expected.items():
                for source_dir in source_dirs:
                    for skill in source_dir.iterdir():
                        if not (skill.is_dir() and (skill / "SKILL.md").is_file()):
                            continue
                        installed = destination / skill.name
                        self.assertTrue(installed.is_symlink(), installed)
                        self.assertEqual(os.readlink(installed), str(skill))

            self.assertEqual(
                os.readlink(home / ".claude" / "skills" / "external-claude"),
                str(legacy / "external-claude"),
            )
            self.assertEqual(
                os.readlink(home / ".codex" / "skills" / "external-codex"),
                str(legacy_codex / "external-codex"),
            )
            self.assertEqual(
                (home / ".codex" / "skills" / "external-codex").resolve(),
                external.resolve(),
            )
            self.assertTrue((home / ".codex" / "skills" / ".system").is_dir())
            retired = home / ".agents" / "skills" / "retired"
            self.assertFalse(retired.exists())
            self.assertFalse(retired.is_symlink())
            self.assertEqual(
                (backup / ".agents" / "skills" / "learn-my-voice" / "marker").read_text(),
                "keep me\n",
            )

    def test_installer_delegates_skill_sync_to_the_script(self) -> None:
        installer = (REPO_ROOT / "install.sh").read_text()

        self.assertEqual(installer.count('"$DOTFILES_DIR/scripts/sync-skills.sh"'), 1)
        self.assertNotIn('"$DOTFILES_DIR"/skills/shared/*', installer)


if __name__ == "__main__":
    unittest.main()
