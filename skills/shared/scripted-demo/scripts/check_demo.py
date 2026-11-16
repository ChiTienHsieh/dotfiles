"""逐格跑完 scripted demo，用程式檢查規則，並把每一格截圖。

用法（需要 Playwright；預設借用系統的 Edge，不必另外下載瀏覽器）：
    uv run --with playwright python check_demo.py demo.html [--dark] [--out shots/] [--browser chromium]

檢查項目（任一不符就以 exit code 1 結束）：
  - 頁面沒有 JavaScript 錯誤，且有 window.__scriptedDemo（用 player.js 建立）
  - 每一步結束時找得到目標錨點（data-demo）
  - 目標完整落在 spotlight 裡、游標點在 spotlight 裡、游標在舞台內
  - 旁白不蓋住目標
  - 用 2 倍速實際播一遍：移動途中游標也一直在 spotlight 裡、不出舞台
  - 換視窗大小後，spotlight 仍框住目標（位置跟著元素重算，不是寫死座標）
  - 按停止後，畫面回到導覽前的狀態
  - 連播途中切換淺色／深色兩次，導覽照樣播到最後一格
  - 加 --dark 時：先切到深色模式再檢查，並確認頁面真的替舞台換了深色配色
三種視窗大小對應瀏覽器縮放 80%、100%、125%（以 1280x800 為 100%）。
"""
import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SIZES = [(1600, 1000), (1280, 800), (1024, 640)]
TOL = 1.5  # 像素誤差容忍


# 2 倍速全部連播，每 50 毫秒量一次畫面上「實際」的游標尖端與 spotlight 位置
ANIMATED_PASS = """async () => {
  const d = window.__scriptedDemo, st = d.stage, bad = [];
  let badCount = 0, samples = 0;
  const theme0 = d.theme;
  d._setSpeed(2); d.playAll();
  // 播放途中切換配色兩次（最後切回原本的），導覽不能因此中斷
  setTimeout(() => d.toggleTheme(), 1500);
  setTimeout(() => d.toggleTheme(), 3500);
  await new Promise(done => {
    const t0 = Date.now();
    const iv = setInterval(() => {
      samples++;
      if (d.spotEl.style.display !== 'none' && d.cursorEl.style.display !== 'none') {
        const s = st.getBoundingClientRect(), a = d.spotEl.getBoundingClientRect(), c = d.cursorEl.getBoundingClientRect();
        const x = c.left + 3, y = c.top + 2, tol = 3;
        const add = kind => { badCount++; if (bad.length < 8) bad.push({ idx: d.idx, kind }); };
        if (x < a.left - tol || x > a.right + tol || y < a.top - tol || y > a.bottom + tol) add('游標跑到 spotlight 外面（暗處）');
        if (x < s.left || x > s.right || y < s.top || y > s.bottom) add('游標跑出舞台');
      }
      if (!d.playing || Date.now() - t0 > 180000) { clearInterval(iv); done(); }
    }, 50);
  });
  d._setSpeed(1);
  const end = d.idx === d.frames.length - 1 && d.theme === theme0;
  return { samples, bad, badCount, end, idx: d.idx };
}"""


def inside(r, box):
    return (r["left"] >= box["left"] - TOL and r["top"] >= box["top"] - TOL
            and r["left"] + r["width"] <= box["left"] + box["width"] + TOL
            and r["top"] + r["height"] <= box["top"] + box["height"] + TOL)


def point_in(p, box):
    return (box["left"] - TOL <= p["x"] <= box["left"] + box["width"] + TOL
            and box["top"] - TOL <= p["y"] <= box["top"] + box["height"] + TOL)


def overlap(a, b):
    return not (a["left"] + a["width"] <= b["left"] or b["left"] + b["width"] <= a["left"]
                or a["top"] + a["height"] <= b["top"] or b["top"] + b["height"] <= a["top"])


def check_frame(p):
    errs = []
    if p["type"] != "step":
        return errs
    name = p["targetName"]
    if p["target"] is None:
        return [f"找不到錨點 data-demo=\"{name}\"（點完畫面換了，就用 after 指定下一個要看的地方）"]
    if p["spotlight"] is None:
        errs.append("這一步沒有 spotlight")
    else:
        if p.get("targetClipped"):
            errs.append(f"目標 {name} 被捲動容器切掉一部分，觀眾看不完整（調整 render 的捲動位置或版面）")
        if not inside(p["target"], p["spotlight"]):
            errs.append(f"目標 {name} 沒有完整落在 spotlight 裡")
        if p["cursor"] and not point_in(p["cursor"], p["spotlight"]):
            errs.append("游標在 spotlight 外面（暗處）")
    if p["cursor"] is None:
        errs.append("這一步沒有游標")
    else:
        st = {"left": 0, "top": 0, "width": p["stage"]["width"], "height": p["stage"]["height"]}
        if not point_in(p["cursor"], st):
            errs.append("游標跑出舞台")
    if p["caption"] and overlap(p["caption"], p["target"]):
        errs.append(f"旁白蓋住了目標 {name}")
    return errs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--out", type=Path, help="截圖資料夾（預設：HTML 旁邊的 <檔名>-shots/）")
    ap.add_argument("--browser", default="msedge", help="msedge（預設，借用系統 Edge）或 chromium")
    ap.add_argument("--dark", action="store_true", help="先切到深色模式再檢查（截圖預設存到 <檔名>-dark-shots/）")
    args = ap.parse_args()

    out = args.out or args.html.with_name(args.html.stem + ("-dark-shots" if args.dark else "-shots"))
    out.mkdir(parents=True, exist_ok=True)
    url = args.html.resolve().as_uri()
    failures = []
    count = 0

    with sync_playwright() as pw:
        launch = {"channel": "msedge"} if args.browser == "msedge" else {}
        browser = pw.chromium.launch(**launch)
        for w, h in SIZES:
            page = browser.new_page(viewport={"width": w, "height": h})
            js_errors = []
            page.on("pageerror", lambda e: js_errors.append(str(e)))
            page.goto(url)
            page.wait_for_load_state("load")
            if not page.evaluate("!!window.__scriptedDemo"):
                failures.append(f"[{w}x{h}] 找不到 window.__scriptedDemo，demo 沒有用 player.js 的 ScriptedDemo.create 建立")
                break
            # 先固定在淺色：頁面若用 create({ theme: 'dark' }) 預設深色，不加 --dark 時才真的檢查到淺色，
            # 加 --dark 時也才有淺色底色可以比對
            page.evaluate("window.__scriptedDemo.setTheme('light')")
            page.wait_for_timeout(300)
            if args.dark:
                # 頁面要依 <html data-sd-theme="dark"> 替舞台換配色；舞台底色沒變就是漏寫深色 CSS
                bg = "getComputedStyle(window.__scriptedDemo.stage).backgroundColor"
                light_bg = page.evaluate(bg)
                page.evaluate("window.__scriptedDemo.setTheme('dark')")
                page.wait_for_timeout(300)
                if page.evaluate("document.documentElement.getAttribute('data-sd-theme')") != "dark":
                    failures.append(f"[{w}x{h}] setTheme('dark') 之後，<html> 沒有 data-sd-theme=\"dark\"")
                if page.evaluate(bg) == light_bg:
                    failures.append(f"[{w}x{h}] 深色模式下舞台底色沒變：頁面 CSS 要寫 [data-sd-theme=\"dark\"] 的舞台配色")
            before = page.evaluate("JSON.stringify(window.__scriptedDemo.state)")
            count = page.evaluate("window.__scriptedDemo.frames.length")
            for i in range(count):
                page.evaluate("i => window.__scriptedDemo.goTo(i, {instant: true})", i)
                page.wait_for_timeout(80)
                p = page.evaluate("window.__scriptedDemo.probe()")
                page.screenshot(path=str(out / f"{w}x{h}-{i:03d}-{p['type']}.png"))
                for e in check_frame(p):
                    failures.append(f"[{w}x{h}] 第 {i} 格：{e}")

            # 換視窗大小後 spotlight 要跟著目標走
            steps = [i for i in range(count) if page.evaluate("i => window.__scriptedDemo.frames[i].type", i) == "step"]
            if steps:
                i = steps[len(steps) // 2]
                page.evaluate("i => window.__scriptedDemo.goTo(i, {instant: true})", i)
                page.set_viewport_size({"width": int(w * 0.8), "height": h})
                page.wait_for_timeout(300)
                p = page.evaluate("window.__scriptedDemo.probe()")
                if p["target"] and p["spotlight"] and not inside(p["target"], p["spotlight"]):
                    failures.append(f"[{w}x{h}] 第 {i} 格：視窗變窄後 spotlight 沒有跟著目標走")
                page.set_viewport_size({"width": w, "height": h})

            if (w, h) == SIZES[1]:
                r = page.evaluate(ANIMATED_PASS)
                for b in r["bad"]:
                    failures.append(f"[{w}x{h}] 動畫播放中第 {b['idx']} 格：{b['kind']}")
                if r["badCount"] > len(r["bad"]):
                    failures.append(f"[{w}x{h}] 動畫播放中還有 {r['badCount'] - len(r['bad'])} 次同類問題")
                if not r["end"]:
                    failures.append(f"[{w}x{h}] 連播途中切換配色後，導覽停在第 {r['idx']} 格，沒有播完")

            page.evaluate("window.__scriptedDemo.stop()")
            if page.evaluate("JSON.stringify(window.__scriptedDemo.state)") != before:
                failures.append(f"[{w}x{h}] 按停止後，狀態沒有回到導覽前")
            failures += [f"[{w}x{h}] JavaScript 錯誤：{e}" for e in js_errors]
            page.close()
        browser.close()

    print(json.dumps({"theme": "dark" if args.dark else "light", "frames_checked_per_size": count,
                      "sizes": [f"{w}x{h}" for w, h in SIZES], "screenshots": str(out),
                      "failures": failures}, ensure_ascii=False, indent=2))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
