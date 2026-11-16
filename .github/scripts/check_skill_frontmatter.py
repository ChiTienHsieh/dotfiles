#!/usr/bin/env python3
"""檢查每個 SKILL.md 開頭設定區（frontmatter）用到的欄位。

skill 可以在 frontmatter 幫自己放行指令（例如 allowed-tools），之後也可能出現
其他會影響權限的欄位。這支程式放在 .github/ 底下，改它要 repo owner approve；
skill 本身改得很頻繁，不在 CODEOWNERS 裡，所以權限相關的欄位由這裡把關。

原則是格式不對就擋，不猜 YAML 會怎麼解讀：
- frontmatter 每一行都要是單純的「欄位: 值」，只有 metadata 底下可以縮排兩格。
  縮排、tab、續行、空行、註解、`?`、`{` 這些寫法一律擋。
- 只准用 SAFE_KEYS 裡的欄位，沒見過的欄位一律擋。
- allowed-tools 只准 ALLOWED_TOOLS 列的 skill 用，值要一字不差。

用法：不帶參數就檢查 git 追蹤的所有 SKILL.md（檔名不分大小寫）；也可以直接給檔案路徑。
"""

import re
import subprocess
import sys
import unicodedata
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

# 准用 allowed-tools 的 skill，以及它准放行的內容（一字不差）。
ALLOWED_TOOLS = {
    "skills/claude/playwright-cli/SKILL.md": "Bash(playwright-cli:*)",
    "skills/shared/delegate/SKILL.md": "Bash(~/.claude/skills/delegate/scripts/pick-worker:*)",
}

KEY_LINE = re.compile(r"^([A-Za-z_][\w-]*):(?: (.*))?$")


def check(path: str) -> list[str]:
    # 開頭的 BOM（檔案開頭看不見的編碼標記）和空行先去掉，
    # 不然前面墊一個空行，整段 frontmatter 就不會被檢查。
    text = Path(path).read_text(encoding="utf-8").lstrip("﻿ \t\r\n")
    if not text.startswith("---"):
        return []
    lines = text.replace("\r\n", "\n").split("\n")
    if lines[0] != "---" or "---" not in lines[1:]:
        return [f"{path}: frontmatter 的開頭和結尾都要是單獨一行 ---"]
    errors = []
    key = None
    for line in lines[1 : lines.index("---", 1)]:
        match = KEY_LINE.match(line)
        if not line.isprintable():
            # 有些 YAML parser 把 U+2028 這類字元當換行，一行就能藏第二個欄位。
            errors.append(f"{path}: frontmatter 裡不能有控制字元或特殊換行：{line!r}")
        elif "---" in line:
            # Claude Code 碰到 --- 就當成 frontmatter 結束，跟這裡切的位置會對不上。
            errors.append(f"{path}: frontmatter 裡不能出現 ---：{line!r}")
        elif match:
            key, value = match.group(1), match.group(2) or ""
            if key == "allowed-tools":
                if ALLOWED_TOOLS.get(path) != value:
                    errors.append(f"{path}: allowed-tools 不在白名單裡，或跟白名單寫的不一樣")
            elif key not in SAFE_KEYS:
                errors.append(f"{path}: 沒見過的 frontmatter 欄位 {key!r}")
        elif not (key == "metadata" and line.startswith("  ")):
            errors.append(f"{path}: 這一行不是「欄位: 值」的寫法：{line!r}")
    return errors


def tracked_skill_files() -> list[str]:
    output = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    # 檔名先做 Unicode 正規化再比對，ſKILL.md 這類長得像的檔名也算。
    return [
        path
        for path in output.split("\0")
        if path and unicodedata.normalize("NFKC", Path(path).name).casefold() == "skill.md"
    ]


def main(argv: list[str]) -> int:
    paths = argv or tracked_skill_files()
    errors = [error for path in paths for error in check(path)]
    for error in errors:
        print(f"::error::{error}")
    if errors:
        print("要放行的話，由 repo owner 改 .github/scripts/check_skill_frontmatter.py 的白名單。")
        return 1
    print(f"檢查了 {len(paths)} 個 SKILL.md，frontmatter 都在白名單內。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
