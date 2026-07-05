from __future__ import annotations

import argparse
import json
import time
import urllib.request
from pathlib import Path
from typing import Dict, Any


ROOT = Path(__file__).resolve().parents[3]

LIVE_CAPTURE_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_live_captures"
DEFAULT_URL = "http://localhost:5173/frontend/pages/studio-v4.html"


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def check_url(url: str, timeout: int = 5) -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return {
                "ok": True,
                "status": response.status,
                "url": url,
            }
    except Exception as exc:
        return {
            "ok": False,
            "url": url,
            "error": str(exc),
        }


def launch_browser(p):
    try:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox"],
        )
        return browser, "playwright_chromium"
    except Exception as chromium_exc:
        try:
            browser = p.chromium.launch(
                channel="msedge",
                headless=True,
                args=["--disable-gpu", "--no-sandbox"],
            )
            return browser, "installed_msedge"
        except Exception as edge_exc:
            raise RuntimeError(
                "Could not launch Playwright Chromium or installed Microsoft Edge. "
                "Run: python -m playwright install chromium"
            ) from edge_exc


def capture_with_playwright(
    url: str,
    width: int,
    height: int,
    device_scale_factor: float,
    wait_ms: int,
) -> Dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise RuntimeError(
            "Playwright is not installed. Run: python -m pip install playwright"
        ) from exc

    LIVE_CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

    stamp = now_stamp()
    screenshot_path = LIVE_CAPTURE_DIR / f"live-ui-capture-{stamp}.png"
    report_path = LIVE_CAPTURE_DIR / f"live-ui-capture-{stamp}.json"

    with sync_playwright() as p:
        browser, launched_browser = launch_browser(p)

        context = browser.new_context(
            viewport={
                "width": width,
                "height": height,
            },
            device_scale_factor=device_scale_factor,
            is_mobile=True,
            has_touch=True,
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                "Mobile/15E148 Safari/604.1"
            ),
        )

        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(wait_ms)

        page.screenshot(
            path=str(screenshot_path),
            full_page=False,
        )

        browser.close()

    report = {
        "ok": True,
        "phase": "PIXEL-MAP-PERFECT-01",
        "created_at": stamp,
        "url": url,
        "browser": launched_browser,
        "viewport": {
            "width": width,
            "height": height,
            "device_scale_factor": device_scale_factor,
        },
        "screenshot_path": str(screenshot_path),
        "report_path": str(report_path),
        "rule": "This screenshot is the real rendered UI and must be used for live UI match auditing.",
        "next_step": "Compare this live screenshot against the golden reference image.",
    }

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture real live UI screenshot for Pixel UI audit.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--width", type=int, default=430)
    parser.add_argument("--height", type=int, default=932)
    parser.add_argument("--dpr", type=float, default=2)
    parser.add_argument("--wait-ms", type=int, default=1200)
    args = parser.parse_args()

    url_check = check_url(args.url)

    if not url_check["ok"]:
        output = {
            "ok": False,
            "phase": "PIXEL-MAP-PERFECT-01",
            "error": "Local frontend URL is not reachable.",
            "url_check": url_check,
            "fix": "Start the frontend server first: python -m http.server 5173",
        }

        print(json.dumps(output, indent=2))
        return 1

    report = capture_with_playwright(
        url=args.url,
        width=args.width,
        height=args.height,
        device_scale_factor=args.dpr,
        wait_ms=args.wait_ms,
    )

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
