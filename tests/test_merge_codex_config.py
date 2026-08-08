from __future__ import annotations

import stat
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import merge_codex_config  # noqa: E402


PORTABLE = """\
[agents]
enabled = true
max_concurrent_threads_per_session = 100
default_subagent_model = "gpt-5.6-luna"
default_subagent_reasoning_effort = "max"
"""

BEFORE = '''\
personality = "pragmatic"

[agents]
notes = """
enabled = false
[projects]
"""

[projects."/tmp/runtime-project"]
trust_level = "trusted"
'''

AFTER = '''\
personality = "pragmatic"

[agents]
notes = """
enabled = false
[projects]
"""
enabled = true
max_concurrent_threads_per_session = 100
default_subagent_model = "gpt-5.6-luna"
default_subagent_reasoning_effort = "max"

[projects."/tmp/runtime-project"]
trust_level = "trusted"
'''

MANAGED_VALUES = {
    "enabled": True,
    "max_concurrent_threads_per_session": 100,
    "default_subagent_model": "gpt-5.6-luna",
    "default_subagent_reasoning_effort": "max",
}


class FakeClient:
    def __init__(
        self,
        destination: Path,
        user_config: dict[str, object],
        *,
        after_write: str = AFTER,
        write_error: Exception | None = None,
    ) -> None:
        self.destination = destination
        self.user_config = user_config
        self.after_write = after_write
        self.write_error = write_error
        self.requests: list[tuple[str, dict[str, object]]] = []

    def __enter__(self) -> FakeClient:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def request(self, method: str, params: dict[str, object]) -> object:
        self.requests.append((method, params))
        if method == "config/read":
            return {
                "layers": [
                    {
                        "name": {"type": "system", "file": "/etc/codex/config.toml"},
                        "version": "system-v1",
                        "config": {},
                    },
                    {
                        "name": {
                            "type": "user",
                            "file": str(self.destination),
                            "profile": None,
                        },
                        "version": "user-v1",
                        "config": self.user_config,
                    },
                ]
            }
        if method == "config/batchWrite":
            if self.write_error is not None:
                raise self.write_error
            self.destination.write_text(self.after_write, encoding="utf-8")
            return {
                "filePath": str(self.destination),
                "status": "ok",
                "version": "user-v2",
            }
        raise AssertionError(f"unexpected method: {method}")


class MergeCodexConfigTests(unittest.TestCase):
    def make_files(self, root: Path) -> tuple[Path, Path]:
        portable = root / "portable.toml"
        destination = root / "config.toml"
        portable.write_text(PORTABLE, encoding="utf-8")
        destination.write_text(BEFORE, encoding="utf-8")
        return portable, destination

    def test_uses_atomic_batch_write_with_concurrency_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            portable, destination = self.make_files(Path(temporary_directory))
            client = FakeClient(
                destination,
                {"personality": "pragmatic", "agents": {"notes": "runtime"}},
            )

            changed = merge_codex_config.merge_portable_config(
                portable, destination, client_factory=lambda: client
            )

            self.assertTrue(changed)
            method, params = client.requests[-1]
            self.assertEqual(method, "config/batchWrite")
            self.assertEqual(params["expectedVersion"], "user-v1")
            self.assertEqual(params["filePath"], str(destination.resolve()))
            self.assertEqual(params["reloadUserConfig"], False)
            edits = {edit["keyPath"]: edit for edit in params["edits"]}
            self.assertEqual(set(edits), {f"agents.{key}" for key in MANAGED_VALUES})
            self.assertTrue(
                all(edit["mergeStrategy"] == "upsert" for edit in edits.values())
            )
            self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)

    def test_rpc_receiver_keeps_read_ahead_response_with_notification(self) -> None:
        child = (
            "import json, sys, time\n"
            "messages = ["
            "{'id': 0, 'result': {}}, "
            "{'method': 'notice', 'params': {}}, "
            "{'id': 1, 'result': {'ok': True}}]\n"
            "payload = ''.join(json.dumps(item) + '\\n' for item in messages)\n"
            "sys.stdout.write(payload)\n"
            "sys.stdout.flush()\n"
            "time.sleep(30)\n"
        )

        with merge_codex_config.AppServer(
            (sys.executable, "-u", "-c", child)
        ) as client:
            result = client.request("probe", {})

        self.assertEqual(result, {"ok": True})

    def test_noop_preserves_multiline_runtime_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            portable, destination = self.make_files(Path(temporary_directory))
            destination.write_text(AFTER, encoding="utf-8")
            before = destination.read_bytes()
            client = FakeClient(
                destination,
                {
                    "personality": "pragmatic",
                    "agents": {"notes": "runtime", **MANAGED_VALUES},
                },
            )

            changed = merge_codex_config.merge_portable_config(
                portable, destination, client_factory=lambda: client
            )

            self.assertFalse(changed)
            self.assertEqual(destination.read_bytes(), before)
            self.assertEqual(
                [method for method, _params in client.requests], ["config/read"]
            )

    def test_version_conflict_leaves_destination_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            portable, destination = self.make_files(Path(temporary_directory))
            before = destination.read_bytes()
            client = FakeClient(
                destination,
                {"agents": {}},
                write_error=merge_codex_config.AppServerError("version mismatch"),
            )

            with self.assertRaisesRegex(
                merge_codex_config.AppServerError, "version mismatch"
            ):
                merge_codex_config.merge_portable_config(
                    portable, destination, client_factory=lambda: client
                )

            self.assertEqual(destination.read_bytes(), before)
            self.assertEqual(client.requests[-1][1]["expectedVersion"], "user-v1")

    def test_refuses_symlink_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            portable = root / "portable.toml"
            target = root / "target.toml"
            destination = root / "config.toml"
            portable.write_text(PORTABLE, encoding="utf-8")
            target.write_text(BEFORE, encoding="utf-8")
            destination.symlink_to(target)

            with self.assertRaisesRegex(RuntimeError, "not a regular file"):
                merge_codex_config.merge_portable_config(portable, destination)

            self.assertEqual(target.read_text(), BEFORE)

    def test_rejects_key_paths_the_rpc_cannot_represent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            portable = root / "portable.toml"
            destination = root / "config.toml"
            portable.write_text(
                '["agents.with.dot"]\nenabled = true\n', encoding="utf-8"
            )
            destination.write_text(BEFORE, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "cannot be represented"):
                merge_codex_config.merge_portable_config(portable, destination)


if __name__ == "__main__":
    unittest.main()
