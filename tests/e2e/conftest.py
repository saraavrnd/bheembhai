from __future__ import annotations

import os
import subprocess
import sys
import time
from collections.abc import Iterator
from urllib.error import URLError
from urllib.request import urlopen

import pytest


@pytest.fixture(scope="session")
def running_server(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    port = 8010
    base_url = f"http://127.0.0.1:{port}"
    database_path = tmp_path_factory.mktemp("e2e-db") / "beembhai.db"
    env = os.environ.copy()
    env["BEEBHAI_ENVIRONMENT"] = "test"
    env["DATABASE_URL"] = f"sqlite+pysqlite:///{database_path}"
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
        env=env,
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
