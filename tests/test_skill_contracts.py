import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
SYNC_SKILLS = REPO_ROOT / "scripts" / "sync-skills.sh"
CODEX_RUNBOOK = REPO_ROOT / "skills" / "shared" / "delegate" / "runbook" / "codex.md"


def frontmatter(path: Path) -> dict[str, str]:
    """Top-level `key: value` pairs from a SKILL.md frontmatter block."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line == "---":
            break
        key, sep, value = line.partition(":")
        if sep and not line[0].isspace():
            fields[key.strip()] = value.strip().strip("'\"")
    return fields


# 指示檔裡指向同一個 skill 目錄內檔案的路徑；含 `<` 或 `...` 的是佔位範例，不檢查。
LOCAL_REFERENCE_RE = re.compile(
    r"(?:`|\]\()((?:\.\./|scripts/|references/|runbook/|assets/)[^`)\s#]+)"
)


class SkillStructureTests(unittest.TestCase):
    def test_frontmatter_has_name_matching_directory_and_description(self) -> None:
        for skill in sorted(SKILLS_DIR.glob("*/*/SKILL.md")):
            with self.subTest(skill=skill.relative_to(REPO_ROOT)):
                fields = frontmatter(skill)
                self.assertEqual(fields.get("name"), skill.parent.name)
                self.assertTrue(fields.get("description"))

    def test_relative_references_resolve(self) -> None:
        for skill in sorted(SKILLS_DIR.glob("*/*/SKILL.md")):
            for match in LOCAL_REFERENCE_RE.finditer(skill.read_text(encoding="utf-8")):
                reference = match.group(1)
                if "<" in reference or "..." in reference:
                    continue
                with self.subTest(skill=skill.relative_to(REPO_ROOT), reference=reference):
                    self.assertTrue((skill.parent / reference).exists())

    def test_tmux_orchestration_is_never_implicitly_invoked(self) -> None:
        skill_dir = SKILLS_DIR / "shared" / "tmux-orchestration"
        self.assertEqual(
            frontmatter(skill_dir / "SKILL.md").get("disable-model-invocation"), "true"
        )
        openai = (skill_dir / "agents" / "openai.yaml").read_text(encoding="utf-8")
        policy = openai.split("\npolicy:\n", 1)[1]
        self.assertRegex(policy, r"(?m)^[ \t]+allow_implicit_invocation:[ \t]*false[ \t]*$")


class DelegateContractTests(unittest.TestCase):
    def test_codex_exec_never_combines_profile_with_sandbox_flag(self) -> None:
        # `--sandbox` overrides the `-p cc-worker` profile's deny list (codex-cli 0.153.0).
        lines = CODEX_RUNBOOK.read_text(encoding="utf-8").splitlines()
        exec_lines = [line for line in lines if line.startswith("codex exec")]
        self.assertTrue(exec_lines)
        for line in exec_lines:
            self.assertNotIn("--sandbox", line)


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
