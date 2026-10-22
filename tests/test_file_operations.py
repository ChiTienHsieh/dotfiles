"""Exercise trash, bak and hide in both supported shells with real disposable files."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ALIASES = Path(__file__).resolve().parents[1] / "bash/.aliases"


class TrashTests(unittest.TestCase):
    def test_collisions_special_names_and_symlinks(self):
        for shell in ("bash", "zsh"):
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as directory:
                home = Path(directory)
                for parent, value in [("a", "first"), ("b", "second")]:
                    (home / parent).mkdir()
                    (home / parent / "same").write_text(value)
                (home / "-leading dash").write_text("third")
                (home / "broken link").symlink_to("missing")
                env = dict(os.environ, HOME=directory)
                command = 'source "$1"; trash -- a/same b/same "-leading dash" "broken link"'
                result = subprocess.run([shell, "-c", command, "fixture", str(ALIASES)],
                                        cwd=home, env=env, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("read-only variable", result.stderr)
                for container in (home / ".Trash").iterdir():
                    self.assertRegex(container.name, r"\.\d{6}-\d{6}\.[A-Za-z0-9]+$")
                entries = list((home / ".Trash").glob("*/*"))
                self.assertEqual(len(entries), 4)
                self.assertEqual(sorted(p.read_text() for p in entries if not p.is_symlink()),
                                 ["first", "second", "third"])
                self.assertEqual(sum(p.is_symlink() for p in entries), 1)
                for original in ["a/same", "b/same", "-leading dash", "broken link"]:
                    self.assertFalse(os.path.lexists(home / original))
                # A second invocation in the same second must also preserve data.
                (home / "a/same").write_text("fourth")
                result = subprocess.run([shell, "-c", 'source "$1"; trash a/same',
                                         "fixture", str(ALIASES)], cwd=home, env=env,
                                        text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(len(list((home / ".Trash").glob("*/*"))), 5)

    def test_missing_operand_and_missing_file_fail(self):
        for shell in ("bash", "zsh"):
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as directory:
                for arguments in ("", " missing-file"):
                    result = subprocess.run([shell, "-c", 'source "$1"; trash' + arguments,
                                             "fixture", str(ALIASES)], cwd=directory,
                                            env=dict(os.environ, HOME=directory),
                                            text=True, capture_output=True)
                    self.assertNotEqual(result.returncode, 0)


def run(shell, command, directory):
    return subprocess.run([shell, "-c", 'source "$1"; ' + command, "fixture", str(ALIASES)],
                          cwd=directory, env=dict(os.environ, HOME=directory),
                          text=True, capture_output=True)


class BakHideTests(unittest.TestCase):
    def make_files(self, root):
        (root / "dir").mkdir()
        (root / "dir/x").write_text("nested")
        (root / "two words").write_text("spaced")
        (root / "folder").mkdir()
        (root / "folder/inner").write_text("inner")

    def test_bak_copies_each_path_beside_itself(self):
        for shell in ("bash", "zsh"):
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.make_files(root)
                result = run(shell, 'bak dir/x "two words" folder/', directory)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((root / "dir/.x.bak").read_text(), "nested")
                self.assertEqual((root / ".two words.bak").read_text(), "spaced")
                self.assertEqual((root / ".folder.bak/inner").read_text(), "inner")
                for original in ("dir/x", "two words", "folder/inner"):
                    self.assertTrue((root / original).exists())

    def test_bak_of_symlink_copies_the_target(self):
        # The dotfiles in ~ are symlinks; a backup that is another link to the
        # same file would change along with it.
        for shell in ("bash", "zsh"):
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "real").write_text("v1")
                (root / "link").symlink_to("real")
                result = run(shell, "bak link", directory)
                self.assertEqual(result.returncode, 0, result.stderr)
                backup = root / ".link.bak"
                self.assertFalse(backup.is_symlink())
                (root / "real").write_text("v2")
                self.assertEqual(backup.read_text(), "v1")

    def test_hide_renames_each_path_in_place(self):
        for shell in ("bash", "zsh"):
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.make_files(root)
                result = run(shell, 'hide dir/x "two words" folder/', directory)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((root / "dir/.x").read_text(), "nested")
                self.assertEqual((root / ".two words").read_text(), "spaced")
                self.assertEqual((root / ".folder/inner").read_text(), "inner")
                for original in ("dir/x", "two words", "folder"):
                    self.assertFalse(os.path.lexists(root / original))

    def test_existing_target_is_left_alone(self):
        for shell in ("bash", "zsh"):
            with self.subTest(shell=shell, command="hide"), \
                    tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.make_files(root)
                (root / "dir/.x").write_text("keep")
                result = run(shell, 'hide dir/x "two words"', directory)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((root / "dir/.x").read_text(), "keep")
                self.assertEqual((root / "dir/x").read_text(), "nested")
                self.assertEqual((root / ".two words").read_text(), "spaced")
            with self.subTest(shell=shell, command="bak"), \
                    tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.make_files(root)
                (root / ".folder.bak").mkdir()
                (root / "dir/.x.bak").write_text("old")
                result = run(shell, 'bak folder dir/x "two words"', directory)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(os.listdir(root / ".folder.bak"), [])
                self.assertEqual((root / "dir/.x.bak").read_text(), "old")
                self.assertEqual((root / ".two words.bak").read_text(), "spaced")

    def test_missing_path_fails_but_others_still_run(self):
        for shell in ("bash", "zsh"):
            for command, created in (("bak", "dir/.x.bak"), ("hide", "dir/.x")):
                with self.subTest(shell=shell, command=command), \
                        tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    self.make_files(root)
                    result = run(shell, command + " missing dir/x", directory)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertTrue((root / created).exists())
                    self.assertNotEqual(run(shell, command, directory).returncode, 0)


if __name__ == "__main__":
    unittest.main()
