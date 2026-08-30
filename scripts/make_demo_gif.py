"""W3: record a ~15s demo GIF of the static site (docs/demo.gif).

Runs headless Chromium (playwright) against a local server and drives a short
scripted tour — landing → hover findings → charts → map (metric + panel
toggles) → water use → back. Converts the webm recording to a GIF with the
Playwright-managed ffmpeg binary.

Usage:  .venv/bin/python scripts/make_demo_gif.py   (serves site/ itself)
Requires: playwright installed (browsers cached), site/data built.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "docs" / "demo.gif"
PORT = 8099
FFMPEG = Path.home() / "Library/Caches/ms-playwright/ffmpeg-1011/ffmpeg-mac"

VIDEO_DIR = ROOT / ".tmp" / "demo-video"
FPS = 8         # output frames per second (webm → gif)
WIDTH = 560     # gif width (keep the file small enough for a README)
COLORS = 64     # palette size for the GIF


def serve() -> subprocess.Popen:
    import http.server
    import functools

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    proc = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "-d", str(SITE)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    return proc


def main() -> int:
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    server = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(
                viewport={"width": 1280, "height": 800},
                record_video_dir=str(VIDEO_DIR),
                record_video_size={"width": 1280, "height": 800},
            )
            page = ctx.new_page()
            page.goto(f"http://127.0.0.1:{PORT}/", wait_until="networkidle")
            page.wait_for_timeout(1500)

            # 1) landing: hover each finding card (hover-focus effect)
            for i in range(1, 4):
                page.hover(f".card:nth-child({i})")
                page.wait_for_timeout(1300)
            page.wait_for_timeout(800)

            # 2) jump to evidence (charts)
            page.click(".card[data-target='charts']")
            page.wait_for_timeout(2000)

            # 3) map: metric toggle + side panel toggle + hover rows
            page.click("#sidenav a[data-section='map-section']")
            page.wait_for_timeout(2500)  # tiles + invalidateSize
            page.click("#metric-buttons button[data-metric='percap']")
            page.wait_for_timeout(1300)
            page.click("#panel-toggle button[data-panel='sites']")
            page.wait_for_timeout(1300)
            page.hover("#flow-site-list .list-row:nth-child(1)")
            page.wait_for_timeout(1600)

            # 4) water consents
            page.click("#sidenav a[data-section='consents-section']")
            page.wait_for_timeout(2000)

            # 5) back to findings
            page.click("#sidenav a[data-section='findings']")
            page.wait_for_timeout(1500)

            video = page.video
            video_path = video.path()
            browser.close()
    finally:
        server.terminate()

    webm = str(video_path)
    if not os.path.exists(webm):
        print("no video recorded"); return 1

    # webm -> PNG frames (this Playwright ffmpeg build has no GIF/palette filters)
    frames_dir = VIDEO_DIR / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for f in frames_dir.glob("f_*.png"):
        f.unlink()
    subprocess.run([str(FFMPEG), "-y", "-i", webm, "-r", str(FPS), "-vf", f"scale={WIDTH}:-1",
                    str(frames_dir / "f_%04d.png")], check=True, capture_output=True)

    # PNG frames -> animated GIF (Pillow)
    from PIL import Image
    frames = sorted(frames_dir.glob("f_*.png"))
    imgs = [Image.open(f).convert("P", palette=Image.ADAPTIVE, colors=COLORS) for f in frames]
    imgs[0].save(OUT, save_all=True, append_images=imgs[1:],
                 duration=1000 // FPS, loop=0, optimize=True)
    size_kb = OUT.stat().st_size / 1024
    print(f"docs/demo.gif written: {size_kb:.0f} KB, {len(imgs)} frames @ {FPS} fps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
