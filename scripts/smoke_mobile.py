"""W3 acceptance smoke: load the site at a mobile viewport and verify the
acceptance criteria — <3 s load, no horizontal scroll, every nav section
switches, no console errors (finding-card 404s are expected until the user
adds site/img/figN.png).

Usage:  .venv/bin/python scripts/smoke_mobile.py   (serves site/ itself)
Requires: playwright installed (browsers cached) + site/data built.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PORT = 8091


def main() -> int:
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "-d", str(ROOT / "site")],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    failures = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(viewport={"width": 390, "height": 844},
                                      device_scale_factor=3, is_mobile=True)
            page = ctx.new_page()
            errors: list[str] = []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))

            t0 = time.time()
            page.goto(f"http://127.0.0.1:{PORT}/", wait_until="load")
            load_ms = (time.time() - t0) * 1000
            perf = page.evaluate("""() => {
                const t = performance.timing;
                return {
                  dom: t.domContentLoadedEventEnd - t.navigationStart,
                  bytes: Math.round(performance.getEntriesByType('resource')
                    .reduce((s, r) => s + (r.transferSize || 0), 0) / 1024),
                };
            }""")

            sw, iw = page.evaluate("() => [document.documentElement.scrollWidth, window.innerWidth]")
            print(f"mobile 390x844: load {load_ms:.0f} ms | DOM {perf['dom']} ms | {perf['bytes']} KB")
            if load_ms > 3000 or perf["dom"] > 3000:
                failures.append("load > 3 s")

            print(f"horizontal scroll: scrollWidth={sw} innerWidth={iw}")
            if sw > iw:
                failures.append("horizontal overflow")

            for section in ["map-section", "consents-section", "charts", "flow-section", "method", "findings"]:
                page.click(f"#sidenav a[data-section='{section}']")
                page.wait_for_timeout(350)
                visible = page.evaluate(f"!document.getElementById('{section}').hidden")
                print(f"  nav {section}: {'✓' if visible else '✗'}")
                if not visible:
                    failures.append(f"nav {section} failed")

            real_errors = [e for e in errors if "fig" not in e and "404" not in e]
            if real_errors:
                failures.append(f"console errors: {real_errors[:2]}")
            print(f"console errors (excl. pending fig images): {len(real_errors)}")
            browser.close()
    finally:
        server.terminate()

    print("RESULT:", "PASS" if not failures else f"FAIL {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
