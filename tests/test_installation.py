"""Run the actual installer in disposable repositories and homes."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-install-")
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.home = base / "home"
        self.home.mkdir()
        self.repo = base / "repo"
        shutil.copytree(ROOT, self.repo, symlinks=True, ignore=shutil.ignore_patterns(
            ".git", "nvim", "__pycache__", "output", "*.local", "learning"))
        (self.repo / "nvim").mkdir()
        self.env = dict(os.environ, HOME=str(self.home), TMPDIR=str(base),
                        GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env,
                              capture_output=True, text=True, check=True)

    def install(self, repo=None):
        result = subprocess.run(["bash", str((repo or self.repo) / "install.sh")],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fresh_install_and_repeat_create_private_secrets(self):
        self.install()
        directory = self.home / ".secrets"
        index = directory / "index.sh"
        self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
        self.assertEqual(index.stat().st_mode & 0o777, 0o600)
        index.write_text("export FIXTURE_VALUE=retained\n")
        self.install()
        self.assertEqual(index.read_text(), "export FIXTURE_VALUE=retained\n")

    def test_public_learning_is_shared_without_a_private_store(self):
        # Keep excluding real records in setUp; installer coverage uses fixtures.
        learning = self.repo / "skills/shared/level-up/learning"
        (learning / "topics").mkdir(parents=True)
        (learning / "INDEX.md").write_text("[Concept](topics/example.md)\n")
        (learning / "topics/example.md").write_text("Synthetic concept evidence\n")
        self.install()
        for runtime in (".codex", ".claude", ".agents"):
            installed = self.home / runtime / "skills/level-up/learning"
            self.assertEqual((installed / "INDEX.md").read_text(),
                             (learning / "INDEX.md").read_text())
            self.assertEqual((installed / "topics/example.md").read_text(),
                             "Synthetic concept evidence\n")
        self.assertFalse((self.home / ".local/share/level-up/learning").exists())

    def test_codex_prompt_is_generated_from_shared_plus_codex(self):
        self.install()
        prompt = self.home / ".codex/AGENTS.md"
        shared = (self.repo / "agents/AGENTS.md").read_text()
        codex_only = (self.repo / "codex/AGENTS.md").read_text()
        self.assertFalse(prompt.is_symlink())
        text = prompt.read_text()
        self.assertIn(shared, text)
        self.assertIn(codex_only, text)
        self.assertLess(text.index(shared), text.index(codex_only))
        self.assertNotIn("顏文字", text)
        self.assertEqual((self.home / ".codex/agents").resolve(),
                         (self.repo / "codex/agents").resolve())
        self.assertTrue((self.home / ".codex/config.toml").is_file())
        self.assertTrue((self.home / ".codex/hooks.json").is_file())
        # An unchanged rerun does not back up; a source edit regenerates and keeps the old file.
        self.install()
        self.assertFalse((self.home / ".dotfiles_backup").exists())
        (self.repo / "codex/AGENTS.md").write_text(codex_only + "\nfixture codex instruction\n")
        self.install()
        self.assertIn("fixture codex instruction", prompt.read_text())
        backups = list((self.home / ".dotfiles_backup").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / ".codex/AGENTS.md").read_text(), text)

    def test_hand_edited_codex_prompt_is_backed_up_before_regeneration(self):
        self.install()
        prompt = self.home / ".codex/AGENTS.md"
        prompt.write_text("hand-edited live prompt\n")
        self.install()
        self.assertNotIn("hand-edited", prompt.read_text())
        backups = list((self.home / ".dotfiles_backup").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / ".codex/AGENTS.md").read_text(),
                         "hand-edited live prompt\n")

    def test_existing_prompt_link_and_runtime_state_survive_migration(self):
        runtime = self.home / ".codex"
        (runtime / "sessions").mkdir(parents=True)
        (runtime / "sessions/fixture.txt").write_text("local session")
        config = runtime / "config.toml"
        config.write_text('model = "user-selected-model"\n')
        prompt = runtime / "AGENTS.md"
        prompt.symlink_to(self.repo / "codex/AGENTS.md")
        self.install()
        self.install()
        self.assertFalse(runtime.is_symlink())
        self.assertEqual(config.read_text(), 'model = "user-selected-model"\n')
        self.assertEqual((runtime / "sessions/fixture.txt").read_text(), "local session")
        # The old symlink is replaced by the generated file; nothing to back up.
        self.assertFalse(prompt.is_symlink())
        self.assertIn((self.repo / "agents/AGENTS.md").read_text(), prompt.read_text())
        self.assertFalse((self.home / ".dotfiles_backup").exists())

    def test_machine_notes_with_same_basename_all_survive(self):
        originals = {".config/machine.md": "first", ".codex/machine.md": "second",
                     ".claude/machine.md": "third"}
        for relative, value in originals.items():
            path = self.home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)
        self.install()
        self.assertEqual((self.home / ".local/share/machine/machine.md").read_text(), "first")
        backups = list((self.home / ".dotfiles_backup").iterdir())
        self.assertEqual(len(backups), 1)
        for relative, value in originals.items():
            self.assertEqual((backups[0] / relative).read_text(), value)

    def test_existing_secrets_directory_keeps_permissions_and_files(self):
        directory = self.home / ".secrets"
        directory.mkdir(mode=0o700)
        (directory / "provider.sh").write_text("fixture")
        self.install()
        self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
        self.assertEqual((directory / "provider.sh").read_text(), "fixture")
        self.assertEqual((directory / "index.sh").stat().st_mode & 0o777, 0o600)

    def test_conflicting_secrets_index_does_not_block_remaining_setup(self):
        index = self.home / ".secrets/index.sh"
        index.mkdir(parents=True)
        (index / "fixture.txt").write_text("keep")
        self.install()
        self.assertEqual((index / "fixture.txt").read_text(), "keep")
        self.assertTrue((self.home / ".aliases.local").is_symlink())

    def test_legacy_secrets_stays_intact_and_both_shells_load_it(self):
        legacy = self.home / ".secrets"
        legacy.write_text("export FIXTURE_VALUE=legacy\n")
        self.install()
        self.assertEqual(legacy.read_text(), "export FIXTURE_VALUE=legacy\n")
        for shell, config in [("bash", "bash/.bash_profile"), ("zsh", "zsh/.zshrc")]:
            source = (self.repo / config).read_text()
            # Execute the actual secrets startup block without unrelated integrations.
            start = source.index("if [ -f ", source.index("# Source secrets" if shell == "bash" else "# Secrets"))
            block = source[start:source.index("\nfi", start) + 3]
            result = subprocess.run([shell, "-c", block + '\nprintf "%s" "$FIXTURE_VALUE"'],
                                    env=self.env, capture_output=True, text=True)
            self.assertEqual((result.returncode, result.stdout), (0, "legacy"), result.stderr)

    def test_secrets_symlinks_are_not_followed_by_installer(self):
        directory = self.home / ".secrets"
        directory.mkdir()
        target = Path(self.temp.name) / "outside"
        (directory / "index.sh").symlink_to(target)
        self.install()
        self.assertFalse(target.exists())
        self.assertTrue((directory / "index.sh").is_symlink())
        (directory / "index.sh").unlink()
        directory.rmdir()
        directory.symlink_to(target)
        self.install()
        self.assertFalse(target.exists())
        self.assertTrue(directory.is_symlink())

    def test_linked_worktree_installs_hook_and_preserves_previous_hook(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        linked = Path(self.temp.name) / "linked"
        self.git("worktree", "add", "--detach", str(linked))
        (linked / "nvim").mkdir()
        hook = self.repo / ".git/hooks/pre-commit"
        hook.write_text("previous hook\n")
        self.install(linked)
        self.assertTrue(hook.is_symlink())
        self.assertEqual(hook.resolve(), (linked / "hooks/pre-commit").resolve())
        backups = list((self.home / ".dotfiles_backup").glob("*/.repo-hooks/pre-commit"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "previous hook\n")

    def test_plain_directory_inside_parent_repo_does_not_replace_parent_hook(self):
        shutil.rmtree(self.repo / ".git")  # This test's disposable fixture only.
        parent = Path(self.temp.name)
        subprocess.run(["git", "init", "-q"], cwd=parent, env=self.env, check=True)
        hook = parent / ".git/hooks/pre-commit"
        hook.write_text("parent hook must survive\n")
        self.install()
        self.assertFalse(hook.is_symlink())
        self.assertEqual(hook.read_text(), "parent hook must survive\n")


if __name__ == "__main__":
    unittest.main()
