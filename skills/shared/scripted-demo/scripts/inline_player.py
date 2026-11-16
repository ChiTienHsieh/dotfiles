"""把 demo HTML 裡引用 player.js 的那行換成播放器全文，產出單一檔案的成品。

播放器只有一份正本：本 skill 的 assets/player.js。HTML 裡的
<script src="...player.js"></script> 只是標記「播放器放這裡」，路徑寫什麼都不影響結果。

用法：
    python inline_player.py demo.src.html                # 輸出 demo.html（去掉 .src）或 demo.standalone.html
    python inline_player.py demo.src.html -o out.html
"""
import argparse
import re
import sys
from pathlib import Path

PLAYER = Path(__file__).resolve().parent.parent / "assets" / "player.js"
TAG = re.compile(r'<script\s+src="[^"]*player\.js"\s*>\s*</script>', re.IGNORECASE)


def default_output(src: Path) -> Path:
    stem = src.name[: -len(".src.html")] if src.name.endswith(".src.html") else src.stem + ".standalone"
    return src.with_name(stem + ".html")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    html = args.html.read_text(encoding="utf-8")
    tags = TAG.findall(html)
    if len(tags) != 1:
        sys.exit(f"停止：預期剛好 1 行 <script src=\"...player.js\"></script>，找到 {len(tags)} 行。")
    # 播放器裡若出現 </script 會提早結束 script 區塊，先跳脫
    js = PLAYER.read_text(encoding="utf-8").replace("</script", "<\\/script")
    out = TAG.sub(lambda _: "<script>\n" + js + "\n</script>", html)

    dest = args.output or default_output(args.html)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    print(dest)


if __name__ == "__main__":
    main()
