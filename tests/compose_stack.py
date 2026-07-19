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
ENV_FILE = ROOT / ".env"
TEST_ENV_CONTENT = """\
BHEEMBHAI_APP_NAME=BheemBhai
BHEEMBHAI_ENVIRONMENT=test
BHEEMBHAI_APP_VERSION=0.1.0
BHEEMBHAI_SECRET_KEY=test-secret-key
BHEEMBHAI_PUBLIC_BASE_URL={base_url}
POSTGRES_DB=beembhai
POSTGRES_USER=beembhai
POSTGRES_PASSWORD=beembhai
DATABASE_URL=postgresql+psycopg://beembhai:beembhai@postgres:5432/beembhai
REDIS_URL=redis://redis:6379/0
RABBITMQ_DEFAULT_USER=beembhai
RABBITMQ_DEFAULT_PASS=beembhai
RABBITMQ_URL=amqp://beembhai:beembhai@rabbitmq:5672/
MINIO_ROOT_USER=beembhai
MINIO_ROOT_PASSWORD=beembhai-secret
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=beembhai
MINIO_SECRET_KEY=beembhai-secret
MINIO_SECURE_STORAGE_BUCKET=secure-storage
LANGFUSE_BASE_URL=http://langfuse-web:3000
LANGFUSE_PUBLIC_KEY=test
LANGFUSE_SECRET_KEY=test
LANGFUSE_NEXTAUTH_SECRET=test
LANGFUSE_POSTGRES_DB=langfuse
LANGFUSE_POSTGRES_USER=langfuse
LANGFUSE_POSTGRES_PASSWORD=langfuse-password
LANGFUSE_REDIS_PASSWORD=langfuse-redis-password
LANGFUSE_CLICKHOUSE_PASSWORD=clickhouse-password
LANGFUSE_MINIO_ROOT_USER=langfuse
LANGFUSE_MINIO_ROOT_PASSWORD=langfuse-secret
LANGFUSE_INIT_ORG_NAME=BheemBhai
LANGFUSE_INIT_PROJECT_NAME=BheemBhai
LANGFUSE_INIT_PROJECT_PUBLIC_KEY=test
LANGFUSE_INIT_PROJECT_SECRET_KEY=test
LANGFUSE_INIT_USER_EMAIL=admin@example.com
LANGFUSE_INIT_USER_NAME=BheemBhai
LANGFUSE_INIT_USER_PASSWORD=test-password
BREVO_API_KEY=test-brevo-key
BREVO_SENDER_EMAIL=no-reply@example.com
BREVO_SENDER_NAME=BheemBhai
EMAIL_PROVIDER=brevo
EMAIL_FROM_ADDRESS=no-reply@example.com
"""


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
def _ensure_compose_env_file(*, base_url: str) -> Iterator[None]:
    created_env_file = False
    if not ENV_FILE.exists():
        ENV_FILE.write_text(
            TEST_ENV_CONTENT.format(base_url=base_url),
            encoding="utf-8",
        )
        created_env_file = True

    try:
        yield
    finally:
        if created_env_file:
            ENV_FILE.unlink(missing_ok=True)


@contextmanager
def deployed_api_stack(
    *,
    base_url: str = "http://127.0.0.1:28010",
    project_name: str = "beembhai-test",
) -> Iterator[str]:
    env = os.environ.copy()
    env["BHEEMBHAI_ENVIRONMENT"] = "test"
    env["BHEEMBHAI_PUBLIC_BASE_URL"] = base_url
    env["BHEEMBHAI_SECRET_KEY"] = "test-secret-key"
    env["API_PORT"] = "28010"
    env["POSTGRES_PORT"] = "25432"
    env["RABBITMQ_PORT"] = "25672"
    env["RABBITMQ_MANAGEMENT_PORT"] = "25673"
    env["REDIS_PORT"] = "26379"
    env["MINIO_PORT"] = "29000"
    env["MINIO_CONSOLE_PORT"] = "29001"
    env["LANGFUSE_POSTGRES_PORT"] = "25433"
    env["LANGFUSE_REDIS_PORT"] = "26380"
    env["LANGFUSE_CLICKHOUSE_HTTP_PORT"] = "28124"
    env["LANGFUSE_CLICKHOUSE_NATIVE_PORT"] = "29002"
    env["LANGFUSE_MINIO_PORT"] = "29090"
    env["LANGFUSE_MINIO_CONSOLE_PORT"] = "29091"

    previous_test_database_url = os.environ.get("TEST_DATABASE_URL")
    os.environ["TEST_DATABASE_URL"] = "postgresql+psycopg://beembhai:beembhai@127.0.0.1:25432/beembhai"

    with _ensure_compose_env_file(base_url=base_url):
        try:
            up_command = _compose_command(
                "up",
                "--build",
                "-d",
                "--wait",
                "api",
                project_name=project_name,
            )
            subprocess.run(
                up_command,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                check=True,
            )
            _wait_for_health(base_url)

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
            if previous_test_database_url is None:
                os.environ.pop("TEST_DATABASE_URL", None)
            else:
                os.environ["TEST_DATABASE_URL"] = previous_test_database_url
