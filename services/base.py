from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Shared interface for future paid/free API connectors."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    @abstractmethod
    def fetch(self) -> dict[str, Any]:
        raise NotImplementedError
