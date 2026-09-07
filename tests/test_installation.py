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
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns(
            ".git", "nvim", "__pycache__", "output", "*.local"))
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
