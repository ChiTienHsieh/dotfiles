#!/usr/bin/env python3
"""Regression tests for playwright-cli skill example command order (A12).

Does not launch a real browser. Validates docs against the CLI contract that:
- `open` restarts the session and navigates (default about:blank)
- `tracing-start` / `state-load` require an already-open session
- intended URL navigation must use `goto` after start/load so first load is
  recorded / authenticated
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAYWRIGHT_SKILL = REPO_ROOT / "skills" / "claude" / "playwright-cli"
TRACING = PLAYWRIGHT_SKILL / "references" / "tracing.md"
STORAGE = PLAYWRIGHT_SKILL / "references" / "storage-state.md"
VIDEO = PLAYWRIGHT_SKILL / "references" / "video-recording.md"

BASH_FENCE_RE = re.compile(r"```bash\n(.*?)```", re.DOTALL)
CMD_RE = re.compile(r"(?m)^playwright-cli\b(.*)$")


def bash_blocks(path: Path) -> list[str]:
    return BASH_FENCE_RE.findall(path.read_text(encoding="utf-8"))


def commands(block: str) -> list[list[str]]:
    out: list[list[str]] = []
    for match in CMD_RE.finditer(block):
        # Keep tokens; strip surrounding quotes used in examples.
        tokens = [
            token.strip("'\"")
            for token in match.group(1).split()
            if token.strip("'\"")
        ]
        out.append(tokens)
    return out


def is_blank_open(tokens: list[str]) -> bool:
    """True when open starts a session without navigating to a real page."""
    if not tokens or tokens[0] != "open":
        return False
    args = [t for t in tokens[1:] if not t.startswith("-")]
    if not args:
        return True
    return args[0] in {"about:blank", "about:blank/"}


def is_url_open(tokens: list[str]) -> bool:
    if not tokens or tokens[0] != "open":
        return False
    args = [t for t in tokens[1:] if not t.startswith("-")]
    return bool(args) and args[0] not in {"about:blank", "about:blank/"}


class ExampleOrderContractTests(unittest.TestCase):
    def _assert_setup_before_action(
        self, path: Path, action: str, require_goto: bool = True
    ) -> None:
        blocks = bash_blocks(path)
        relevant = [b for b in blocks if f"playwright-cli {action}" in b]
        self.assertTrue(relevant, f"{path.name}: expected bash examples with {action}")

        for block in relevant:
            cmds = commands(block)
            for idx, tokens in enumerate(cmds):
                if not tokens or tokens[0] != action:
                    continue
                prior_opens = [
                    (j, cmds[j]) for j in range(idx) if cmds[j] and cmds[j][0] == "open"
                ]
                self.assertTrue(
                    prior_opens,
                    f"{path.name}: {action} without a preceding open\n{block}",
                )
                _j, open_tokens = prior_opens[-1]
                self.assertTrue(
                    is_blank_open(open_tokens),
                    f"{path.name}: nearest open before {action} must be blank/"
                    f"about:blank, got {open_tokens!r}\n{block}",
                )
                # No URL-open between blank open and action.
                for mid in cmds[_j + 1 : idx]:
                    self.assertFalse(
                        is_url_open(mid),
                        f"{path.name}: URL open between blank open and {action}: "
                        f"{mid!r}\n{block}",
                    )
                if require_goto:
                    later = cmds[idx + 1 :]
                    goto_idx = next(
                        (
                            k
                            for k, t in enumerate(later)
                            if t and t[0] == "goto"
                        ),
                        None,
                    )
                    self.assertIsNotNone(
                        goto_idx,
                        f"{path.name}: {action} must be followed by goto to the "
                        f"intended URL\n{block}",
                    )
                    # Do not restart via open before that goto.
                    for mid in later[: goto_idx]:
                        self.assertNotEqual(
                            mid[0],
                            "open",
                            f"{path.name}: open before goto would restart and "
                            f"wipe {action}\n{block}",
                        )

    def test_tracing_examples_open_blank_start_then_goto(self) -> None:
        self._assert_setup_before_action(TRACING, "tracing-start", require_goto=True)

    def test_storage_restore_examples_open_blank_load_then_goto(self) -> None:
        self._assert_setup_before_action(STORAGE, "state-load", require_goto=True)

    def test_tracing_never_opens_target_url_before_start(self) -> None:
        for block in bash_blocks(TRACING):
            if "tracing-start" not in block:
                continue
            cmds = commands(block)
            for idx, tokens in enumerate(cmds):
                if tokens and tokens[0] == "tracing-start":
                    for prev in cmds[:idx]:
                        self.assertFalse(
                            is_url_open(prev),
                            "tracing.md must not open the target URL before "
                            f"tracing-start:\n{block}",
                        )

    def test_performance_example_records_goto_inside_trace_window(self) -> None:
        text = TRACING.read_text(encoding="utf-8")
        self.assertIn("### Analyzing Performance", text)
        section = text.split("### Analyzing Performance", 1)[1]
        block = bash_blocks_from_text(section)[0]
        cmds = commands(block)
        names = [c[0] for c in cmds]
        self.assertEqual(
            names[:4],
            ["open", "tracing-start", "goto", "tracing-stop"],
            f"performance example must record first navigation:\n{block}",
        )
        self.assertTrue(is_blank_open(cmds[0]))
        self.assertEqual(cmds[2][1], "https://slow-site.com")

    def test_auth_reuse_restore_targets_dashboard_via_goto(self) -> None:
        text = STORAGE.read_text(encoding="utf-8")
        section = text.split("### Authentication State Reuse", 1)[1]
        block = bash_blocks_from_text(section)[0]
        # Focus on the restore half (after state-save).
        restore = block.split("state-save", 1)[1]
        cmds = commands("playwright-cli state-save" + restore)
        # Drop the save line; keep restore commands.
        restore_cmds = [c for c in cmds if c[0] != "state-save"]
        names = [c[0] for c in restore_cmds]
        self.assertEqual(names[:3], ["open", "state-load", "goto"])
        self.assertTrue(is_blank_open(restore_cmds[0]))
        self.assertEqual(
            restore_cmds[2][1], "https://app.example.com/dashboard"
        )
        self.assertNotIn("reload", names)

    def test_video_recording_keeps_same_order(self) -> None:
        # Sibling reference already documents the correct pattern; keep aligned.
        block = next(
            b for b in bash_blocks(VIDEO) if "video-start" in b and "goto" in b
        )
        cmds = commands(block)
        names = [c[0] for c in cmds]
        start = names.index("video-start")
        self.assertEqual(names[start - 1], "open")
        self.assertTrue(is_blank_open(cmds[start - 1]))
        self.assertIn("goto", names[start + 1 :])


def bash_blocks_from_text(text: str) -> list[str]:
    return BASH_FENCE_RE.findall(text)


if __name__ == "__main__":
    unittest.main()
