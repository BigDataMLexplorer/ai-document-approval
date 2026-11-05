from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    dashboard_out = artifacts / "review_dashboard.png"
    architecture_out = artifacts / "architecture_process.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto("http://127.0.0.1:8000/demo", wait_until="networkidle")
        page.click("#run")
        page.wait_for_function(
            "document.querySelector('#status').textContent.includes('needs_review')"
        )
        page.wait_for_timeout(500)
        page.screenshot(path=str(dashboard_out), full_page=True)

        diagram = browser.new_page(viewport={"width": 1440, "height": 900})
        diagram.goto("http://127.0.0.1:8000/architecture", wait_until="networkidle")
        diagram.screenshot(path=str(architecture_out), full_page=True)

        browser.close()

    print(f"Saved {dashboard_out}")
    print(f"Saved {architecture_out}")


if __name__ == "__main__":
    main()
