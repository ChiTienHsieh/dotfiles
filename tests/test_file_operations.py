"""Exercise trash in both supported shells with real disposable files."""
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


if __name__ == "__main__":
    unittest.main()
