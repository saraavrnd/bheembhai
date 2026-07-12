from __future__ import annotations

from typing import Protocol


class ObjectStorageService(Protocol):
    def put(self, key: str, content: bytes, content_type: str | None = None) -> str: ...

    def get(self, key: str) -> bytes: ...
