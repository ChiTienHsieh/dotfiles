#!/usr/bin/env python3
"""檢查每個 SKILL.md 開頭設定區（frontmatter）用到的欄位。

skill 可以在 frontmatter 幫自己放行指令（例如 allowed-tools），之後也可能出現
其他會影響權限的欄位。這支程式放在 .github/ 底下，改它要 repo owner approve；
skill 本身改得很頻繁，不在 CODEOWNERS 裡，所以權限相關的欄位由這裡把關：

- 只准用 SAFE_KEYS 裡的欄位，沒見過的欄位一律擋下（寧可誤擋）。
- allowed-tools 只准 ALLOWED_TOOLS 列的 skill 用，值也要完全一樣。

用法：不帶參數就檢查 git 追蹤的所有 SKILL.md；也可以直接給檔案路徑。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# 不影響權限的欄位。要加新欄位，先確認它不會放行指令、掛 hook 或改權限模式。
SAFE_KEYS = {
    "name",
    "description",
    "disable-model-invocation",
    "user-invocable",
    "argument-hint",
    "metadata",
    "license",
}

# 准用 allowed-tools 的 skill，以及它准放行的內容（完全比對）。
ALLOWED_TOOLS = {
    "skills/claude/playwright-cli/SKILL.md": "Bash(playwright-cli:*)",
    "skills/shared/delegate/SKILL.md": "Bash(~/.claude/skills/delegate/scripts/pick-worker:*)",
}

# 頂層欄位：行首不是空白、不是註解，後面接冒號。其他寫法（引號、{...}）
# 會被當成沒見過的欄位擋下。
TOP_LEVEL_KEY = re.compile(r"^([^\s#][^:]*):(.*)$")


def frontmatter_entries(text: str) -> list[tuple[str, str]]:
    # 開頭的 BOM（檔案開頭看不見的編碼標記）和空行先去掉，免得藏一段 frontmatter 卻被當成沒有。
    lines = text.lstrip("\ufeff \t\r\n").splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    entries: list[tuple[str, str]] = []
    for line in lines[1:]:
        if line.strip() == "---":
            return entries
        match = TOP_LEVEL_KEY.match(line)
        if match:
            entries.append((match.group(1), match.group(2)))
        elif entries and line.strip() and not line.lstrip().startswith("#"):
            key, value = entries[-1]
            entries[-1] = (key, f"{value} {line}")
    # 沒有結尾的 --- 就不是 frontmatter，Claude Code 也不會讀。
    return []


def normalize(value: str) -> str:
    return " ".join(value.split()).strip("'\"")


def check(path: str) -> list[str]:
    errors = []
    for key, value in frontmatter_entries(Path(path).read_text(encoding="utf-8")):
        if key == "allowed-tools":
            expected = ALLOWED_TOOLS.get(path)
            if expected is None:
                errors.append(f"{path}: 這個 skill 不在 allowed-tools 白名單裡")
            elif normalize(value) != expected:
                errors.append(
                    f"{path}: allowed-tools 跟白名單不同（白名單：{expected}；"
                    f"實際：{normalize(value)}）"
                )
        elif key not in SAFE_KEYS:
            errors.append(f"{path}: 沒見過的 frontmatter 欄位 {key!r}")
    return errors


def main(argv: list[str]) -> int:
    paths = argv or subprocess.run(
        ["git", "ls-files", "*SKILL.md"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split()
    errors = [error for path in paths for error in check(path)]
    for error in errors:
        print(f"::error::{error}")
    if errors:
        print(
            "要放行的話，由 repo owner 改 .github/scripts/check_skill_frontmatter.py"
            " 的白名單。"
        )
        return 1
    print(f"檢查了 {len(paths)} 個 SKILL.md，frontmatter 都在白名單內。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
