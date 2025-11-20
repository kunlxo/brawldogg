from pydantic import BaseModel, Field


class Gadget(BaseModel):
    id: int
    name: str


class StarPower(BaseModel):
    id: int
    name: str


class GearStat(BaseModel):
    id: int
    name: str
    level: int


class Brawler(BaseModel):
    id: int
    name: str
    star_powers: list[StarPower] = Field(alias="starPowers")
    gadgets: list[Gadget]


class BrawlerStat(BaseModel):
    id: int
    name: str
    power: int
    rank: int
    trophies: int
    highest_trophies: int = Field(alias="highestTrophies")
    max_win_streak: int = Field(alias="maxWinStreak")
    current_win_streak: int = Field(alias="currentWinStreak")
    gears: list[GearStat] = Field(default_factory=list)
    gadgets: list[Gadget] = Field(default_factory=list)
    star_powers: list[StarPower] = Field(alias="starPowers", default_factory=list)
