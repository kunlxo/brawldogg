import logging
from typing import Any, Type, TypeVar

import httpx
from pydantic import BaseModel

from brawldogg.exceptions import BadRequest

from .constants import BASE_URL, ENDPOINTS
from .http_client import HTTPClient
from .models import (
    BattleLogEntry,
    Brawler,
    Club,
    ClubMember,
    ClubRanking,
    EventEntry,
    GameMode,
    PagingResponse,
    Player,
    PlayerRanking,
)
from .utils.tag_parser import normalize_tag

log = logging.getLogger("brawldogg")
T = TypeVar("T", bound=BaseModel)


class BrawlStarsClient(HTTPClient):
    """
    Async Brawl Stars API wrapper.

    Inherits all core features (async httpx, token rotation, caching,
    rate limiting, retries) from HTTPClient.
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
        super().__init__(
            token,
            timeout=timeout,
            cache_ttl=cache_ttl,
            max_retries=max_retries,
            session=session,
            base_url=base_url,
        )

    # ──────────────────────────────────────────────────────────────
    # Internal Fetchers (Refactored Logic)
    # ──────────────────────────────────────────────────────────────

    async def _fetch_single_endpoint(
        self,
        endpoint_key: str,
        model: Type[T],
        path_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
        cache_ttl: int | None = None,
    ) -> T:
        """Helper for fetching a single object (e.g., Player, Club)."""
        endpoint = ENDPOINTS[endpoint_key].format(**(path_params or {}))

        data = await self._request(
            "GET", endpoint, params=query_params, cache_ttl=cache_ttl
        )

        return model.model_validate(data)

    async def _fetch_paged_endpoint(
        self,
        endpoint_key: str,
        model: Type[T],
        path_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
        cache_ttl: int | None = None,
    ) -> PagingResponse[T]:
        """
        Helper for fetching a list of objects from a paginated endpoint.
        Returns the PagingResponse model, parameterized by the model.
        """
        endpoint = ENDPOINTS[endpoint_key].format(**(path_params or {}))

        data = await self._request(
            "GET", endpoint, params=query_params, cache_ttl=cache_ttl
        )

        return PagingResponse[model].model_validate(data)

    async def _fetch_list_endpoint(
        self,
        endpoint_key: str,
        model: Type[T],
        path_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
        cache_ttl: int | None = None,
    ) -> list[T]:
        """
        Helper for fetching a list of objects from an endpoint.
        """
        endpoint = ENDPOINTS[endpoint_key].format(**(path_params or {}))

        data = await self._request(
            "GET", endpoint, params=query_params, cache_ttl=cache_ttl
        )

        return [model.model_validate(item) for item in data]

    # ──────────────────────────────────────────────────────────────
    # Query helpers
    # ──────────────────────────────────────────────────────────────

    def _build_query_(
        self, limit: int, after: str | None = None, before: str | None = None
    ) -> dict[str, Any]:
        """
        Constructs a dictionary of API query parameters for pagination,
        excluding any parameters where the value is None.
        """
        query_params = {
            "limit": limit,
            "after": after,
            "before": before,
        }

        return {k: v for k, v in query_params.items() if v is not None}

    def _validate_query(self, query_params):
        if not query_params:
            return
        if query_params.get("before") and query_params.get("after"):
            raise BadRequest(
                reason="Incorrect query_params",
                message="Cannot specify both 'after' and 'before' pagination markers. Choose one or neither.",
            )

    # ──────────────────────────────────────────────────────────────
    # Public API Methods (Simplified)
    # ──────────────────────────────────────────────────────────────

    # Player Methods
    async def get_player(self, tag: str) -> Player:
        """Retrieve player information by tag."""
        tag = normalize_tag(tag)
        return await self._fetch_single_endpoint(
            "player", Player, path_params={"tag": tag}
        )

    async def get_player_battlelog(self, tag: str) -> PagingResponse[BattleLogEntry]:
        """Retrieve a player's recent battle log."""
        tag = normalize_tag(tag)
        return await self._fetch_paged_endpoint(
            "battlelog", BattleLogEntry, path_params={"tag": tag}
        )

    # Club Methods
    async def get_club(self, tag: str) -> Club:
        """Retrieve club information by tag."""
        tag = normalize_tag(tag)
        return await self._fetch_single_endpoint("club", Club, path_params={"tag": tag})

    async def get_club_members(
        self,
        tag: str,
        *,
        limit: int = 30,
        after: str | None = None,
        before: str | None = None,
    ) -> PagingResponse[ClubMember]:
        """Retrieve a club's members."""
        tag = normalize_tag(tag)
        query_params = self._build_query_(limit, after, before)
        self._validate_query(query_params)

        return await self._fetch_paged_endpoint(
            "club_members",
            ClubMember,
            path_params={"tag": tag},
            query_params=query_params,
        )

    # Global/Static Data Methods (High TTL)
    async def get_gamemodes(
        self,
        *,
        limit: int = 100,
        after: str | None = None,
        before: str | None = None,
    ) -> PagingResponse[GameMode]:
        """Retrieve a list of available game modes."""
        query_params = self._build_query_(limit, after, before)
        self._validate_query(query_params)

        return await self._fetch_paged_endpoint(
            "gamemodes", GameMode, query_params=query_params, cache_ttl=60 * 60 * 24
        )

    async def get_current_events(self) -> list[EventEntry]:
        """Retrieve the current events map rotation."""
        return await self._fetch_list_endpoint(
            "events",
            EventEntry,
            cache_ttl=60 * 60,
        )

    async def get_brawlers(
        self,
        *,
        limit: int = 100,
        after: str | None = None,
        before: str | None = None,
    ) -> PagingResponse[Brawler]:
        """Retrieve all brawlers."""
        query_params = self._build_query_(limit, after, before)
        self._validate_query(query_params)

        return await self._fetch_paged_endpoint(
            "brawlers", Brawler, query_params=query_params, cache_ttl=60 * 60 * 24
        )

    async def get_brawler(self, brawler_id: int) -> Brawler:
        """Retrieve information for a specific brawler by ID."""
        return await self._fetch_single_endpoint(
            "brawler", Brawler, path_params={"id": brawler_id}, cache_ttl=60 * 60 * 24
        )

    # Rankings Methods
    async def get_player_rankings(
        self,
        country: str = "global",
        *,
        limit: int = 200,
        after: str | None = None,
        before: str | None = None,
    ) -> PagingResponse[PlayerRanking]:
        """Retrieve player rankings for a country."""
        query_params = self._build_query_(limit, after, before)
        self._validate_query(query_params)

        return await self._fetch_paged_endpoint(
            "rankings_players",
            PlayerRanking,
            path_params={"country": country},
            query_params=query_params,
        )

    async def get_club_rankings(
        self,
        country: str = "global",
        *,
        limit: int = 200,
        after: str | None = None,
        before: str | None = None,
    ) -> PagingResponse[ClubRanking]:
        """Retrieve club rankings for a country."""
        query_params = self._build_query_(limit, after, before)
        self._validate_query(query_params)

        return await self._fetch_paged_endpoint(
            "rankings_clubs",
            ClubRanking,
            path_params={"country": country},
            query_params=query_params,
        )

    async def get_brawler_rankings(
        self,
        brawler_id: int,
        country: str = "global",
        *,
        limit: int = 200,
        after: str | None = None,
        before: str | None = None,
    ) -> PagingResponse[PlayerRanking]:
        """Retrieve brawler rankings for a specific brawler in a country."""
        query_params = self._build_query_(limit, after, before)
        self._validate_query(query_params)

        return await self._fetch_paged_endpoint(
            "rankings_brawlers",
            PlayerRanking,
            path_params={"country": country, "id": brawler_id},
            query_params=query_params,
        )
