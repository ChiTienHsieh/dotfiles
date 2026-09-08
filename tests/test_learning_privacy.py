"""A04: learning/ contents are gitignored; .gitignore itself stays trackable.

Uses a synthetic repo and fixture paths only. Never reads real learning records.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_GITIGNORE = (
    REPO_ROOT / "skills" / "shared" / "level-up" / "learning" / ".gitignore"
)


# Fixture paths relative to a synthetic learning/ directory.
FIXTURE_REL_PATHS = (
    "INDEX.md",
    "user-profile.md",
    "workflow-events.md",
    "topics/example-topic.md",
)


def _run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


class LearningPrivacyGitignoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gitignore_text = SOURCE_GITIGNORE.read_text(encoding="utf-8")

    def test_gitignore_ignores_all_content_but_keeps_itself(self) -> None:
        self.assertIn("*", self.gitignore_text.splitlines())
        self.assertIn("!.gitignore", self.gitignore_text.splitlines())

    def test_synthetic_repo_ignores_fixtures_not_gitignore(self) -> None:
        with tempfile.TemporaryDirectory(prefix="learning-privacy-") as tmp:
            root = Path(tmp)
            learning = root / "skills" / "shared" / "level-up" / "learning"
            topics = learning / "topics"
            topics.mkdir(parents=True)

            (learning / ".gitignore").write_text(self.gitignore_text, encoding="utf-8")
            for rel in FIXTURE_REL_PATHS:
                path = learning / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                # Synthetic fixture only — not real learner content.
                path.write_text("# fixture\n", encoding="utf-8")

            init = _run(["git", "init"], cwd=root)
            self.assertEqual(init.returncode, 0, init.stderr)

            for rel in FIXTURE_REL_PATHS:
                rel_from_root = f"skills/shared/level-up/learning/{rel}"
                ignored = _run(
                    ["git", "check-ignore", "-q", rel_from_root],
                    cwd=root,
                )
                self.assertEqual(
                    ignored.returncode,
                    0,
                    f"expected ignored: {rel_from_root}\n{ignored.stderr}",
                )

            gitignore_rel = "skills/shared/level-up/learning/.gitignore"
            not_ignored = _run(
                ["git", "check-ignore", "-q", gitignore_rel],
                cwd=root,
            )
            self.assertEqual(
                not_ignored.returncode,
                1,
                f".gitignore must remain trackable\n{not_ignored.stdout}",
            )

            add_gi = _run(["git", "add", "-n", gitignore_rel], cwd=root)
            self.assertEqual(add_gi.returncode, 0, add_gi.stderr)
            self.assertIn(gitignore_rel, add_gi.stdout)

            add_index = _run(
                ["git", "add", "-n", "skills/shared/level-up/learning/INDEX.md"],
                cwd=root,
            )
            # git add -n on an ignored path fails or warns; either way INDEX
            # must not appear as a staged path.
            self.assertNotRegex(add_index.stdout, r"(?m)^add '.*INDEX\.md'$")

    def test_check_ignore_no_index_on_fixture_tree(self) -> None:
        """Cover --no-index against fixture paths in a synthetic repo (no index)."""
        with tempfile.TemporaryDirectory(prefix="learning-privacy-ni-") as tmp:
            root = Path(tmp)
            learning = root / "learning"
            topics = learning / "topics"
            topics.mkdir(parents=True)
            (learning / ".gitignore").write_text(self.gitignore_text, encoding="utf-8")
            (learning / "INDEX.md").write_text("# fixture\n", encoding="utf-8")
            (topics / "example-topic.md").write_text("# fixture\n", encoding="utf-8")

            init = _run(["git", "init"], cwd=root)
            self.assertEqual(init.returncode, 0, init.stderr)
            # Do not git-add fixtures; --no-index must not depend on the index.

            for rel in ("learning/INDEX.md", "learning/topics/example-topic.md"):
                result = _run(
                    ["git", "check-ignore", "--no-index", "-q", rel],
                    cwd=root,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"--no-index should ignore {rel}: {result.stderr}",
                )

            gi = _run(
                ["git", "check-ignore", "--no-index", "-q", "learning/.gitignore"],
                cwd=root,
            )
            self.assertEqual(
                gi.returncode,
                1,
                ".gitignore must not be ignored under --no-index",
            )


if __name__ == "__main__":
    unittest.main()
