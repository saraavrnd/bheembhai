from __future__ import annotations

from collections.abc import Iterator

import pytest


@pytest.fixture(scope="session")
def running_server(deployed_api: str) -> Iterator[str]:
    yield deployed_api
