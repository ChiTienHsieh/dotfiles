#!/usr/bin/env python3
"""Regression tests for daily-loop mine_transcripts.sh (A14, A17).

Uses synthetic transcripts under an isolated HOME/TMPDIR in /tmp.
Never reads live ~/.claude or ~/.codex transcripts.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "shared" / "daily-loop" / "scripts" / "mine_transcripts.sh"
FIXTURE_ROOT = Path("/tmp/dotfiles-fix-20260907-daily-loop-fixtures")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def run_mine(
    home: Path,
    tmpdir: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["TMPDIR"] = str(tmpdir)
    # Avoid leaking user locale quirks into fixture parsing.
    env.setdefault("LC_ALL", "C")
    result = subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"mine_transcripts failed ({result.returncode})\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def count_md_snippets(md: str) -> int:
    # Representative asks are indented list items under Projects.
    return len(re.findall(r"^  - ", md, flags=re.M))


def count_json_snippets(payload: dict) -> int:
    return sum(len(p.get("snippets") or []) for p in payload.get("projects") or [])


class DailyLoopMineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not SCRIPT.is_file():
            raise unittest.SkipTest(f"missing script: {SCRIPT}")

    def setUp(self) -> None:
        FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
        self._ctx = tempfile.TemporaryDirectory(prefix="daily-loop-", dir=str(FIXTURE_ROOT))
        self.root = Path(self._ctx.name)
        self.home = self.root / "home"
        self.tmpdir = self.root / "tmpdir"
        self.home.mkdir()
        self.tmpdir.mkdir()
        self.claude_root = self.home / ".claude" / "projects"
        self.codex_root = self.home / ".codex" / "sessions"
        self.state_file = self.home / "scratch" / "daily-loop" / "state.jsonl"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.now = utc_now_iso()

    def tearDown(self) -> None:
        self._ctx.cleanup()

    def test_bash_syntax(self) -> None:
        result = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a14_resumed_codex_session_in_old_day_dir_is_included(self) -> None:
        """Old create-day folder with fresh mtime/events must enter the digest."""
        today = datetime.now().strftime("%Y/%m/%d")
        old_day = (datetime.now() - timedelta(days=10)).strftime("%Y/%m/%d")

        fresh = self.codex_root / today / "rollout-fresh.jsonl"
        resumed = self.codex_root / old_day / "rollout-resumed.jsonl"

        write_jsonl(
            fresh,
            [
                {
                    "type": "session_meta",
                    "timestamp": self.now,
                    "payload": {"id": "fresh", "cwd": "/synthetic/fresh"},
                },
                {
                    "type": "event_msg",
                    "timestamp": self.now,
                    "payload": {
                        "type": "user_message",
                        "message": "Synthetic fresh session request text",
                    },
                },
            ],
        )
        write_jsonl(
            resumed,
            [
                {
                    "type": "session_meta",
                    "timestamp": self.now,
                    "payload": {"id": "resumed", "cwd": "/synthetic/resumed"},
                },
                {
                    "type": "event_msg",
                    "timestamp": self.now,
                    "payload": {
                        "type": "user_message",
                        "message": "Synthetic resumed session request text",
                    },
                },
            ],
        )
        # Ensure find -newermt sees both files as recent even if the parent
        # directory path encodes an old create day.
        os.utime(fresh, None)
        os.utime(resumed, None)

        result = run_mine(
            self.home,
            self.tmpdir,
            "--since",
            "24",
            "--source",
            "codex",
            "--format",
            "json",
            "--max-snippets",
            "40",
        )
        payload = json.loads(result.stdout)
        cwds = sorted(p["cwd"] for p in payload["projects"])
        self.assertEqual(cwds, ["/synthetic/fresh", "/synthetic/resumed"])
        self.assertEqual(payload["totals"]["sessions"], 2)

    def test_a14_stale_events_outside_window_still_filtered(self) -> None:
        """mtime discovery is only a candidate prefilter; timestamps still gate."""
        old_day = (datetime.now() - timedelta(days=10)).strftime("%Y/%m/%d")
        stale_ts = (datetime.now(timezone.utc) - timedelta(days=3)).strftime(
            "%Y-%m-%dT%H:%M:%S.%f"
        )[:-3] + "Z"
        path = self.codex_root / old_day / "rollout-stale.jsonl"
        write_jsonl(
            path,
            [
                {
                    "type": "session_meta",
                    "timestamp": stale_ts,
                    "payload": {"id": "stale", "cwd": "/synthetic/stale"},
                },
                {
                    "type": "event_msg",
                    "timestamp": stale_ts,
                    "payload": {
                        "type": "user_message",
                        "message": "Synthetic stale session request text",
                    },
                },
            ],
        )
        os.utime(path, None)  # recent mtime, old event timestamps

        result = run_mine(
            self.home,
            self.tmpdir,
            "--since",
            "24",
            "--source",
            "codex",
            "--format",
            "json",
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["totals"]["sessions"], 0)
        self.assertEqual(payload["projects"], [])

    def _seed_three_claude_projects(self) -> None:
        for i in range(3):
            rows = [
                {
                    "type": "user",
                    "timestamp": self.now,
                    "cwd": f"/synthetic/claude{i}",
                    "message": {"content": f"Synthetic prompt number {j} for cap test"},
                }
                for j in range(3)
            ]
            write_jsonl(self.claude_root / f"proj{i}" / f"session{i}.jsonl", rows)
            os.utime(self.claude_root / f"proj{i}" / f"session{i}.jsonl", None)

    def test_a17_max_snippets_global_cap_md_and_json(self) -> None:
        """--max-snippets is a cross-project global cap; MD and JSON agree; 0 means 0."""
        self._seed_three_claude_projects()

        expected = {
            0: 0,
            1: 1,
            40: 9,  # 3 projects × 3 prompts, all under the default-sized cap
        }
        for cap, want in expected.items():
            with self.subTest(cap=cap):
                md = run_mine(
                    self.home,
                    self.tmpdir,
                    "--since",
                    "24",
                    "--source",
                    "claude",
                    "--format",
                    "md",
                    "--max-snippets",
                    str(cap),
                )
                js = run_mine(
                    self.home,
                    self.tmpdir,
                    "--since",
                    "24",
                    "--source",
                    "claude",
                    "--format",
                    "json",
                    "--max-snippets",
                    str(cap),
                )
                payload = json.loads(js.stdout)
                md_count = count_md_snippets(md.stdout)
                json_count = count_json_snippets(payload)
                self.assertEqual(json_count, want, f"json cap={cap}")
                self.assertEqual(md_count, want, f"md cap={cap}\n{md.stdout}")
                self.assertEqual(md_count, json_count)
                if cap == 0:
                    self.assertNotIn("representative asks:", md.stdout)
                    self.assertTrue(all(len(p["snippets"]) == 0 for p in payload["projects"]))


if __name__ == "__main__":
    unittest.main()
