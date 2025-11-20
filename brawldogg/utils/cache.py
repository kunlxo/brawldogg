from collections import OrderedDict
from time import time
from typing import Any
from threading import Lock


class TTLCache:
    def __init__(self, default_ttl: int = 60, maxsize: int | None = None):
        self.cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self.default_ttl = default_ttl
        self.maxsize = maxsize
        self._lock = Lock()

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def set(self, key: str, value: Any, ttl: int | None = None):
        self.__setitem__(key, value, ttl)

    def _is_expired(self, key: str, expiry: float) -> bool:
        if time() > expiry:
            del self.cache[key]
            return True
        return False

    def __contains__(self, key: str) -> bool:
        with self._lock:
            if key not in self.cache:
                return False

            _, expiry = self.cache[key]
            return not self._is_expired(key, expiry)

    def __getitem__(self, key: str) -> Any:
        with self._lock:
            value, expiry = self.cache[key]

            if self._is_expired(key, expiry):
                raise KeyError(key)

            self.cache.move_to_end(key)
            return value

    def __setitem__(self, key: str, value: Any, ttl: int | None = None):
        with self._lock:
            ttl = ttl or self.default_ttl
            self.cache[key] = (value, time() + ttl)
            self.cache.move_to_end(key)
            if self.maxsize is not None and len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

    def __delitem__(self, key: str):
        with self._lock:
            del self.cache[key]

    def __len__(self) -> int:
        with self._lock:
            return len(self.cache)
