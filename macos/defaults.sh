#!/usr/bin/env bash
# macOS 使用者層級偏好設定（鍵盤快捷鍵）。install.sh 不會自動跑；換新機時手動執行：
#   ./macos/defaults.sh
# 冪等，重跑無害。只碰使用者網域的 defaults，不動系統或安全設定。
#
# 目標：Rectangle 是唯一的視窗管理引擎。
# - Rectangle：左半 / 右半 / 最大化 綁 ⌥⌘← / ⌥⌘→ / ⌥⌘↑。
# - macOS 內建「視窗」平鋪快捷鍵（Keyboard Shortcuts › Windows）原本佔用 ⌃⌥⌘←/→/↑，
#   會跟 Rectangle 搶同一個視窗，而且在 Window 選單沒有 Move & Resize 的 app（例如 ChatGPT）
#   按了只會嗶。這裡把那三組關掉；Fn+Ctrl 那組 macOS 預設保留不動。
#
# 對照：ghostty/config 已 unbind super+alt+arrow，讓 Rectangle 接手；
# Chrome 的 ⌥⌘←/→ 切 tab 會被 Rectangle 的全域 hotkey 先攔走，改用 ⌃Tab / ⌃⇧Tab。

set -euo pipefail

# --- Rectangle -----------------------------------------------------------------
# modifierFlags 1572864 = NSEventModifierFlagOption (0x80000) | NSEventModifierFlagCommand (0x100000)
# keyCode 123 = ←, 124 = →, 126 = ↑
RECT=com.knollsoft.Rectangle
defaults write "$RECT" leftHalf  -dict keyCode -int 123 modifierFlags -int 1572864
defaults write "$RECT" rightHalf -dict keyCode -int 124 modifierFlags -int 1572864
defaults write "$RECT" maximize  -dict keyCode -int 126 modifierFlags -int 1572864
echo "Rectangle: ⌥⌘← 左半、⌥⌘→ 右半、⌥⌘↑ 最大化"

# --- macOS 內建視窗平鋪快捷鍵 ------------------------------------------------------
# AppleSymbolicHotKeys ID：237 = ⌃⌥⌘↑、240 = ⌃⌥⌘←、241 = ⌃⌥⌘→（本機讀出的實際值）。
# parameters = (字元碼, keyCode, modifier mask)；65535 表示無字元。10223616 = 0x9C0000 = Fn|⌘|⌥|⌃。
SHK=com.apple.symbolichotkeys
disable_hotkey() {
    local id="$1" keycode="$2"
    defaults write "$SHK" AppleSymbolicHotKeys -dict-add "$id" \
        "{ enabled = 0; value = { parameters = (65535, $keycode, 10223616); type = standard; }; }"
}
disable_hotkey 237 126
disable_hotkey 240 123
disable_hotkey 241 124
# 通知系統重讀快捷鍵設定，不用登出。
/System/Library/PrivateFrameworks/SystemAdministration.framework/Resources/activateSettings -u
echo "macOS: 已停用 ⌃⌥⌘←/→/↑ 的內建視窗平鋪快捷鍵"

# Rectangle 只在啟動時讀 defaults：有在跑就重啟，沒在跑就啟動。
if pgrep -xq Rectangle; then
    osascript -e 'quit app "Rectangle"' && sleep 1
fi
open -a Rectangle
echo "Rectangle 已（重新）啟動"
