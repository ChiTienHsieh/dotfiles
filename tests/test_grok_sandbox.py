"""Structure checks for the Grok worker sandbox deny list."""
from pathlib import Path
import tomllib
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
SANDBOX = REPO_ROOT / "grok" / "sandbox.toml"
HOME_ROOTS = ("/Users/*/", "/home/*/")  # macOS, Linux (Grok does not expand `~`)


def deny_list() -> list[str]:
    with SANDBOX.open("rb") as handle:
        return tomllib.load(handle)["profiles"]["cc-worker"]["deny"]


def home_entries(deny: list[str], root: str) -> set[str]:
    """Home-relative suffixes (e.g. `.ssh/**`) denied under one home root."""
    return {entry.removeprefix(root) for entry in deny if entry.startswith(root)}


class GrokSandboxDenyTests(unittest.TestCase):
    def test_every_home_entry_is_denied_on_macos_and_linux(self) -> None:
        deny = deny_list()
        macos, linux = (home_entries(deny, root) for root in HOME_ROOTS)
        self.assertTrue(macos)
        self.assertEqual(sorted(macos - linux), [], "/Users/* deny without /home/* twin")
        self.assertEqual(sorted(linux - macos), [], "/home/* deny without /Users/* twin")

    def test_entries_are_absolute_or_workspace_wide(self) -> None:
        # Relative globs anchor at the workspace, so `~/.ssh/**` or `.ssh/**`
        # would never reach the real home directory.
        for entry in deny_list():
            with self.subTest(entry=entry):
                self.assertTrue(entry.startswith(("/", "**/")), "relative deny entry")

    def test_secrets_directory_contents_are_denied(self) -> None:
        deny = deny_list()
        for root in HOME_ROOTS:
            with self.subTest(root=root):
                self.assertIn(".secrets/**", home_entries(deny, root))


if __name__ == "__main__":
    unittest.main()
