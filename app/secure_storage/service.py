from __future__ import annotations

from typing import Protocol


class SecureStorageService(Protocol):
    def put_secret(self, name: str, value: str) -> str: ...

    def get_secret(self, reference: str) -> str: ...
