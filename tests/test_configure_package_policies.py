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

PNPM_RC_POLICY = configure_package_policies.PNPM_RC_POLICY
PNPM_YAML_LINE = f"minimumReleaseAge: {PNPM_RC_POLICY.value}"
PNPM_YAML_NEW_FILE = f"{PNPM_RC_POLICY.comment}\n{PNPM_YAML_LINE}\n"

# (platform, XDG_CONFIG_HOME, pnpm config dir relative to the temporary root)
PNPM_CONFIG_DIR_CASES = (
    ("darwin", "xdg", "xdg/pnpm"),
    ("darwin", None, "home/Library/Preferences/pnpm"),
    ("darwin", "", "home/Library/Preferences/pnpm"),
    ("linux", None, "home/.config/pnpm"),
)


class ConfigurePackagePoliciesTests(unittest.TestCase):
    def configure(self, home: Path) -> None:
        # Pin platform and env so a host XDG_CONFIG_HOME cannot redirect writes.
        configure_package_policies.configure_package_policies(
            home, REPO_ROOT, platform="linux", env={}
        )

    def for_each_pnpm_config_dir(self, check) -> None:
        for platform, xdg, expected in PNPM_CONFIG_DIR_CASES:
            with self.subTest(platform=platform, xdg=xdg):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    root = Path(temporary_directory)
                    env = {}
                    if xdg is not None:
                        env["XDG_CONFIG_HOME"] = str(root / xdg) if xdg else ""

                    def configure() -> list[Path]:
                        return configure_package_policies.configure_package_policies(
                            root / "home", REPO_ROOT, platform=platform, env=env
                        )

                    check(root, root / expected, configure)

    def test_pnpm_files_follow_pnpm_config_dir_order(self) -> None:
        def check(root: Path, config_dir: Path, configure) -> None:
            configured = configure()

            for name in ("rc", "config.yaml"):
                written = list(root.rglob(f"pnpm/{name}"))
                self.assertEqual(written, [config_dir / name])
                self.assertIn(config_dir / name, configured)
            self.assertIn(
                f"{PNPM_RC_POLICY.key}={PNPM_RC_POLICY.value}",
                (config_dir / "rc").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                (config_dir / "config.yaml").read_text(encoding="utf-8"),
                PNPM_YAML_NEW_FILE,
            )
            self.assertEqual(
                stat.S_IMODE((config_dir / "config.yaml").stat().st_mode), 0o600
            )

        self.for_each_pnpm_config_dir(check)

    def test_pnpm_config_yaml_keeps_other_settings(self) -> None:
        existing = (
            "# Global pnpm settings\n"
            "registries:\n"
            "  default: https://registry.example.invalid/\n"
            "storeDir: store\n"
            "minimumReleaseAgeExclude:\n"
            "- '@example/*'\n"
        )

        def check(_root: Path, config_dir: Path, configure) -> None:
            config_dir.mkdir(parents=True)
            (config_dir / "config.yaml").write_text(existing, encoding="utf-8")

            configure()

            self.assertEqual(
                (config_dir / "config.yaml").read_text(encoding="utf-8"),
                f"{existing}\n{PNPM_YAML_NEW_FILE}",
            )

        self.for_each_pnpm_config_dir(check)

    def test_pnpm_config_yaml_replaces_old_value(self) -> None:
        existing = (
            "registries:\n"
            "  default: https://registry.example.invalid/\n"
            "minimumReleaseAge: 1440 # one day\n"
            "minimumReleaseAgeExclude:\n"
            "- '@example/*'\n"
            '"minimumReleaseAge":\n'
            "  2880\n"
            "storeDir: store\n"
        )
        expected = (
            "registries:\n"
            "  default: https://registry.example.invalid/\n"
            f"{PNPM_YAML_LINE}\n"
            "minimumReleaseAgeExclude:\n"
            "- '@example/*'\n"
            "storeDir: store\n"
        )

        def check(_root: Path, config_dir: Path, configure) -> None:
            config_dir.mkdir(parents=True)
            (config_dir / "config.yaml").write_text(existing, encoding="utf-8")

            configure()

            self.assertEqual(
                (config_dir / "config.yaml").read_text(encoding="utf-8"), expected
            )

        self.for_each_pnpm_config_dir(check)

    def test_pnpm_config_yaml_leaves_nested_lookalike_keys_alone(self) -> None:
        # Not a real pnpm config: these lines only look like the policy key.
        lookalikes = (
            "notes: |\n"
            "  minimumReleaseAge: 5\n"
            "nested:\n"
            "  minimumReleaseAge: 1\n"
            "items:\n"
            "- minimumReleaseAge: 2\n"
        )
        cases = (
            (lookalikes, f"{lookalikes}\n{PNPM_YAML_NEW_FILE}"),
            (
                f"{lookalikes}minimumReleaseAge: 1440\n",
                f"{lookalikes}{PNPM_YAML_LINE}\n",
            ),
        )
        for existing, expected in cases:
            with self.subTest(existing=existing):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    home = Path(temporary_directory)
                    config = home / ".config/pnpm/config.yaml"
                    config.parent.mkdir(parents=True)
                    config.write_text(existing, encoding="utf-8")

                    self.configure(home)

                    self.assertEqual(config.read_text(encoding="utf-8"), expected)

    def test_pnpm_config_yaml_refuses_layouts_it_cannot_edit_safely(self) -> None:
        layouts = (
            "{minimumReleaseAge: 1440}\n",
            "---\nminimumReleaseAge: 1440\n",
            "  minimumReleaseAge: 1440\n",
            "- minimumReleaseAge\n",
        )
        for layout in layouts:
            with self.subTest(layout=layout):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    home = Path(temporary_directory)
                    config = home / ".config/pnpm/config.yaml"
                    config.parent.mkdir(parents=True)
                    config.write_text(layout, encoding="utf-8")

                    with self.assertRaisesRegex(RuntimeError, "by hand in .*config.yaml"):
                        self.configure(home)
                    self.assertEqual(config.read_text(encoding="utf-8"), layout)

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
            (home / ".config/pnpm/config.yaml").write_text(
                "minimumReleaseAge: 1\nminimumReleaseAge: 2\n", encoding="utf-8"
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
                    home / ".config/pnpm/config.yaml",
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
                (home / ".config/pnpm/config.yaml").read_text(),
                f"{PNPM_YAML_LINE}\n",
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

    def test_bun_inline_comment_header_remains_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            home = Path(temporary_directory)
            bun_path = home / ".bunfig.toml"
            bun_path.write_text(
                '[install] # Bun settings\nregistry = "https://registry.example.invalid/"\n',
                encoding="utf-8",
            )
            self.configure(home)
            parsed = tomllib.loads(bun_path.read_text(encoding="utf-8"))
            self.assertEqual(parsed["install"]["minimumReleaseAge"], 604800)
            self.assertEqual(bun_path.read_text().count("[install]"), 1)

    def test_bun_array_table_ends_install_section(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            home = Path(temporary_directory)
            bun_path = home / ".bunfig.toml"
            bun_path.write_text(
                "[install]\n"
                'registry = "https://registry.example.invalid/"\n'
                "[[install.security.scanner]]\n"
                'package = "scanner"\n'
                "minimumReleaseAge = 1\n",
                encoding="utf-8",
            )
            self.configure(home)
            parsed = tomllib.loads(bun_path.read_text(encoding="utf-8"))
            self.assertEqual(parsed["install"]["minimumReleaseAge"], 604800)
            self.assertEqual(
                parsed["install"]["security"]["scanner"][0]["minimumReleaseAge"],
                1,
            )


if __name__ == "__main__":
    unittest.main()
