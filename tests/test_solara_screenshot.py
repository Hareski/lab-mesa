from __future__ import annotations

import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest


def start_solara(app_path: str, timeout: float = 45.0) -> tuple[subprocess.Popen, str]:
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "solara",
            "run",
            app_path,
            "--host",
            "127.0.0.1",
            "--port",
            "0",
            "--no-open",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    base_url: str | None = None
    deadline = time.time() + timeout

    while time.time() < deadline:
        if proc.poll() is not None:
            stdout, stderr = proc.communicate()
            raise RuntimeError(
                f"Solara server exited prematurely with code {proc.returncode}.\n"
                f"--- STDOUT ---\n{stdout}\n"
                f"--- STDERR ---\n{stderr}"
            )
        line = proc.stdout.readline() if proc.stdout else ""
        if line:
            match = re.search(r"http://[a-zA-Z0-9\.\:]+", line)
            if match:
                base_url = match.group(0)
                break
        time.sleep(0.1)

    if base_url is None:
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=5)
        raise TimeoutError(
            f"Timed out waiting for Solara to report listening URL.\n"
            f"--- STDOUT ---\n{stdout}\n"
            f"--- STDERR ---\n{stderr}"
        )

    last_err: Exception | None = None
    while time.time() < deadline:
        if proc.poll() is not None:
            stdout, stderr = proc.communicate()
            raise RuntimeError(
                f"Solara server terminated while waiting for ready status.\n"
                f"--- STDOUT ---\n{stdout}\n"
                f"--- STDERR ---\n{stderr}"
            )
        try:
            with urllib.request.urlopen(base_url, timeout=2.0) as resp:
                if resp.status in (200, 301, 302):
                    return proc, base_url
        except Exception as e:
            last_err = e
            time.sleep(0.5)

    proc.terminate()
    stdout, stderr = proc.communicate(timeout=5)
    raise TimeoutError(
        f"Timed out waiting for Solara server at {base_url}. Last error: {last_err}\n"
        f"--- STDOUT ---\n{stdout}\n"
        f"--- STDERR ---\n{stderr}"
    )


def test_solara_app_screenshot() -> None:
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    proc, base_url = start_solara("src/app.py", timeout=45.0)

    try:
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)
        screenshot_path = screenshots_dir / "solara_simulation.png"

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(base_url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)
            page.screenshot(path=str(screenshot_path))
            browser.close()

        assert screenshot_path.exists(), f"Screenshot not found at {screenshot_path}"
        assert screenshot_path.stat().st_size > 1000, (
            f"Screenshot unexpectedly small ({screenshot_path.stat().st_size}B)"
        )

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
