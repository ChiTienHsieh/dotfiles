"""Public learning path allowlist, using synthetic records only."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = (".gitignore", "INDEX.md", "user-profile.md", "topics/example-topic.md")
PRIVATE = ("INDEX.local.md", "workflow-events.md", "raw.md", "private/context.md",
           "topics/raw.json", "topics/raw/context.md", "topics/private/data.md")


class LearningPrivacyTests(unittest.TestCase):
    def test_only_public_paths_stage_and_survive_a_clone(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            repo.mkdir()
            env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)

            def git(*args, cwd=repo, check=True):
                return subprocess.run(["git", *args], cwd=cwd, env=env, text=True,
                                      capture_output=True, check=check)

            git("init", "-q")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            learning = repo / "learning"
            for rel in PUBLIC + PRIVATE:
                path = learning / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# synthetic fixture\n")
            (learning / ".gitignore").write_text(
                (ROOT / "skills/shared/level-up/learning/.gitignore").read_text())
            for rel in PUBLIC + PRIVATE:
                with self.subTest(path=rel):
                    result = git("check-ignore", "--no-index", "-q", f"learning/{rel}", check=False)
                    self.assertEqual(result.returncode, 1 if rel in PUBLIC else 0)
            git("add", ".")
            staged = set(git("diff", "--cached", "--name-only").stdout.splitlines())
            self.assertEqual(staged, {f"learning/{p}" for p in PUBLIC})
            git("commit", "-qm", "Synthetic public progress")
            clone = base / "clone"
            git("clone", "-q", str(repo), str(clone))
            for rel in PUBLIC:
                self.assertEqual((clone / "learning" / rel).read_bytes(),
                                 (learning / rel).read_bytes())
            for rel in PRIVATE:
                self.assertFalse((clone / "learning" / rel).exists())


if __name__ == "__main__":
    unittest.main()
