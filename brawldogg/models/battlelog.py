from datetime import datetime

from pydantic import BaseModel, Field

from ..utils.validators import time_validator
from .constants import GAME_MODE
from .events import Event


class BattleBrawler(BaseModel):
    id: int
    name: str
    power: int
    trophies: int
    trophy_change: int | None = Field(alias="trophyChange", default=None)


class DuelPlayer(BaseModel):
    tag: str
    name: str
    brawlers: list[BattleBrawler]


class BattlePlayer(BaseModel):
    tag: str
    name: str
    brawler: BattleBrawler


class BossLevel(BaseModel):
    name: str
    id: int


class Battle(BaseModel):
    mode: GAME_MODE
    type: str
    trophy_change: int | None = Field(alias="trophyChange", default=None)


class TeamBattle(Battle):
    result: str
    duration: int
    star_player: BattlePlayer | None = Field(alias="starPlayer", default=None)
    teams: list[list[BattlePlayer]]


class SoloBattle(Battle):
    rank: int
    players: list[BattlePlayer]


class DuelBattle(Battle):
    result: str
    duration: int
    players: list[DuelPlayer]


class BossBattle(BaseModel):
    mode: GAME_MODE
    result: str
    players: list[BattlePlayer]
    level: BossLevel


class BattleLogEntry(BaseModel):
    battle_time: datetime = Field(alias="battleTime")
    event: Event
    battle: TeamBattle | SoloBattle | DuelBattle | BossBattle

    _validate_time = time_validator
