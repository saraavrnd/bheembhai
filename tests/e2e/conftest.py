from __future__ import annotations

import subprocess
import sys
import time
from collections.abc import Iterator
from urllib.error import URLError
from urllib.request import urlopen

import pytest


@pytest.fixture(scope="session")
def running_server() -> Iterator[str]:
    port = 8010
    base_url = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    deadline = time.monotonic() + 30
    try:
        while time.monotonic() < deadline:
            try:
                with urlopen(f"{base_url}/health", timeout=1) as response:
                    if response.status == 200:
                        break
            except URLError:
                time.sleep(0.2)
        else:
            raise RuntimeError("uvicorn walking skeleton did not start in time")

        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
