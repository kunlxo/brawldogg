from pydantic import BaseModel, Field
from .player import PlayerIcon
from .constants import CLUB_ROLES, CLUB_TYPE


class ClubName(BaseModel):
    name: str


class ClubMember(BaseModel):
    tag: str
    name: str
    name_color: str = Field(alias="nameColor")
    trophies: int
    role: CLUB_ROLES
    icon: PlayerIcon


class Club(BaseModel):
    tag: str
    name: str
    description: str
    trophies: int
    required_trophies: int = Field(alias="requiredTrophies")
    members: list[ClubMember]
    type: CLUB_TYPE
    badge_id: int = Field(alias="badgeId")


class ClubMembers(BaseModel):
    members: list[ClubMember]
    paging: dict | None
