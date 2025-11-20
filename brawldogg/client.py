import logging
import httpx
from typing import TypeVar, Type, Any
from pydantic import BaseModel

from .http_client import HTTPClient
from .constants import ENDPOINTS, BASE_URL
from .utils.tag_parser import normalize_tag
from .models import (
    Player,
    Club,
    ClubMember,
    EventEntry,
    Brawler,
    PlayerRanking,
    ClubRanking,
    BattleLogEntry,
    GameMode,
)

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

    async def _fetch_list_endpoint(
        self,
        endpoint_key: str,
        model: Type[T],
        path_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
        cache_ttl: int | None = None,
        root_is_list: bool = False,
    ) -> list[T]:
        """
        Helper for fetching a list of objects from an endpoint.
        Assumes data is in data['items'] unless root_is_list is True.
        """
        endpoint = ENDPOINTS[endpoint_key].format(**(path_params or {}))
        data = await self._request(
            "GET", endpoint, params=query_params, cache_ttl=cache_ttl
        )

        items = data if root_is_list else data.get("items", [])
        return [model.model_validate(item) for item in items]

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

    async def get_player_battlelog(self, tag: str) -> list[BattleLogEntry]:
        """Retrieve a player's recent battle log."""
        tag = normalize_tag(tag)
        return await self._fetch_list_endpoint(
            "battlelog", BattleLogEntry, path_params={"tag": tag}
        )

    # Club Methods
    async def get_club(self, tag: str) -> Club:
        """Retrieve club information by tag."""
        tag = normalize_tag(tag)
        return await self._fetch_single_endpoint("club", Club, path_params={"tag": tag})

    async def get_club_members(self, tag: str, *, limit: int = 30) -> list[ClubMember]:
        """Retrieve a club's members."""
        tag = normalize_tag(tag)
        return await self._fetch_list_endpoint(
            "club_members",
            ClubMember,
            path_params={"tag": tag},
            query_params={"limit": limit},
        )

    # Global/Static Data Methods (High TTL)
    async def get_gamemodes(self, *, limit: int = 100) -> list[GameMode]:
        """Retrieve a list of available game modes."""
        return await self._fetch_list_endpoint(
            "gamemodes", GameMode, query_params={"limit": limit}, cache_ttl=60 * 60 * 24
        )

    async def get_current_events(self) -> list[EventEntry]:
        """Retrieve the current events map rotation."""
        return await self._fetch_list_endpoint(
            "events",
            EventEntry,
            cache_ttl=60 * 60,
            root_is_list=True,  # Note: This endpoint returns a list directly, not an 'items' object.
        )

    async def get_brawlers(self, *, limit: int = 100) -> list[Brawler]:
        """Retrieve all brawlers."""
        return await self._fetch_list_endpoint(
            "brawlers", Brawler, query_params={"limit": limit}, cache_ttl=60 * 60 * 24
        )

    async def get_brawler(self, brawler_id: int) -> Brawler:
        """Retrieve information for a specific brawler by ID."""
        return await self._fetch_single_endpoint(
            "brawler", Brawler, path_params={"id": brawler_id}, cache_ttl=60 * 60 * 24
        )

    # Rankings Methods
    async def get_player_rankings(
        self, country: str = "global", *, limit: int = 200
    ) -> list[PlayerRanking]:
        """Retrieve player rankings for a country."""
        return await self._fetch_list_endpoint(
            "rankings_players",
            PlayerRanking,
            path_params={"country": country},
            query_params={"limit": limit},
        )

    async def get_club_rankings(
        self, country: str = "global", *, limit: int = 200
    ) -> list[ClubRanking]:
        """Retrieve club rankings for a country."""
        return await self._fetch_list_endpoint(
            "rankings_clubs",
            ClubRanking,
            path_params={"country": country},
            query_params={"limit": limit},
        )

    async def get_brawler_rankings(
        self, brawler_id: int, country: str = "global", *, limit: int = 200
    ) -> list[PlayerRanking]:
        """Retrieve brawler rankings for a specific brawler in a country."""
        return await self._fetch_list_endpoint(
            "rankings_brawlers",
            PlayerRanking,
            path_params={"country": country, "id": brawler_id},
            query_params={"limit": limit},
        )
