from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Optional


class DataCache:
    """Thread-safe in-memory cache for space weather and greyline data."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: dict[str, dict[str, Any]] = {}

    def set(self, key: str, data: Any) -> None:
        with self._lock:
            self._store[key] = {
                "data": data,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

    def get(self, key: str) -> Optional[dict[str, Any]]:
        with self._lock:
            return self._store.get(key)

    def get_all(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._store)


cache = DataCache()
