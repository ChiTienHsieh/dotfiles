#!/usr/bin/env python3
"""Private receipt registry for delegated Codex task return events.

This helper deliberately does not call Codex App APIs. Agents use the App's
thread tools for fresh reads, event waits, and wake-up messages; this file only
keeps the minimal durable state needed for idempotency and crash recovery.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


SCHEMA_VERSION = 1
EVENT_STATUSES = {"completed", "blocked", "needs-attention"}
ALL_STATUSES = EVENT_STATUSES | {"running"}
DELIVERY_STATES = {"pending", "sent"}
RECEIPT_STATES = {"none", "unacknowledged", "acknowledged"}
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@-]{0,255}$")
EVENT_ID_RE = re.compile(r"^dte1-[0-9a-f]{32}$")
MAX_CURSOR_LENGTH = 4096


class RegistryError(RuntimeError):
    """Raised when registry data or a requested transition is unsafe."""


def default_state_directory() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    root = Path(codex_home).expanduser() if codex_home else Path.home() / ".codex"
    return root / "state" / "task-delegations"


def ensure_identifier(label: str, value: str) -> str:
    if not IDENTIFIER_RE.fullmatch(value):
        raise RegistryError(f"invalid {label}: expected a bounded opaque identifier")
    return value


def ensure_cursor(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) > MAX_CURSOR_LENGTH or "\x00" in value:
        raise RegistryError("invalid cursor: expected at most 4096 characters")
    return value


def endpoint(host: str, thread: str) -> dict[str, str]:
    return {
        "host": ensure_identifier("host id", host),
        "thread": ensure_identifier("thread id", thread),
    }


def same_endpoint(left: dict[str, str], right: dict[str, str]) -> bool:
    return left["host"] == right["host"] and left["thread"] == right["thread"]


def qualified(value: dict[str, str]) -> str:
    return f'{value["host"]}/{value["thread"]}'


def delegation_key(source: dict[str, str], child: dict[str, str]) -> str:
    material = f'v1\0{qualified(source)}\0{qualified(child)}'.encode()
    return "dlg1-" + hashlib.sha256(material).hexdigest()[:32]


def event_id_for(
    source: dict[str, str],
    child: dict[str, str],
    status_value: str,
    sequence: int,
) -> str:
    material = (
        f'v1\0{qualified(source)}\0{qualified(child)}\0'
        f"{status_value}\0{sequence}"
    ).encode()
    return "dte1-" + hashlib.sha256(material).hexdigest()[:32]


def event_message(event: dict[str, object]) -> str:
    source = event["source"]
    child = event["child"]
    assert isinstance(source, dict) and isinstance(child, dict)
    return (
        "[CODEX_DELEGATION_EVENT "
        f'v=1 id={event["eventId"]} seq={event["sequence"]} '
        f'status={event["status"]} source={qualified(source)} '
        f"child={qualified(child)}]\n"
        "委派 task 狀態已變更；這只是一個喚醒訊號。先 fresh-read 指定 child，"
        "再處理並記錄 receipt；不要回送同一事件，也不要自動 archive/delete。"
    )


def ensure_private_directory(path: Path) -> Path:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    metadata = path.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or metadata.st_uid != os.getuid():
        raise RegistryError("delegation state directory is not owned by this user")
    if stat.S_IMODE(metadata.st_mode) != 0o700:
        path.chmod(0o700)
        metadata = path.lstat()
        if stat.S_IMODE(metadata.st_mode) != 0o700:
            raise RegistryError("delegation state directory is not mode 0700")
    return path


def validate_private_file(path: Path) -> os.stat_result:
    metadata = path.lstat()
    if (
        not stat.S_ISREG(metadata.st_mode)
        or metadata.st_uid != os.getuid()
        or stat.S_IMODE(metadata.st_mode) != 0o600
    ):
        raise RegistryError("delegation state file is not a private mode-0600 file")
    return metadata


def empty_state() -> dict[str, object]:
    return {"version": SCHEMA_VERSION, "delegations": {}, "outbox": {}}


def validate_state(state: object) -> dict[str, object]:
    if not isinstance(state, dict) or state.get("version") != SCHEMA_VERSION:
        raise RegistryError("unsupported or malformed delegation registry")
    delegations = state.get("delegations")
    outbox = state.get("outbox")
    if not isinstance(delegations, dict) or not isinstance(outbox, dict):
        raise RegistryError("malformed delegation registry collections")

    for key, record in delegations.items():
        if not isinstance(key, str) or not isinstance(record, dict):
            raise RegistryError("malformed delegation record")
        source = record.get("source")
        child = record.get("child")
        if not isinstance(source, dict) or not isinstance(child, dict):
            raise RegistryError("delegation record has invalid endpoints")
        checked_source = endpoint(str(source.get("host", "")), str(source.get("thread", "")))
        checked_child = endpoint(str(child.get("host", "")), str(child.get("thread", "")))
        if same_endpoint(checked_source, checked_child):
            raise RegistryError("delegation record targets itself")
        if key != delegation_key(checked_source, checked_child):
            raise RegistryError("delegation record key does not match its endpoints")
        if record.get("status") not in ALL_STATUSES:
            raise RegistryError("delegation record has invalid status")
        if record.get("receipt") not in RECEIPT_STATES:
            raise RegistryError("delegation record has invalid receipt state")
        sequence = record.get("sequence")
        accepted = record.get("lastAcceptedSequence")
        if not isinstance(sequence, int) or sequence < 0:
            raise RegistryError("delegation record has invalid sequence")
        if not isinstance(accepted, int) or accepted < 0 or accepted > sequence:
            raise RegistryError("delegation record has invalid accepted sequence")
        cursor = record.get("cursor")
        if cursor is not None and not isinstance(cursor, str):
            raise RegistryError("delegation record has invalid cursor")
        ensure_cursor(cursor)
        last_event = record.get("lastEventId")
        if last_event is not None and (
            not isinstance(last_event, str) or not EVENT_ID_RE.fullmatch(last_event)
        ):
            raise RegistryError("delegation record has invalid event id")

    for key, event in outbox.items():
        if not isinstance(key, str) or not EVENT_ID_RE.fullmatch(key):
            raise RegistryError("outbox has invalid event id")
        if not isinstance(event, dict) or event.get("eventId") != key:
            raise RegistryError("outbox has malformed event")
        if event.get("status") not in EVENT_STATUSES:
            raise RegistryError("outbox event has invalid status")
        if event.get("delivery") not in DELIVERY_STATES:
            raise RegistryError("outbox event has invalid delivery state")
        sequence = event.get("sequence")
        source = event.get("source")
        child = event.get("child")
        if not isinstance(sequence, int) or sequence < 1:
            raise RegistryError("outbox event has invalid sequence")
        if not isinstance(source, dict) or not isinstance(child, dict):
            raise RegistryError("outbox event has invalid endpoints")
        checked_source = endpoint(str(source.get("host", "")), str(source.get("thread", "")))
        checked_child = endpoint(str(child.get("host", "")), str(child.get("thread", "")))
        if key != event_id_for(checked_source, checked_child, str(event["status"]), sequence):
            raise RegistryError("outbox event id does not match its contents")
    return state


def load_state(path: Path) -> dict[str, object]:
    try:
        validate_private_file(path)
    except FileNotFoundError:
        return empty_state()
    try:
        return validate_state(json.loads(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError as exc:
        raise RegistryError("delegation registry is not valid JSON") from exc


def write_state_atomic(path: Path, state: dict[str, object]) -> None:
    validate_state(state)
    directory = ensure_private_directory(path.parent)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".registry.", dir=directory)
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = -1
            json.dump(state, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
        directory_descriptor = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)
        raise


class Registry:
    def __init__(self, state_directory: Path | None = None) -> None:
        self.directory = state_directory or default_state_directory()
        self.path = self.directory / "registry.json"
        self.lock_path = self.directory / "registry.lock"

    @contextmanager
    def locked_state(self, *, write: bool) -> Iterator[dict[str, object]]:
        ensure_private_directory(self.directory)
        flags = os.O_RDWR | os.O_CREAT
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(self.lock_path, flags, 0o600)
        try:
            os.fchmod(descriptor, 0o600)
            validate_private_file(self.lock_path)
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            state = load_state(self.path)
            yield state
            if write:
                write_state_atomic(self.path, state)
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    @staticmethod
    def _record_for(
        state: dict[str, object], source: dict[str, str], child: dict[str, str]
    ) -> tuple[str, dict[str, object] | None]:
        key = delegation_key(source, child)
        delegations = state["delegations"]
        assert isinstance(delegations, dict)
        record = delegations.get(key)
        return key, record if isinstance(record, dict) else None

    @staticmethod
    def _new_record(source: dict[str, str], child: dict[str, str]) -> dict[str, object]:
        return {
            "source": source,
            "child": child,
            "status": "running",
            "cursor": None,
            "sequence": 0,
            "lastAcceptedSequence": 0,
            "lastEventId": None,
            "receipt": "none",
        }

    @staticmethod
    def _reject_conflicting_child(
        state: dict[str, object], source: dict[str, str], child: dict[str, str]
    ) -> None:
        delegations = state["delegations"]
        assert isinstance(delegations, dict)
        for record in delegations.values():
            if not isinstance(record, dict):
                continue
            existing_child = record.get("child")
            existing_source = record.get("source")
            if (
                isinstance(existing_child, dict)
                and isinstance(existing_source, dict)
                and same_endpoint(existing_child, child)
                and not same_endpoint(existing_source, source)
            ):
                raise RegistryError("child task is already bound to a different source")

    def register(
        self, source: dict[str, str], child: dict[str, str]
    ) -> dict[str, object]:
        if same_endpoint(source, child):
            raise RegistryError("source and child tasks must be different")
        with self.locked_state(write=True) as state:
            self._reject_conflicting_child(state, source, child)
            key, record = self._record_for(state, source, child)
            created = record is None
            if created:
                record = self._new_record(source, child)
                delegations = state["delegations"]
                assert isinstance(delegations, dict)
                delegations[key] = record
            assert record is not None
            return {"created": created, "delegationId": key, "record": dict(record)}

    def prepare(
        self,
        source: dict[str, str],
        child: dict[str, str],
        status_value: str,
    ) -> dict[str, object]:
        if status_value not in EVENT_STATUSES:
            raise RegistryError("invalid delegated-task event status")
        if same_endpoint(source, child):
            raise RegistryError("a task cannot notify itself")
        with self.locked_state(write=True) as state:
            self._reject_conflicting_child(state, source, child)
            key, record = self._record_for(state, source, child)
            if record is None:
                record = self._new_record(source, child)
                delegations = state["delegations"]
                assert isinstance(delegations, dict)
                delegations[key] = record

            last_event_id = record.get("lastEventId")
            if record.get("status") == status_value and isinstance(last_event_id, str):
                outbox = state["outbox"]
                assert isinstance(outbox, dict)
                existing = outbox.get(last_event_id)
                if not isinstance(existing, dict):
                    raise RegistryError("delegation event is missing from the local outbox")
                result = dict(existing)
                result["duplicate"] = True
                result["message"] = event_message(existing)
                return result

            if record.get("status") == "completed":
                raise RegistryError("completed delegation must be resumed before a new event")

            sequence = int(record["sequence"]) + 1
            new_event_id = event_id_for(source, child, status_value, sequence)
            event: dict[str, object] = {
                "eventId": new_event_id,
                "sequence": sequence,
                "source": source,
                "child": child,
                "status": status_value,
                "delivery": "pending",
            }
            outbox = state["outbox"]
            assert isinstance(outbox, dict)
            outbox[new_event_id] = event
            record.update(
                {
                    "status": status_value,
                    "sequence": sequence,
                    "lastEventId": new_event_id,
                    "receipt": "unacknowledged",
                }
            )
            result = dict(event)
            result["duplicate"] = False
            result["message"] = event_message(event)
            return result

    def mark_sent(
        self, event_id: str, *, actor_thread: str | None = None
    ) -> dict[str, object]:
        if not EVENT_ID_RE.fullmatch(event_id):
            raise RegistryError("invalid delegation event id")
        with self.locked_state(write=True) as state:
            outbox = state["outbox"]
            assert isinstance(outbox, dict)
            event = outbox.get(event_id)
            if not isinstance(event, dict):
                raise RegistryError("delegation event is not present in this host's outbox")
            child = event.get("child")
            if (
                actor_thread is not None
                and isinstance(child, dict)
                and child.get("thread") != actor_thread
            ):
                raise RegistryError("current task does not own this outbox event")
            duplicate = event.get("delivery") == "sent"
            event["delivery"] = "sent"
            return {"eventId": event_id, "duplicate": duplicate, "delivery": "sent"}

    def accept(
        self,
        source: dict[str, str],
        child: dict[str, str],
        status_value: str,
        sequence: int,
        event_id: str,
    ) -> dict[str, object]:
        if status_value not in EVENT_STATUSES or sequence < 1:
            raise RegistryError("invalid delegated-task event")
        expected = event_id_for(source, child, status_value, sequence)
        if event_id != expected:
            raise RegistryError("delegation event does not match its endpoints and sequence")
        with self.locked_state(write=True) as state:
            _, record = self._record_for(state, source, child)
            if record is None:
                raise RegistryError("source has no registered delegation for this child")
            accepted_sequence = int(record["lastAcceptedSequence"])
            if sequence <= accepted_sequence:
                duplicate = sequence == accepted_sequence and record.get("lastEventId") == event_id
                return {
                    "accepted": False,
                    "duplicate": duplicate,
                    "stale": not duplicate,
                    "eventId": event_id,
                }
            record.update(
                {
                    "status": status_value,
                    "sequence": max(int(record["sequence"]), sequence),
                    "lastAcceptedSequence": sequence,
                    "lastEventId": event_id,
                    "receipt": "acknowledged",
                }
            )
            outbox = state["outbox"]
            assert isinstance(outbox, dict)
            local_event = outbox.get(event_id)
            if isinstance(local_event, dict):
                local_event["delivery"] = "sent"
            return {
                "accepted": True,
                "duplicate": False,
                "stale": False,
                "eventId": event_id,
            }

    def observe(
        self,
        source: dict[str, str],
        child: dict[str, str],
        status_value: str,
    ) -> dict[str, object]:
        """Record a source-side wait/read result when no callback arrived."""
        if status_value not in EVENT_STATUSES:
            raise RegistryError("invalid observed delegated-task status")
        with self.locked_state(write=True) as state:
            _, record = self._record_for(state, source, child)
            if record is None:
                raise RegistryError("delegation is not registered")
            if record.get("status") == status_value:
                event_id = record.get("lastEventId")
                if record.get("receipt") == "acknowledged":
                    return {
                        "accepted": False,
                        "duplicate": True,
                        "eventId": event_id,
                    }
                if isinstance(event_id, str):
                    sequence = int(record["sequence"])
                else:
                    sequence = int(record["sequence"]) + 1
                    event_id = event_id_for(source, child, status_value, sequence)
            else:
                sequence = int(record["sequence"]) + 1
                event_id = event_id_for(source, child, status_value, sequence)
            record.update(
                {
                    "status": status_value,
                    "sequence": sequence,
                    "lastAcceptedSequence": sequence,
                    "lastEventId": event_id,
                    "receipt": "acknowledged",
                }
            )
            outbox = state["outbox"]
            assert isinstance(outbox, dict)
            local_event = outbox.get(event_id)
            if isinstance(local_event, dict):
                local_event["delivery"] = "sent"
            return {"accepted": True, "duplicate": False, "eventId": event_id}

    def resume(self, source: dict[str, str], child: dict[str, str]) -> dict[str, object]:
        with self.locked_state(write=True) as state:
            _, record = self._record_for(state, source, child)
            if record is None:
                raise RegistryError("delegation is not registered")
            duplicate = record.get("status") == "running"
            record["status"] = "running"
            return {"resumed": not duplicate, "duplicate": duplicate, "record": dict(record)}

    def set_cursor(
        self, source: dict[str, str], child: dict[str, str], cursor: str | None
    ) -> dict[str, object]:
        checked_cursor = ensure_cursor(cursor)
        with self.locked_state(write=True) as state:
            _, record = self._record_for(state, source, child)
            if record is None:
                raise RegistryError("delegation is not registered")
            record["cursor"] = checked_cursor
            return {"cursor": checked_cursor, "child": child}

    def recover_source(self, source: dict[str, str]) -> dict[str, object]:
        with self.locked_state(write=False) as state:
            delegations = state["delegations"]
            assert isinstance(delegations, dict)
            records = [
                dict(record)
                for record in delegations.values()
                if isinstance(record, dict)
                and isinstance(record.get("source"), dict)
                and same_endpoint(record["source"], source)
            ]
            records.sort(key=lambda record: qualified(record["child"]))
            wait_targets: list[dict[str, str]] = []
            needs_handling: list[dict[str, object]] = []
            for record in records:
                if record["status"] == "running" or record["receipt"] == "unacknowledged":
                    child = record["child"]
                    assert isinstance(child, dict)
                    target = {"threadId": child["thread"], "hostId": child["host"]}
                    if isinstance(record.get("cursor"), str):
                        target["afterCursor"] = record["cursor"]
                    wait_targets.append(target)
                if record["receipt"] == "unacknowledged":
                    needs_handling.append(record)
            return {
                "source": source,
                "delegations": records,
                "waitTargets": wait_targets,
                "needsHandling": needs_handling,
            }

    def recover_child(self, child: dict[str, str]) -> dict[str, object]:
        with self.locked_state(write=False) as state:
            outbox = state["outbox"]
            assert isinstance(outbox, dict)
            events = [
                dict(event)
                for event in outbox.values()
                if isinstance(event, dict)
                and isinstance(event.get("child"), dict)
                and same_endpoint(event["child"], child)
            ]
            events.sort(key=lambda event: int(event["sequence"]))
            for event in events:
                event["message"] = event_message(event)
            return {"child": child, "events": events}


def current_thread_id() -> str | None:
    value = os.environ.get("CODEX_THREAD_ID")
    return ensure_identifier("CODEX_THREAD_ID", value) if value else None


def require_current(endpoint_value: dict[str, str], role: str) -> None:
    current = current_thread_id()
    if current is not None and endpoint_value["thread"] != current:
        raise RegistryError(f"current task does not match the declared {role} thread")


def add_source(parser: argparse.ArgumentParser, *, current: bool) -> None:
    parser.add_argument("--source-host", required=True)
    parser.add_argument("--source-thread", required=not current)


def add_child(parser: argparse.ArgumentParser, *, current: bool) -> None:
    parser.add_argument("--child-host", required=True)
    parser.add_argument("--child-thread", required=not current)


def endpoint_from_args(args: argparse.Namespace, name: str, *, current: bool) -> dict[str, str]:
    thread_value = getattr(args, f"{name}_thread", None)
    if current and not thread_value:
        thread_value = current_thread_id()
    if not thread_value:
        raise RegistryError(f"missing {name} thread id and CODEX_THREAD_ID is unavailable")
    return endpoint(getattr(args, f"{name}_host"), thread_value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, help="override private registry directory")
    commands = parser.add_subparsers(dest="command", required=True)

    register_parser = commands.add_parser("register")
    add_source(register_parser, current=True)
    add_child(register_parser, current=False)

    prepare_parser = commands.add_parser("prepare")
    add_source(prepare_parser, current=False)
    add_child(prepare_parser, current=True)
    prepare_parser.add_argument("--status", choices=sorted(EVENT_STATUSES), required=True)

    sent_parser = commands.add_parser("mark-sent")
    sent_parser.add_argument("--event-id", required=True)

    accept_parser = commands.add_parser("accept")
    add_source(accept_parser, current=True)
    add_child(accept_parser, current=False)
    accept_parser.add_argument("--status", choices=sorted(EVENT_STATUSES), required=True)
    accept_parser.add_argument("--sequence", type=int, required=True)
    accept_parser.add_argument("--event-id", required=True)

    observe_parser = commands.add_parser("observe")
    add_source(observe_parser, current=True)
    add_child(observe_parser, current=False)
    observe_parser.add_argument("--status", choices=sorted(EVENT_STATUSES), required=True)

    resume_parser = commands.add_parser("resume")
    add_source(resume_parser, current=False)
    add_child(resume_parser, current=False)
    resume_parser.add_argument("--as-role", choices=("source", "child"), required=True)

    cursor_parser = commands.add_parser("set-cursor")
    add_source(cursor_parser, current=True)
    add_child(cursor_parser, current=False)
    cursor_parser.add_argument("--cursor")

    recover_source_parser = commands.add_parser("recover-source")
    add_source(recover_source_parser, current=True)

    recover_child_parser = commands.add_parser("recover-child")
    add_child(recover_child_parser, current=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    registry = Registry(args.state_dir)
    try:
        if args.command == "register":
            source = endpoint_from_args(args, "source", current=True)
            child = endpoint_from_args(args, "child", current=False)
            require_current(source, "source")
            result = registry.register(source, child)
        elif args.command == "prepare":
            source = endpoint_from_args(args, "source", current=False)
            child = endpoint_from_args(args, "child", current=True)
            require_current(child, "child")
            result = registry.prepare(source, child, args.status)
        elif args.command == "mark-sent":
            result = registry.mark_sent(args.event_id, actor_thread=current_thread_id())
        elif args.command == "accept":
            source = endpoint_from_args(args, "source", current=True)
            child = endpoint_from_args(args, "child", current=False)
            require_current(source, "source")
            result = registry.accept(
                source, child, args.status, args.sequence, args.event_id
            )
        elif args.command == "observe":
            source = endpoint_from_args(args, "source", current=True)
            child = endpoint_from_args(args, "child", current=False)
            require_current(source, "source")
            result = registry.observe(source, child, args.status)
        elif args.command == "resume":
            source = endpoint_from_args(args, "source", current=False)
            child = endpoint_from_args(args, "child", current=False)
            require_current(source if args.as_role == "source" else child, args.as_role)
            result = registry.resume(source, child)
        elif args.command == "set-cursor":
            source = endpoint_from_args(args, "source", current=True)
            child = endpoint_from_args(args, "child", current=False)
            require_current(source, "source")
            result = registry.set_cursor(source, child, args.cursor)
        elif args.command == "recover-source":
            source = endpoint_from_args(args, "source", current=True)
            require_current(source, "source")
            result = registry.recover_source(source)
        elif args.command == "recover-child":
            child = endpoint_from_args(args, "child", current=True)
            require_current(child, "child")
            result = registry.recover_child(child)
        else:  # pragma: no cover - argparse enforces the choices.
            raise RegistryError("unsupported command")
    except (OSError, RegistryError) as exc:
        print(f"task_delegation_registry.py: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
