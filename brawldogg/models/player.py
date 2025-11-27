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
    trophies_over_1000: int = 0

    @model_validator(mode="after")
    def compute_brawlers_stats(self):
        self.max_winstreak = WinStreak()
        self.current_winstreak = WinStreak()
        self.trophies_over_1000 = 0

        for b in self.brawlers:
            # MAX WINSTREAK
            if b.max_win_streak > self.max_winstreak.winstreak:
                self.max_winstreak.winstreak = b.max_win_streak
                self.max_winstreak.brawler_id = b.id

            # CURRENT WINSTREAK
            if b.current_win_streak > self.current_winstreak.winstreak:
                self.current_winstreak.winstreak = b.current_win_streak
                self.current_winstreak.brawler_id = b.id

            # TROPHIES > 1000
            if b.trophies > 1000:
                self.trophies_over_1000 += b.trophies - 1000

        return self
