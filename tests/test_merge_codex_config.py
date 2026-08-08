from __future__ import annotations

import stat
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import merge_codex_config  # noqa: E402


PORTABLE = """\
model = "portable-model"

[agents]
enabled = true
max_concurrent_threads_per_session = 100
default_subagent_model = "gpt-5.6-luna"
default_subagent_reasoning_effort = "max"

[plugins."example@openai"]
enabled = true
"""


class MergeCodexConfigTests(unittest.TestCase):
    def test_updates_only_portable_keys_and_preserves_runtime_state(self) -> None:
        destination = """\
model = "runtime-model"
personality = "pragmatic"

[agents]
enabled = false
interrupt_message = false
default_subagent_model = "gpt-5.6-terra"

[projects."/tmp/runtime-project"]
trust_level = "trusted"

[plugins."example@openai"]
enabled = false
runtime_field = "keep"
"""

        merged = merge_codex_config.merge_text(destination, PORTABLE)
        parsed = tomllib.loads(merged)

        self.assertEqual(parsed["model"], "portable-model")
        self.assertEqual(parsed["personality"], "pragmatic")
        self.assertEqual(
            parsed["projects"]["/tmp/runtime-project"]["trust_level"], "trusted"
        )
        self.assertEqual(parsed["agents"]["interrupt_message"], False)
        self.assertEqual(parsed["agents"]["max_concurrent_threads_per_session"], 100)
        self.assertEqual(parsed["agents"]["default_subagent_model"], "gpt-5.6-luna")
        self.assertEqual(parsed["plugins"]["example@openai"]["runtime_field"], "keep")
        self.assertEqual(parsed["plugins"]["example@openai"]["enabled"], True)

    def test_adds_missing_section_and_is_idempotent(self) -> None:
        destination = 'personality = "pragmatic"\n\n[projects."/tmp"]\ntrust_level = "trusted"\n'
        portable = """\
[agents]
enabled = true
max_concurrent_threads_per_session = 100
"""

        once = merge_codex_config.merge_text(destination, portable)
        twice = merge_codex_config.merge_text(once, portable)

        self.assertEqual(once, twice)
        self.assertEqual(once.count("[agents]"), 1)
        self.assertEqual(
            tomllib.loads(once)["agents"]["max_concurrent_threads_per_session"],
            100,
        )

    def test_writes_private_regular_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            portable = root / "portable.toml"
            destination = root / "config.toml"
            portable.write_text("[agents]\nenabled = true\n", encoding="utf-8")
            destination.write_text("personality = \"pragmatic\"\n", encoding="utf-8")
            destination.chmod(0o644)

            changed = merge_codex_config.merge_portable_config(
                portable, destination
            )

            self.assertTrue(changed)
            self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)

    def test_refuses_symlink_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            portable = root / "portable.toml"
            target = root / "target.toml"
            destination = root / "config.toml"
            portable.write_text("[agents]\nenabled = true\n", encoding="utf-8")
            target.write_text("personality = \"pragmatic\"\n", encoding="utf-8")
            destination.symlink_to(target)

            with self.assertRaisesRegex(RuntimeError, "not a regular file"):
                merge_codex_config.merge_portable_config(portable, destination)

            self.assertEqual(target.read_text(), 'personality = "pragmatic"\n')

    def test_rejects_multiline_portable_values(self) -> None:
        portable = """\
[tui]
status_line = [
  "current-dir",
]
"""
        with self.assertRaisesRegex(ValueError, "one bare-key assignment per line"):
            merge_codex_config.merge_text("personality = \"none\"\n", portable)


if __name__ == "__main__":
    unittest.main()
