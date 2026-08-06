from __future__ import annotations

import stat
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import configure_package_policies  # noqa: E402


class ConfigurePackagePoliciesTests(unittest.TestCase):
    def configure(self, home: Path) -> None:
        configure_package_policies.configure_package_policies(home, REPO_ROOT)

    def test_preserves_existing_registry_settings_and_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            home = Path(temporary_directory)
            (home / ".config/pnpm").mkdir(parents=True)
            (home / ".npmrc").write_text(
                "registry=https://registry.example.invalid/\n"
                "//registry.example.invalid/:_authToken=${NPM_TOKEN}\n",
                encoding="utf-8",
            )
            (home / ".config/pnpm/rc").write_text(
                "registry=https://registry.example.invalid/\n"
                "//registry.example.invalid/:_authToken=${PNPM_TOKEN}\n",
                encoding="utf-8",
            )
            (home / ".bunfig.toml").write_text(
                "[install.scopes]\n"
                '"@example" = { token = "$BUN_TOKEN", url = '
                '"https://registry.example.invalid/" }\n',
                encoding="utf-8",
            )

            self.configure(home)

            npm = (home / ".npmrc").read_text(encoding="utf-8")
            pnpm = (home / ".config/pnpm/rc").read_text(encoding="utf-8")
            bun_path = home / ".bunfig.toml"
            bun = bun_path.read_text(encoding="utf-8")
            self.assertIn("${NPM_TOKEN}", npm)
            self.assertIn("${PNPM_TOKEN}", pnpm)
            self.assertIn("$BUN_TOKEN", bun)
            self.assertIn("min-release-age=7", npm)
            self.assertIn("minimum-release-age=10080", pnpm)
            self.assertEqual(
                tomllib.loads(bun)["install"]["minimumReleaseAge"], 604800
            )

    def test_migrates_prior_symlinks_to_private_real_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            home = Path(temporary_directory)
            destinations = (
                (home / ".bunfig.toml", REPO_ROOT / "bun/.bunfig.toml"),
                (home / ".npmrc", REPO_ROOT / "npm/.npmrc"),
                (
                    home / ".config/pnpm/rc",
                    REPO_ROOT / "pnpm/.config/pnpm/rc",
                ),
            )
            for destination, source in destinations:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.symlink_to(source)

            source_contents = {
                source: source.read_bytes() for _destination, source in destinations
            }
            self.configure(home)

            for destination, source in destinations:
                self.assertTrue(destination.is_file())
                self.assertFalse(destination.is_symlink())
                self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)
                self.assertEqual(source.read_bytes(), source_contents[source])

    def test_is_idempotent_and_removes_duplicate_policy_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            home = Path(temporary_directory)
            (home / ".config/pnpm").mkdir(parents=True)
            (home / ".npmrc").write_text(
                "min-release-age=1\nmin-release-age=2\n", encoding="utf-8"
            )
            (home / ".config/pnpm/rc").write_text(
                "minimum-release-age=1\nminimum-release-age=2\n", encoding="utf-8"
            )
            (home / ".bunfig.toml").write_text(
                "[install]\nminimumReleaseAge = 1\nminimumReleaseAge = 2\n",
                encoding="utf-8",
            )

            self.configure(home)
            first = {
                path: path.read_bytes()
                for path in (
                    home / ".bunfig.toml",
                    home / ".npmrc",
                    home / ".config/pnpm/rc",
                )
            }
            self.configure(home)

            for path, contents in first.items():
                self.assertEqual(path.read_bytes(), contents)
            self.assertEqual((home / ".npmrc").read_text().count("min-release-age="), 1)
            self.assertEqual(
                (home / ".config/pnpm/rc")
                .read_text()
                .count("minimum-release-age="),
                1,
            )
            self.assertEqual(
                (home / ".bunfig.toml").read_text().count("minimumReleaseAge ="),
                1,
            )

    def test_refuses_non_file_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            home = Path(temporary_directory)
            (home / ".bunfig.toml").mkdir()
            with self.assertRaisesRegex(RuntimeError, "not a regular file"):
                self.configure(home)


if __name__ == "__main__":
    unittest.main()
