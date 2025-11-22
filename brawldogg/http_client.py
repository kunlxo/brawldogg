import asyncio
import logging
from typing import Any, Literal, Self

import httpx

from .constants import BASE_URL
from .exceptions import (
    AccessDenied,
    BadRequest,
    HTTPException,
    InternalServerError,
    NotFound,
    RateLimited,
    Unavailable,
)
from .utils.cache import TTLCache
from .utils.rate_limiter import RateLimiter

log = logging.getLogger("brawldogg.http")


class HTTPClient:
    """
    Core asynchronous HTTP client with token rotation, exponential backoff,
    TTL caching, and rate limiting.
    """

    def __init__(
        self,
        token: str | list[str],
        *,
        timeout: float = 10.0,
        cache_ttl: int = 60,
        max_retries: int = 3,
        session: httpx.AsyncClient | None = None,
        base_url: str = BASE_URL,
    ):
        self.tokens = [token] if isinstance(token, str) else token
        if not self.tokens:
            raise ValueError("At least one API token is required")

        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(timeout)
        self.max_retries = max_retries
        self.cache_ttl = cache_ttl

        self._session = session
        self._owned_session = session is None

        self.rate_limiter = RateLimiter()
        self.cache = TTLCache(default_ttl=cache_ttl)

        self._closed = False

    async def _get_session(self) -> httpx.AsyncClient:
        """Lazily create a session only if we own it."""
        if self._session is None:
            self._session = httpx.AsyncClient(
                timeout=self.timeout,
                event_hooks={"response": [self._handle_response_hook]},
            )
        return self._session

    async def _handle_response_hook(self, response: httpx.Response) -> None:
        """Global hook to raise exceptions and log request IDs."""
        request = response.request
        log.debug(f"← {request.method} {request.url} → {response.status_code}")

        if response.status_code < 400:
            return

        await response.aread()

        try:
            data = response.json()
        except Exception:
            reason = response.reason_phrase or "Unknown Error"
            message = response.text or "Could not parse error response body."
            raise HTTPException(response.status_code, reason, message)

        reason = data.get("reason", response.reason_phrase or "Unknown Error")
        message = data.get("message", data)

        match status_code := response.status_code:
            case 400:
                raise BadRequest(reason, message)
            case 403:
                raise AccessDenied(reason, message)
            case 404:
                raise NotFound(reason, message)
            case 429:
                raise RateLimited(reason, message)
            case 500:
                raise InternalServerError(reason, message)
            case 503:
                raise Unavailable(reason, message)
            case _:
                raise HTTPException(status_code, reason, message)

    def _generate_cache_key(
        self, method: str, url: str, params: dict[str, Any] | None
    ) -> str:
        """Generates a canonical, hashable cache key from request components."""
        params_items = frozenset((params or {}).items())
        return f"{method}:{url}:{hash(params_items)}"

    async def _request(
        self,
        method: Literal["GET"],
        endpoint: str,
        cache_ttl: int | None = None,
        *,
        params: dict[str, Any] | None = None,
        use_cache: bool = True,
    ) -> Any:
        if self._closed:
            raise RuntimeError("Client is closed")

        cache_ttl = cache_ttl if cache_ttl is not None else self.cache_ttl
        url = f"{self.base_url}{endpoint}"
        cache_key = self._generate_cache_key(method, url, params)

        # 1. Cache HIT
        if use_cache and cache_key in self.cache:
            log.debug(f"Cache HIT → {cache_key}")
            return self.cache[cache_key]

        # 2. Rate limiting (pre-request wait)
        await self.rate_limiter.acquire()

        attempt = 0
        last_exc: Exception | None = None

        for attempt in range(self.max_retries):
            # Token rotation logic
            token_index = attempt % len(self.tokens)
            token = self.tokens[token_index]
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

            try:
                session = await self._get_session()
                response = await session.request(
                    method, url, headers=headers, params=params
                )

                # The hook handles exceptions. If we reach here, status is < 400.
                data = response.json()

                # 3. Cache MISS - store
                if use_cache:
                    self.cache.set(cache_key, data, cache_ttl)
                    log.debug(f"Cache MISS → stored {cache_key}")
                return data

            except AccessDenied as e:
                last_exc = e
                log.warning(
                    f"Token rotation: Token index {token_index} invalid (403). Trying next token."
                )
                # No sleep, try the next token immediately

            except RateLimited as e:
                last_exc = e
                wait_time = 2**attempt  # Exponential backoff
                log.warning(
                    f"Rate limited (429). Backing off for {wait_time}s. Trying next token/retry."
                )
                await asyncio.sleep(wait_time)

            except HTTPException as e:
                # Catch non-retryable errors (400, 404, 500, etc.) and re-raise immediately.
                raise e

        # Final failure state
        if last_exc:
            raise last_exc

        raise HTTPException(500, "Unknown Error", "Request failed after all retries.")

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._owned_session and self._session:
            await self._session.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
