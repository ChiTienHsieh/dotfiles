"""Codex agent 的 toml 跟它的 Claude agent md 要是同一份定義。

toml 用 `# twin: <md 路徑>` 註解指向 md；md 是正本，toml 的 name、description、
developer_instructions 必須跟 md 的 name、description、內文相同。
"""

import json
from pathlib import Path
import re
import tomllib
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_AGENTS_DIR = REPO_ROOT / "codex" / "agents"
CLAUDE_AGENTS_DIR = REPO_ROOT / "claude" / "agents"
TWIN_RE = re.compile(r"(?m)^# twin: (\S+)")


def yaml_scalar(raw: str) -> str:
    """單行 YAML 值：雙引號照 JSON 規則解跳脫字元，單引號把 '' 還原成 '。"""
    if raw.startswith('"'):
        return json.loads(raw)
    if raw.startswith("'"):
        return raw[1:-1].replace("''", "'")
    return raw


def claude_agent(path: Path) -> tuple[dict[str, str], str]:
    """Claude agent md 的 frontmatter 頂層欄位與內文。"""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path.relative_to(REPO_ROOT)} 開頭不是 frontmatter")
    _, frontmatter, body = text.split("---\n", 2)
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        key, sep, value = line.partition(":")
        if sep and line[:1].strip():
            fields[key.strip()] = yaml_scalar(value.strip())
    return fields, body


class AgentTwinTests(unittest.TestCase):
    maxDiff = None

    def test_codex_twin_matches_claude_agent(self) -> None:
        claude_names = {
            claude_agent(md)[0].get("name") for md in CLAUDE_AGENTS_DIR.glob("*.md")
        }
        for toml_path in sorted(CODEX_AGENTS_DIR.glob("*.toml")):
            text = toml_path.read_text(encoding="utf-8")
            codex = tomllib.loads(text)
            match = TWIN_RE.search(text)
            label = toml_path.relative_to(REPO_ROOT)
            if not match:
                # 同名卻沒標 twin，兩份就沒人比對了，一樣算錯。
                with self.subTest(toml=label):
                    self.assertNotIn(
                        codex.get("name"),
                        claude_names,
                        "跟 Claude agent 同名，要加 `# twin:` 註解指向那份 md",
                    )
                continue
            md_path = REPO_ROOT / match.group(1)
            with self.subTest(toml=label, md=match.group(1)):
                self.assertTrue(md_path.is_file(), "`# twin:` 指向的 md 不存在")
                fields, body = claude_agent(md_path)
                self.assertEqual(codex.get("name"), fields.get("name"))
                self.assertEqual(codex.get("description"), fields.get("description"))
                self.assertEqual(
                    codex.get("developer_instructions", "").strip(), body.strip()
                )


if __name__ == "__main__":
    unittest.main()
