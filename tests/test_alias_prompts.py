"""Exercise the interactive alias helpers in both supported shells."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ALIASES = Path(__file__).resolve().parents[1] / "bash/.aliases"
SHELLS = ("bash", "zsh")


def run(shell, script, home, stdin="", cwd=None):
    env = dict(os.environ, HOME=str(home))
    for name in ("BASH_ENV", "ENV", "ZDOTDIR", "OPENAI_API_KEY", "PWD"):
        env.pop(name, None)
    return subprocess.run([shell, "-c", 'source "$1"; ' + script, "fixture", str(ALIASES)],
                          cwd=cwd or home, env=env, input=stdin, text=True,
                          capture_output=True)


class AskTests(unittest.TestCase):
    def test_sets_callers_local_and_keeps_backslashes(self):
        script = ('f() { local answer=old; _ask answer "Name? "; printf "[%s]" "$answer"; }; '
                  'f; printf "{%s}" "${answer-unset}"')
        for shell in SHELLS:
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as home:
                result = run(shell, script, home, stdin="  a b\\c  \n")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "[a b\\c]{unset}")
                self.assertEqual(result.stderr, "Name? ")

    def test_no_zsh_only_read_prompt_left(self):
        # bash reads `read "var?prompt"` as an invalid variable name, so every
        # prompt has to go through _ask (pc needs a real /tmp/prompts to run).
        code = [line for line in ALIASES.read_text().splitlines()
                if not line.lstrip().startswith("#")]
        offenders = [line for line in code if re.search(r"\bread\b[^;|&]*\w\?", line)]
        self.assertEqual(offenders, [])


class AddcdTests(unittest.TestCase):
    def test_retries_after_conflict_and_records_alias(self):
        for shell in SHELLS:
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as directory:
                home = Path(directory)
                project = home / "project"
                project.mkdir()
                result = run(shell, "addcd", home, stdin="ls\njumphere\n", cwd=project)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("not a valid identifier", result.stderr)
                self.assertEqual((home / ".aliases.local").read_text(),
                                 f"alias jumphere='cd {project.resolve()}'\n")


class AddaliTests(unittest.TestCase):
    def test_manual_name_without_api_key_creates_working_alias(self):
        use_alias = ('[ -n "$BASH_VERSION" ] && shopt -s expand_aliases; '
                     'source "$HOME/.aliases.local"; eval zzqq_new')
        for shell in SHELLS:
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as home:
                result = run(shell, "addali", home, stdin="ls\nzzqq_new\necho 'hi there'\n")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("not a valid identifier", result.stderr)
                result = run(shell, use_alias, home)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "hi there\n")

    def test_empty_name_aborts_without_writing(self):
        for shell in SHELLS:
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as home:
                result = run(shell, "addali", home, stdin="\n")
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((Path(home) / ".aliases.local").exists())


if __name__ == "__main__":
    unittest.main()
