from pydantic import BaseModel, Field, model_validator

from .brawler import BrawlerStat


class PlayerClub(BaseModel):
    tag: str
    name: str


class PlayerIcon(BaseModel):
    id: int


class WinStreak(BaseModel):
    winstreak: int = 0
    brawler_id: int | None = None


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
    victories_3vs3: int = Field(alias="victories3v3", validation_alias="3vs3Victories")
    solo_victories: int = Field(alias="soloVictories")
    duo_victories: int = Field(alias="duoVictories")
    best_robo_rumble_time: int = Field(alias="bestRoboRumbleTime")
    best_time_as_big_brawler: int = Field(alias="bestTimeAsBigBrawler")
    club: PlayerClub | None
    brawlers: list[BrawlerStat] = Field(default_factory=list)

    max_winstreak: WinStreak = Field(default_factory=WinStreak)
    current_winstreak: WinStreak = Field(default_factory=WinStreak)

    @model_validator(mode="after")
    def compute_winstreaks(self):
        max_winstreak = 0
        max_winstreak_id = None

        current_winstreak = 0
        current_winstreak_id = None

        for b in self.brawlers:
            max_winstreak = max(max_winstreak, b.max_win_streak)
            current_winstreak = max(current_winstreak, b.current_win_streak)
            if b.max_win_streak > max_winstreak:
                max_winstreak = b.max_win_streak
                max_winstreak_id = b.id

            if b.current_win_streak > current_winstreak:
                current_winstreak = b.current_win_streak
                current_winstreak_id = b.id

        self.max_winstreak = WinStreak(
            winstreak=max_winstreak, brawler_id=max_winstreak_id
        )
        self.current_winstreak = WinStreak(
            winstreak=current_winstreak, brawler_id=current_winstreak_id
        )
        return self
