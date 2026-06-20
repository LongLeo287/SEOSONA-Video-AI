import os
from playwright.sync_api import sync_playwright

def capture_screenshot(url: str, output_path: str, width: int = 1200, height: int = 800) -> str:
    """
    Captures a screenshot of the given URL using headless Playwright.
    Returns the absolute path to the saved screenshot, or empty string on failure.
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(url, wait_until="networkidle", timeout=15000)
            page.screenshot(path=output_path, full_page=False)
            browser.close()
        return os.path.abspath(output_path)
    except Exception as e:
        print(f"[Web Capture] Failed to capture {url}: {e}")
        return ""

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        capture_screenshot(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python web_capture.py <url> <output_path>")
