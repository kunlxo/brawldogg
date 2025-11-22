from pydantic import BaseModel, Field

from .club import ClubName
from .player import PlayerIcon


class RankingModel(BaseModel):
    tag: str
    name: str
    rank: int
    trophies: int


class PlayerRanking(RankingModel):
    name_color: str = Field(alias="nameColor")
    club: ClubName | None = None
    icon: PlayerIcon


class ClubRanking(RankingModel):
    member_count: int = Field(alias="memberCount")
    badge_id: int = Field(alias="badgeId")
