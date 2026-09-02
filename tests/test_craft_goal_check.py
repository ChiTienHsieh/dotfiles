from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "skills" / "shared" / "craft-goal" / "scripts" / "check_goal_prompt.py"
SKILL = REPO_ROOT / "skills" / "shared" / "craft-goal" / "SKILL.md"


def run_check(text: str, *, via_file: bool = False) -> subprocess.CompletedProcess:
    if via_file:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as handle:
            handle.write(text)
            path = handle.name
        return subprocess.run([sys.executable, str(CHECK_SCRIPT), path], capture_output=True, text=True)
    return subprocess.run([sys.executable, str(CHECK_SCRIPT)], input=text, capture_output=True, text=True)


class CraftGoalCheckTests(unittest.TestCase):
    def test_under_limit_prompt_passes(self) -> None:
        result = run_check("請在 `~/repo` 依照 spec 完成所有任務。")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK: ", result.stdout)
        self.assertIn("limit 4000", result.stdout)

    def test_over_limit_prompt_fails(self) -> None:
        result = run_check("x" * 4000, via_file=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("TOO LONG: 4000 characters", result.stdout)

    def test_skill_prose_points_at_the_script_instead_of_a_number(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        self.assertNotIn("4000", skill)
        self.assertIn("scripts/check_goal_prompt.py", skill)
        self.assertTrue(CHECK_SCRIPT.exists())


if __name__ == "__main__":
    unittest.main()
