#!/usr/bin/env python3
"""Sync portable settings through Codex's atomic config RPC."""

from __future__ import annotations

import argparse
import json
import os
import re
import select
import stat
import subprocess
import sys
import time
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any


KEY_COMPONENT = re.compile(r"^[A-Za-z0-9_-]+$")
MISSING = object()


class AppServerError(RuntimeError):
    """Raised when the Codex app-server cannot complete a config request."""


class AppServer:
    def __init__(self, command: tuple[str, ...] = ("codex", "app-server", "--stdio")):
        self.command = command
        self.process: subprocess.Popen[bytes] | None = None
        self.next_id = 1
        self.stdout_buffer = bytearray()

    def __enter__(self) -> AppServer:
        try:
            self.process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                bufsize=0,
            )
        except FileNotFoundError as exc:
            raise AppServerError("Codex CLI is not installed or not on PATH") from exc

        try:
            self._send(
                {
                    "method": "initialize",
                    "id": 0,
                    "params": {
                        "clientInfo": {
                            "name": "dotfiles_config_sync",
                            "title": "Dotfiles config sync",
                            "version": "1.0.0",
                        }
                    },
                }
            )
            self._receive(0, "initialize")
            self._send({"method": "initialized", "params": {}})
        except BaseException:
            self.__exit__()
            raise
        return self

    def __exit__(self, *_args: object) -> None:
        if self.process is None:
            return
        if self.process.stdin is not None:
            try:
                self.process.stdin.close()
            except BrokenPipeError:
                pass
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if self.process.stdout is not None:
            self.process.stdout.close()

    def _send(self, message: dict[str, object]) -> None:
        if self.process is None or self.process.stdin is None:
            raise AppServerError("Codex app-server is not running")
        payload = json.dumps(message, separators=(",", ":")).encode() + b"\n"
        self.process.stdin.write(payload)
        self.process.stdin.flush()

    def _receive(self, response_id: int, method: str) -> object:
        if self.process is None or self.process.stdout is None:
            raise AppServerError("Codex app-server is not running")

        deadline = time.monotonic() + 20
        while True:
            newline = self.stdout_buffer.find(b"\n")
            if newline >= 0:
                raw_line = bytes(self.stdout_buffer[:newline])
                del self.stdout_buffer[: newline + 1]
                try:
                    message = json.loads(raw_line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise AppServerError(
                        "Codex app-server returned invalid JSON"
                    ) from exc
                if message.get("id") != response_id:
                    continue
                if "error" in message:
                    error = message["error"]
                    if isinstance(error, dict):
                        code = error.get("code", "unknown")
                        text = error.get("message", "unknown error")
                        raise AppServerError(f"{method} failed ({code}): {text}")
                    raise AppServerError(f"{method} failed")
                return message.get("result")

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise AppServerError(f"Codex app-server timed out during {method}")
            descriptor = self.process.stdout.fileno()
            readable, _, _ = select.select([descriptor], [], [], remaining)
            if not readable:
                raise AppServerError(f"Codex app-server timed out during {method}")

            chunk = os.read(descriptor, 65536)
            if not chunk:
                raise AppServerError(f"Codex app-server exited during {method}")
            self.stdout_buffer.extend(chunk)

    def request(self, method: str, params: dict[str, object]) -> object:
        response_id = self.next_id
        self.next_id += 1
        self._send({"method": method, "id": response_id, "params": params})
        return self._receive(response_id, method)


def _portable_settings(portable: Path) -> list[tuple[tuple[str, ...], object]]:
    with portable.open("rb") as stream:
        parsed = tomllib.load(stream)

    settings: list[tuple[tuple[str, ...], object]] = []

    def visit(value: Mapping[str, Any], prefix: tuple[str, ...]) -> None:
        for key, child in value.items():
            if not KEY_COMPONENT.fullmatch(key):
                raise ValueError(
                    f"portable config key cannot be represented as a Codex keyPath: {key}"
                )
            path = (*prefix, key)
            if isinstance(child, dict):
                if not child:
                    raise ValueError(
                        f"portable config table cannot be empty: {'.'.join(path)}"
                    )
                visit(child, path)
                continue
            try:
                json.dumps(child, allow_nan=False)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"portable config value is not JSON-compatible: {'.'.join(path)}"
                ) from exc
            settings.append((path, child))

    visit(parsed, ())
    if not settings:
        raise ValueError("portable config does not contain any settings")
    return settings


def _value_at(config: Mapping[str, Any], path: tuple[str, ...]) -> object:
    value: object = config
    for component in path:
        if not isinstance(value, Mapping) or component not in value:
            return MISSING
        value = value[component]
    return value


def _same_value(left: object, right: object) -> bool:
    if left is MISSING:
        return False
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(
        right, sort_keys=True, allow_nan=False
    )


def _user_layer(result: object, destination: Path) -> dict[str, Any]:
    if not isinstance(result, dict) or not isinstance(result.get("layers"), list):
        raise AppServerError("config/read did not return configuration layers")

    expected = destination.resolve()
    for layer in result["layers"]:
        if not isinstance(layer, dict):
            continue
        name = layer.get("name")
        if not isinstance(name, dict):
            continue
        if name.get("type") != "user" or name.get("profile") is not None:
            continue
        file_path = name.get("file")
        if isinstance(file_path, str) and Path(file_path).resolve() == expected:
            return layer
    raise AppServerError(f"config/read did not return the user layer for {destination}")


def merge_portable_config(
    portable: Path,
    destination: Path,
    client_factory: Any = AppServer,
) -> bool:
    metadata = destination.lstat()
    if not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError(f"Codex config is not a regular file: {destination}")

    settings = _portable_settings(portable)
    with client_factory() as client:
        read_result = client.request("config/read", {"includeLayers": True})
        layer = _user_layer(read_result, destination)
        current = layer.get("config")
        if not isinstance(current, Mapping):
            raise AppServerError("user config layer has no configuration object")

        edits = [
            {
                "keyPath": ".".join(path),
                "value": value,
                "mergeStrategy": "upsert",
            }
            for path, value in settings
            if not _same_value(_value_at(current, path), value)
        ]
        if not edits:
            destination.chmod(0o600)
            return False

        version = layer.get("version")
        if not isinstance(version, str) or not version:
            raise AppServerError("user config layer has no concurrency version")
        write_result = client.request(
            "config/batchWrite",
            {
                "edits": edits,
                "expectedVersion": version,
                "filePath": str(destination.resolve()),
                "reloadUserConfig": False,
            },
        )
        if not isinstance(write_result, dict) or write_result.get("status") not in {
            "ok",
            "okOverridden",
        }:
            raise AppServerError("config/batchWrite returned an invalid response")
        if Path(str(write_result.get("filePath", ""))).resolve() != destination.resolve():
            raise AppServerError("config/batchWrite wrote an unexpected file")

    destination.chmod(0o600)
    with destination.open("rb") as stream:
        written = tomllib.load(stream)
    missing = [
        ".".join(path)
        for path, value in settings
        if not _same_value(_value_at(written, path), value)
    ]
    if missing:
        raise AppServerError(
            "Codex config write did not persist portable settings: " + ", ".join(missing)
        )
    return True


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--portable",
        type=Path,
        default=repo_root / "codex/config.portable.toml",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path.home() / ".codex/config.toml",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        changed = merge_portable_config(args.portable, args.destination)
    except (AppServerError, OSError, RuntimeError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"  ERROR: Codex portable config sync failed: {exc}", file=sys.stderr)
        return 1
    state = "Updated" if changed else "Already current"
    print(f"  {state}: {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
