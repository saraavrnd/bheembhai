from __future__ import annotations

import os
import subprocess
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
COMPOSE_FILES = [ROOT / "docker-compose.yml", ROOT / "docker-compose.test.yml"]


def _compose_command(*args: str, project_name: str) -> list[str]:
    command = ["docker", "compose"]
    for compose_file in COMPOSE_FILES:
        command.extend(["-f", str(compose_file)])
    command.extend(["-p", project_name])
    command.extend(args)
    return command


def _wait_for_health(base_url: str, timeout_seconds: int = 120) -> None:
    deadline = time.monotonic() + timeout_seconds
    health_url = f"{base_url.rstrip('/')}/health"
    while time.monotonic() < deadline:
        try:
            with urlopen(health_url, timeout=1) as response:
                if response.status == 200:
                    return
        except URLError:
            time.sleep(0.5)
    raise RuntimeError(f"docker compose API did not become healthy at {health_url}")


@contextmanager
def deployed_api_stack(
    *,
    base_url: str = "http://127.0.0.1:8010",
    project_name: str = "beembhai-test",
) -> Iterator[str]:
    env = os.environ.copy()
    env["BEEBHAI_ENVIRONMENT"] = "test"
    env["BEEBHAI_PUBLIC_BASE_URL"] = base_url
    env["BEEBHAI_SECRET_KEY"] = "test-secret-key"

    up_command = _compose_command("up", "-d", "--wait", "api", project_name=project_name)
    subprocess.run(
        up_command,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        check=True,
    )
    _wait_for_health(base_url)

    try:
        yield base_url
    finally:
        down_command = _compose_command(
            "down",
            "-v",
            "--remove-orphans",
            project_name=project_name,
        )
        subprocess.run(
            down_command,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            check=False,
        )
