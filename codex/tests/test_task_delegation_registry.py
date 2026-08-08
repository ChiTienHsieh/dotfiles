#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path


CODEX_DIR = Path(__file__).resolve().parents[1]
REGISTRY_PATH = CODEX_DIR / "bin" / "task_delegation_registry.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


registry_module = load_module("task_delegation_registry", REGISTRY_PATH)


class FakeThreadTools:
    """Small contract fixture for the installed App thread-tool semantics."""

    def __init__(self) -> None:
        self.threads: dict[tuple[str, str], dict[str, object]] = {}
        self.operation = 0
        self.last_read: tuple[tuple[str, str], int] | None = None

    def add(self, value: dict[str, str], *, status_value: str = "running") -> None:
        self.threads[(value["host"], value["thread"])] = {
            "status": status_value,
            "available": True,
            "messages": [],
            "wakeCount": 0,
            "cursor": "cursor-0",
        }

    def set_status(self, value: dict[str, str], status_value: str, cursor: str) -> None:
        thread = self.threads[(value["host"], value["thread"])]
        thread["status"] = status_value
        thread["cursor"] = cursor

    def set_available(self, value: dict[str, str], available: bool) -> None:
        self.threads[(value["host"], value["thread"])]["available"] = available

    def read_thread(self, value: dict[str, str]) -> dict[str, object]:
        self.operation += 1
        key = (value["host"], value["thread"])
        thread = self.threads[key]
        if not thread["available"]:
            self.last_read = None
            raise RuntimeError("source unavailable")
        self.last_read = (key, self.operation)
        return dict(thread)

    def send_message_to_thread(self, value: dict[str, str], message: str) -> None:
        self.operation += 1
        key = (value["host"], value["thread"])
        if self.last_read != (key, self.operation - 1):
            raise AssertionError("send was not immediately preceded by a fresh recipient read")
        thread = self.threads[key]
        if not thread["available"]:
            raise RuntimeError("recipient became unavailable")
        messages = thread["messages"]
        assert isinstance(messages, list)
        messages.append(message)
        thread["wakeCount"] = int(thread["wakeCount"]) + 1
        self.last_read = None

    def wait_threads(self, targets: list[dict[str, str]]) -> dict[str, object]:
        for target in targets:
            key = (target["hostId"], target["threadId"])
            thread = self.threads[key]
            if thread["status"] != "running":
                return {
                    "threadId": target["threadId"],
                    "hostId": target["hostId"],
                    "status": thread["status"],
                    "cursor": thread["cursor"],
                }
        return {"status": "timeout"}


class DelegationRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.state_directory = Path(self.tempdir.name) / "private-state"
        self.registry = registry_module.Registry(self.state_directory)
        self.source = registry_module.endpoint("local", "source-1")
        self.child = registry_module.endpoint("local", "child-1")

    def dispatch_event(
        self,
        tools: FakeThreadTools,
        event: dict[str, object],
    ) -> None:
        if event["delivery"] == "sent":
            return
        tools.read_thread(self.source)
        tools.send_message_to_thread(self.source, str(event["message"]))
        self.registry.mark_sent(str(event["eventId"]))

    def accept_after_fresh_child_read(
        self,
        tools: FakeThreadTools,
        event: dict[str, object],
    ) -> dict[str, object]:
        tools.read_thread(self.child)
        return self.registry.accept(
            self.source,
            self.child,
            str(event["status"]),
            int(event["sequence"]),
            str(event["eventId"]),
        )

    def test_completion_callback_really_wakes_source(self) -> None:
        tools = FakeThreadTools()
        tools.add(self.source)
        tools.add(self.child, status_value="completed")
        self.registry.register(self.source, self.child)

        event = self.registry.prepare(self.source, self.child, "completed")
        self.dispatch_event(tools, event)
        accepted = self.accept_after_fresh_child_read(tools, event)

        source_state = tools.read_thread(self.source)
        self.assertEqual(source_state["wakeCount"], 1)
        self.assertEqual(len(source_state["messages"]), 1)
        self.assertTrue(accepted["accepted"])
        recovered = self.registry.recover_source(self.source)
        self.assertEqual(recovered["waitTargets"], [])
        self.assertEqual(recovered["delegations"][0]["status"], "completed")

    def test_blocked_and_needs_attention_callbacks_wake_source(self) -> None:
        for index, status_value in enumerate(("blocked", "needs-attention"), start=1):
            with self.subTest(status=status_value):
                source = registry_module.endpoint("local", f"source-{index + 10}")
                child = registry_module.endpoint("local", f"child-{index + 10}")
                state = Path(self.tempdir.name) / f"state-{index}"
                registry = registry_module.Registry(state)
                tools = FakeThreadTools()
                tools.add(source)
                tools.add(child, status_value=status_value)
                registry.register(source, child)
                event = registry.prepare(source, child, status_value)

                tools.read_thread(source)
                tools.send_message_to_thread(source, str(event["message"]))
                registry.mark_sent(str(event["eventId"]))
                tools.read_thread(child)
                accepted = registry.accept(
                    source,
                    child,
                    status_value,
                    int(event["sequence"]),
                    str(event["eventId"]),
                )

                self.assertTrue(accepted["accepted"])
                self.assertEqual(tools.read_thread(source)["wakeCount"], 1)

    def test_duplicate_prepare_and_accept_are_idempotent(self) -> None:
        tools = FakeThreadTools()
        tools.add(self.source)
        tools.add(self.child, status_value="completed")
        self.registry.register(self.source, self.child)
        first = self.registry.prepare(self.source, self.child, "completed")
        self.dispatch_event(tools, first)

        duplicate = self.registry.prepare(self.source, self.child, "completed")
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(duplicate["eventId"], first["eventId"])
        self.assertEqual(duplicate["delivery"], "sent")
        self.dispatch_event(tools, duplicate)
        self.assertEqual(tools.read_thread(self.source)["wakeCount"], 1)

        first_accept = self.accept_after_fresh_child_read(tools, first)
        second_accept = self.accept_after_fresh_child_read(tools, first)
        self.assertTrue(first_accept["accepted"])
        self.assertFalse(second_accept["accepted"])
        self.assertTrue(second_accept["duplicate"])

    def test_wait_result_settles_same_host_outbox_before_callback(self) -> None:
        self.registry.register(self.source, self.child)
        event = self.registry.prepare(self.source, self.child, "completed")

        observed = self.registry.observe(self.source, self.child, "completed")
        duplicate = self.registry.prepare(self.source, self.child, "completed")

        self.assertTrue(observed["accepted"])
        self.assertEqual(observed["eventId"], event["eventId"])
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(duplicate["delivery"], "sent")

    def test_source_unavailable_leaves_private_pending_outbox(self) -> None:
        tools = FakeThreadTools()
        tools.add(self.source)
        tools.add(self.child, status_value="blocked")
        tools.set_available(self.source, False)
        self.registry.register(self.source, self.child)
        event = self.registry.prepare(self.source, self.child, "blocked")

        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            tools.read_thread(self.source)

        restarted = registry_module.Registry(self.state_directory)
        outbox = restarted.recover_child(self.child)["events"]
        self.assertEqual(len(outbox), 1)
        self.assertEqual(outbox[0]["eventId"], event["eventId"])
        self.assertEqual(outbox[0]["delivery"], "pending")
        self.assertEqual(tools.threads[("local", "source-1")]["wakeCount"], 0)

    def test_restart_recovery_uses_wait_cursor_and_fresh_child_read(self) -> None:
        tools = FakeThreadTools()
        tools.add(self.source)
        tools.add(self.child)
        self.registry.register(self.source, self.child)
        self.registry.set_cursor(self.source, self.child, "cursor-before-crash")
        tools.set_status(self.child, "completed", "cursor-after-restart")

        restarted = registry_module.Registry(self.state_directory)
        recovery = restarted.recover_source(self.source)
        self.assertEqual(
            recovery["waitTargets"],
            [
                {
                    "threadId": "child-1",
                    "hostId": "local",
                    "afterCursor": "cursor-before-crash",
                }
            ],
        )
        result = tools.wait_threads(recovery["waitTargets"])
        restarted.set_cursor(self.source, self.child, str(result["cursor"]))
        tools.read_thread(self.child)
        observed = restarted.observe(self.source, self.child, str(result["status"]))

        self.assertTrue(observed["accepted"])
        after = restarted.recover_source(self.source)
        self.assertEqual(after["waitTargets"], [])
        self.assertEqual(after["delegations"][0]["cursor"], "cursor-after-restart")

    def test_multiple_children_recover_as_qualified_wait_targets(self) -> None:
        remote = registry_module.endpoint("remote-ssh-discovered:clawd-vm", "child-remote")
        other = registry_module.endpoint("local", "child-2")
        self.registry.register(self.source, self.child)
        self.registry.register(self.source, remote)
        self.registry.register(self.source, other)
        self.registry.set_cursor(self.source, remote, "remote-cursor")

        targets = self.registry.recover_source(self.source)["waitTargets"]
        self.assertEqual(len(targets), 3)
        self.assertIn(
            {
                "threadId": "child-remote",
                "hostId": "remote-ssh-discovered:clawd-vm",
                "afterCursor": "remote-cursor",
            },
            targets,
        )

    def test_rejects_self_notification_and_conflicting_source(self) -> None:
        with self.assertRaisesRegex(registry_module.RegistryError, "different"):
            self.registry.register(self.source, self.source)
        self.registry.register(self.source, self.child)
        other_source = registry_module.endpoint("local", "source-other")
        with self.assertRaisesRegex(registry_module.RegistryError, "different source"):
            self.registry.register(other_source, self.child)

    def test_rejects_wrong_event_binding_and_stale_delivery(self) -> None:
        self.registry.register(self.source, self.child)
        first = self.registry.prepare(self.source, self.child, "needs-attention")
        self.registry.accept(
            self.source,
            self.child,
            "needs-attention",
            int(first["sequence"]),
            str(first["eventId"]),
        )
        self.registry.resume(self.source, self.child)
        second = self.registry.prepare(self.source, self.child, "completed")
        self.registry.accept(
            self.source,
            self.child,
            "completed",
            int(second["sequence"]),
            str(second["eventId"]),
        )

        stale = self.registry.accept(
            self.source,
            self.child,
            "needs-attention",
            int(first["sequence"]),
            str(first["eventId"]),
        )
        self.assertTrue(stale["stale"])
        wrong_child = registry_module.endpoint("local", "child-wrong")
        with self.assertRaisesRegex(registry_module.RegistryError, "does not match"):
            self.registry.accept(
                self.source,
                wrong_child,
                "completed",
                int(second["sequence"]),
                str(second["eventId"]),
            )

    def test_registry_is_private_atomic_and_stores_only_minimal_metadata(self) -> None:
        self.registry.register(self.source, self.child)
        event = self.registry.prepare(self.source, self.child, "completed")
        state_path = self.state_directory / "registry.json"
        lock_path = self.state_directory / "registry.lock"

        self.assertEqual(stat.S_IMODE(self.state_directory.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(state_path.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(lock_path.stat().st_mode), 0o600)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        serialized = json.dumps(state)
        for forbidden in ("prompt", "final answer", "browser", "token", "personal"):
            self.assertNotIn(forbidden, serialized.lower())
        self.assertIn(str(event["eventId"]), serialized)

    def test_rejects_symlinked_or_public_state_files(self) -> None:
        self.state_directory.mkdir(mode=0o700)
        target = Path(self.tempdir.name) / "target.json"
        target.write_text("{}\n", encoding="utf-8")
        (self.state_directory / "registry.json").symlink_to(target)
        with self.assertRaisesRegex(registry_module.RegistryError, "mode-0600"):
            self.registry.recover_source(self.source)

        (self.state_directory / "registry.json").unlink()
        (self.state_directory / "registry.json").write_text(
            json.dumps(registry_module.empty_state()), encoding="utf-8"
        )
        (self.state_directory / "registry.json").chmod(0o644)
        with self.assertRaisesRegex(registry_module.RegistryError, "mode-0600"):
            self.registry.recover_source(self.source)

    def test_cli_refuses_declared_current_task_mismatch(self) -> None:
        old = os.environ.get("CODEX_THREAD_ID")
        os.environ["CODEX_THREAD_ID"] = "actual-source"
        try:
            with self.assertRaisesRegex(registry_module.RegistryError, "declared source"):
                registry_module.require_current(self.source, "source")
        finally:
            if old is None:
                os.environ.pop("CODEX_THREAD_ID", None)
            else:
                os.environ["CODEX_THREAD_ID"] = old


class DelegationWorkflowWiringTests(unittest.TestCase):
    def test_coordination_helper_is_not_installed_as_a_hook(self) -> None:
        manifest = (CODEX_DIR / "hooks.json").read_text(encoding="utf-8")
        self.assertNotIn("task_delegation_registry", manifest)
        self.assertNotIn("SessionEnd", manifest)

    def test_skill_and_global_rule_require_both_return_paths(self) -> None:
        skill = (
            CODEX_DIR.parent
            / "skills"
            / "codex"
            / "codex-task-return"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        agents = (CODEX_DIR / "AGENTS.md").read_text(encoding="utf-8")
        for marker in (
            "wait_threads",
            "read_thread",
            "send_message_to_thread",
            "completed",
            "blocked",
            "needs-attention",
            "recover-source",
            "recover-child",
        ):
            self.assertIn(marker, skill)
        self.assertIn("codex-task-return", agents)
        self.assertIn("只改 sidebar 狀態不算 return", agents)


if __name__ == "__main__":
    unittest.main()
