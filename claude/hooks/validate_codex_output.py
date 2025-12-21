#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = []
# ///
"""
PreToolUse hook: 驗證 codex read-only 指令的 -o 參數只能寫到 /tmp/
"""

from __future__ import annotations

import json
import sys
import re


def extract_output_path(command: str) -> str | None:
    """
    從 codex 指令中提取 -o 參數的路徑

    範例:
    - 'codex exec -o /tmp/foo.txt "task"' → '/tmp/foo.txt'
    - 'codex exec -o "/tmp/foo.txt" "task"' → '/tmp/foo.txt'
    - 'OUTPUT_FILE="/tmp/foo.txt" && codex -o "$OUTPUT_FILE"' → '/tmp/foo.txt'
    """
    # 先提取 -o 參數的值（可能是變數或路徑）
    match = re.search(r'-o\s+([\'"]?)([^\s\'"]+)\1', command)
    if not match:
        return None

    output_value = match.group(2)

    # 如果是變數引用（如 $OUTPUT_FILE），嘗試解析變數賦值
    if output_value.startswith('$'):
        var_name = output_value[1:]  # 去掉 $ 符號
        # 尋找變數賦值：VAR_NAME="value" 或 VAR_NAME='value'
        # 支援引號內的任意字元（包括空白、$() 等）
        var_pattern = rf'{var_name}=([\'"])(.+?)\1'
        var_match = re.search(var_pattern, command)
        if var_match:
            return var_match.group(2)

    # 否則直接返回路徑
    return output_value


def is_codex_readonly_command(command: str) -> bool:
    """檢查是否是 codex read-only 指令"""
    return (
        'codex' in command and
        '--sandbox read-only' in command
    )


def validate_command(tool_name: str, command: str) -> dict:
    """
    驗證指令，返回 {"decision": "approve"|"block", "reason": "..."}
    """
    # 只檢查 Bash tool
    if tool_name != "Bash":
        return {"decision": "approve"}

    # 只檢查 codex read-only 指令
    if not is_codex_readonly_command(command):
        return {"decision": "approve"}

    # 檢查是否有 -o 參數
    output_path = extract_output_path(command)
    if not output_path:
        # 沒有 -o 參數，放行
        return {"decision": "approve"}

    # 驗證路徑必須在 /tmp/ 下
    if not output_path.startswith('/tmp/'):
        return {
            "decision": "block",
            "reason": (
                f"🚫 Codex read-only 指令的 -o 參數只能寫到 /tmp/ 下！\n"
                f"   當前路徑: {output_path}\n"
                f"   建議: OUTPUT_FILE=\"/tmp/codex-$(date +%Y%m%d-%H%M%S)-task.txt\""
            )
        }

    # 驗證通過！
    return {"decision": "approve"}


def main():
    try:
        # 從 stdin 讀取 hook payload
        payload = json.loads(sys.stdin.read())

        tool_name = payload.get("tool_name", "")
        tool_input = payload.get("tool_input", {})
        command = tool_input.get("command", "")

        # 驗證指令
        result = validate_command(tool_name, command)

        # 輸出結果（給 Claude 看）
        print(json.dumps(result, ensure_ascii=False))

        # Exit code 決定是否 block
        if result["decision"] == "block":
            sys.exit(2)  # 2 = block tool execution
        else:
            sys.exit(0)  # 0 = allow

    except Exception as e:
        # Hook 發生錯誤時，放行（避免卡住 CC）
        error_msg = {
            "decision": "approve",
            "reason": f"⚠️ Hook validation error: {e}"
        }
        print(json.dumps(error_msg), file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
