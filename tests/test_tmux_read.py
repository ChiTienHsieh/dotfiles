#!/usr/bin/env python3
"""The allow-listed tmux-read wrapper must never mutate tmux or run code."""

from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/shared/tmux-orchestration/scripts/tmux-read"


def load_tmux_read():
    loader = SourceFileLoader("tmux_read", str(SCRIPT))
    module = module_from_spec(spec_from_loader("tmux_read", loader))
    loader.exec_module(module)
    return module


tmux_read = load_tmux_read()


class TmuxReadTests(unittest.TestCase):
    def assert_allowed(self, argv, expected):
        self.assertEqual(tmux_read.validate(argv), ["tmux", *expected])

    def assert_rejected(self, argv):
        with self.assertRaises(tmux_read.Rejected, msg=argv):
            tmux_read.validate(argv)

    def test_read_only_queries_pass_through(self) -> None:
        self.assert_allowed(
            ["list-panes", "-a", "-F", "#{pane_id} #{pane_current_command}"],
            ["list-panes", "-a", "-F", "#{pane_id} #{pane_current_command}"],
        )
        self.assert_allowed(
            ["capture-pane", "-pt", "%24", "-S", "-40"],
            ["capture-pane", "-p", "-t", "%24", "-S", "-40"],
        )
        self.assert_allowed(
            ["display-message", "-p", "-t", "%3", "#{session_name}"],
            ["display-message", "-p", "-t", "%3", "#{session_name}"],
        )
        self.assert_allowed(
            ["show-options", "-gv", "prefix"],
            ["show-options", "-g", "-v", "prefix"],
        )
        self.assert_allowed(
            ["list-sessions", "-F", ""], ["list-sessions", "-F", ""]
        )

    def test_mutating_subcommands_are_rejected(self) -> None:
        for sub in ("kill-server", "kill-session", "send-keys", "run-shell",
                    "set-option", "join-pane", "new-window", "source-file"):
            self.assert_rejected([sub])
        self.assert_rejected([])

    def test_tmux_command_chaining_is_rejected(self) -> None:
        self.assert_rejected(["list-sessions", ";", "kill-server"])
        self.assert_rejected(["list-sessions", "\\;", "kill-server"])
        self.assert_rejected(["list-panes", "-F", "x;", "kill-server"])

    def test_shell_and_nested_formats_are_rejected(self) -> None:
        for fmt in ("#(touch /tmp/pwned)", "#{E:status-right}",
                    "#{?pane_active,#(id),x}", "#[fg=red]", "#S"):
            self.assert_rejected(["list-panes", "-F", fmt])
            self.assert_rejected(["list-panes", "-f", fmt])
            self.assert_rejected(["display-message", "-p", fmt])

    def test_side_effect_flags_are_rejected(self) -> None:
        self.assert_rejected(["capture-pane", "-t", "%3"])
        self.assert_rejected(["capture-pane", "-p", "-b", "buf"])
        self.assert_rejected(["display-message", "hello"])
        self.assert_rejected(["display-message", "-p", "-I"])
        self.assert_rejected(["display-message", "-p", "-c", "client"])
        self.assert_rejected(["list-panes", "-L", "other-socket"])

    def test_arguments_are_shape_checked(self) -> None:
        self.assert_rejected(["capture-pane", "-p", "-t", "%3 #(id)"])
        self.assert_rejected(["capture-pane", "-p", "-S", "$(id)"])
        self.assert_rejected(["show-options", "-g", "status-right", "extra"])
        self.assert_rejected(["list-panes", "stray"])


if __name__ == "__main__":
    unittest.main()
