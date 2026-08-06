#!/usr/bin/env python3
"""Compose Codex Stop policies into one bounded continuation prompt."""

from __future__ import annotations

import json
import sys
from json import JSONDecodeError

from request_thread_title import prepare_title_request, take_title_request
from set_thread_title import set_thread_title
from stop_dirty_worktree import build_dirty_worktree_followup, track_touched_worktrees


TITLE_CHECKPOINT = """Thread 標題檢查：

依使用者下一步，只在以下狀態改名：
- ⏸️：缺資料、權限、CI、部署或前置條件，需使用者協助。
- ⏳：只等使用者做簡單選擇。
- 🔎：使用者需理解重要背景或取捨。
- 📦：沒有未完成責任或重要學習，值得封存。

停止、閒置、已有 final answer 或只有本機 commit，都不足以標 📦。若 agent 應繼續工作且使用者無須行動，不改名。

標題使用台灣繁中，格式（共三段，以兩個半形 ` | ` 分隔）：
<一個狀態 emoji> <repo／project／最小可辨識範圍> | <使用者目的> | <進度>
合格範例：`📦 dotfiles | 精簡 hook prompt | 完成`
開頭只能有一個上述狀態 emoji，且語意須和第三段進度一致。
送出前確認：只有一行、恰有兩個 ` | `、不得使用全形 `｜`，且三段都不是空白。
技術識別字保留原文；目標 24–32 字，最多 40 字。

若有 `apply_patch`，只能呼叫一次，把以下檔案的完整內容改成只有標題與一個結尾換行：
{request_path}
目前內容是 `NO_TITLE_REQUEST`。不得用 shell 寫檔。工具或檔案不可用就略過；patch 失敗只警告一次。

只能改標題；📦 只是封存建議，不得自行封存。
"""


def emit(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def apply_queued_title(payload: dict[str, object]) -> dict[str, object]:
    thread_id = str(payload.get("session_id") or "")
    try:
        request = take_title_request(thread_id)
        if request:
            set_thread_title(*request)
    except (OSError, ValueError, RuntimeError):
        return {
            "continue": True,
            "systemMessage": "Thread 標題更新失敗；已略過。",
        }
    return {"continue": True}


def has_explicitly_null_transcript_path(payload: dict[str, object]) -> bool:
    """Return true only when the hook payload explicitly reports a null path."""
    return "transcript_path" in payload and payload["transcript_path"] is None


def build_stop_result(payload: dict[str, object]) -> dict[str, object]:
    already_continued_by_stop_hook = payload.get("stop_hook_active") is True

    # Side chats are ephemeral forks and expose a null transcript_path, but a
    # persisted transcript-path lookup failure can do the same. Skip only the
    # inapplicable title checkpoint; retain dirty-worktree safety on first Stop.
    if has_explicitly_null_transcript_path(payload):
        if already_continued_by_stop_hook:
            return {"continue": True}
        dirty_reason = build_dirty_worktree_followup(payload)
        if not dirty_reason:
            return {"continue": True}
        return {
            "decision": "block",
            "reason": dirty_reason
            + "\n\n完成工作區整理後，只補整理選項；不要重述或擴寫上一則 final answer。",
        }

    if already_continued_by_stop_hook:
        return apply_queued_title(payload)

    thread_id = str(payload.get("session_id") or "")
    try:
        request_path = str(prepare_title_request(thread_id))
    except (OSError, ValueError, RuntimeError):
        request_path = "無法使用，略過標題更新"
    reasons = [
        TITLE_CHECKPOINT.format(request_path=request_path)
    ]
    dirty_reason = build_dirty_worktree_followup(payload)
    if dirty_reason:
        reasons.append(dirty_reason)

    reasons.append(
        "若有「工作區整理」，完成標題檢查後只補整理選項；否則不要重述或擴寫上一則 "
        "final answer。"
    )
    return {"decision": "block", "reason": "\n\n".join(reasons)}


def handle_payload(payload: dict[str, object]) -> dict[str, object]:
    event_name = payload.get("hook_event_name")
    if event_name == "PostToolUse":
        track_touched_worktrees(payload)
        return {"continue": True}
    if event_name == "Stop":
        return build_stop_result(payload)
    return {"continue": True}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except JSONDecodeError:
        return emit({"continue": True})
    if not isinstance(payload, dict):
        return emit({"continue": True})
    return emit(handle_payload(payload))


if __name__ == "__main__":
    raise SystemExit(main())
