from pydantic import BaseModel, Field
from .brawler import BrawlerStat


class PlayerClub(BaseModel):
    tag: str
    name: str


class PlayerIcon(BaseModel):
    id: int


class Player(BaseModel):
    tag: str
    name: str
    name_color: str = Field(alias="nameColor")
    icon: PlayerIcon
    trophies: int
    highest_trophies: int = Field(alias="highestTrophies")
    exp_level: int = Field(alias="expLevel")
    exp_points: int = Field(alias="expPoints")
    is_qualified_from_championship_challenge: bool = Field(
        alias="isQualifiedFromChampionshipChallenge"
    )
    victories_3vs3: int = Field(alias="3vs3Victories")
    solo_victories: int = Field(alias="soloVictories")
    duo_victories: int = Field(alias="duoVictories")
    best_robo_rumble_time: int = Field(alias="bestRoboRumbleTime")
    best_time_as_big_brawler: int = Field(alias="bestTimeAsBigBrawler")
    club: PlayerClub | None
    brawlers: list[BrawlerStat] = Field(default_factory=list)
