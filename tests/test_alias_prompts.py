"""Exercise the interactive alias helpers in both supported shells."""
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ALIASES = Path(__file__).resolve().parents[1] / "bash/.aliases"
SHELLS = ("bash", "zsh")
# Prints the names of addali/addcd variables left behind as globals.
LEAKS = ('; printf "leaked:<%s>" "${alias_name+alias_name }${choice+choice }'
         '${alias_command+alias_command }${alias_command_escaped+alias_command_escaped }'
         '${full_alias+full_alias }${suggested_name+suggested_name }"')
# Stub curl: keep the request body, answer with $FAKE_RESPONSE.
CURL_STUB = ('curl() { while [ $# -gt 0 ]; do [ "$1" = -d ] && printf "%s" "$2" > "$HOME/body.json"; '
             'shift; done; printf "%s" "$FAKE_RESPONSE"; }; ')


def reply(text):
    """An OpenAI Responses API reply whose message comes after a reasoning item."""
    return json.dumps({"output": [
        {"type": "reasoning", "summary": []},
        {"type": "message", "content": [{"type": "output_text", "text": text}]},
    ]})


def run(shell, script, home, stdin="", cwd=None, **extra_env):
    env = dict(os.environ, HOME=str(home))
    for name in ("BASH_ENV", "ENV", "ZDOTDIR", "OPENAI_API_KEY", "ADDALI_MODEL", "PWD"):
        env.pop(name, None)
    env.update(extra_env)
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
        # Only a `read` in command position counts, so an echo that happens
        # to say "read it?" is not flagged.
        zsh_read = re.compile(r"(?:^|[;&|()]|\b(?:then|do|else))\s*read\b[^;|&#]*\w\?")
        code = [line for line in ALIASES.read_text().splitlines()
                if not line.lstrip().startswith("#")]
        offenders = [line for line in code if zsh_read.search(line)]
        self.assertEqual(offenders, [])


class AddcdTests(unittest.TestCase):
    def test_retries_after_conflict_and_records_alias(self):
        for shell in SHELLS:
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as directory:
                home = Path(directory)
                project = home / "project"
                project.mkdir()
                result = run(shell, "addcd" + LEAKS, home, stdin="ls\njumphere\n", cwd=project)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("not a valid identifier", result.stderr)
                self.assertTrue(result.stdout.endswith("leaked:<>"), result.stdout)
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

    def test_accepting_ai_suggestion_creates_alias(self):
        for shell in SHELLS:
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as home:
                result = run(shell, CURL_STUB + "addali" + LEAKS, home,
                             stdin="ls\ny\necho hi\n", OPENAI_API_KEY="dummy",
                             FAKE_RESPONSE=reply("zzqq_ai"))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.endswith("leaked:<>"), result.stdout)
                self.assertEqual((Path(home) / ".aliases.local").read_text(),
                                 "alias zzqq_ai='echo hi'\n")

    def test_empty_name_aborts_without_writing(self):
        for shell in SHELLS:
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as home:
                result = run(shell, "addali", home, stdin="\n")
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((Path(home) / ".aliases.local").exists())


class SuggestNameTests(unittest.TestCase):
    REASONING_REPLY = reply(" qq ")

    def suggest(self, shell, home, response, **extra_env):
        return run(shell, CURL_STUB + "suggest_alternative_name 'l\"s' 'l\"s, ll'", home,
                   OPENAI_API_KEY="dummy", FAKE_RESPONSE=response, **extra_env)

    def test_model_comes_from_env_and_reply_after_reasoning_is_used(self):
        for shell in SHELLS:
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as home:
                result = self.suggest(shell, home, self.REASONING_REPLY, ADDALI_MODEL="custom-model")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "qq\n")
                body = json.loads((Path(home) / "body.json").read_text())
                self.assertEqual(body["model"], "custom-model")
                self.assertIn('l"s, ll', body["input"])

    def test_default_model_is_an_undated_alias(self):
        for shell in SHELLS:
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as home:
                result = self.suggest(shell, home, self.REASONING_REPLY)
                self.assertEqual(result.returncode, 0, result.stderr)
                model = json.loads((Path(home) / "body.json").read_text())["model"]
                self.assertTrue(model)
                self.assertNotRegex(model, r"\d{4}-?\d{2}-?\d{2}$")

    def test_reply_that_is_not_a_plain_name_is_rejected(self):
        for text in ("x; touch pwned", "it's", "two\nlines", "-x"):
            for shell in SHELLS:
                with self.subTest(shell=shell, text=text), \
                        tempfile.TemporaryDirectory() as home:
                    result = self.suggest(shell, home, reply(text))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")

    def test_api_error_is_reported_instead_of_suggested(self):
        error = json.dumps({"error": {"message": "The model `gone` does not exist"}})
        for shell in SHELLS:
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as home:
                result = self.suggest(shell, home, error, ADDALI_MODEL="gone")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("The model `gone` does not exist", result.stderr)


if __name__ == "__main__":
    unittest.main()
