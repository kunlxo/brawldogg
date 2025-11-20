from typing import Literal

CLUB_ROLES = Literal[
    "member", "senior", "vicePresident", "president", "notMember", "unknown"
]

CLUB_TYPE = Literal["open", "inviteOnly", "closed", "unknown"]

GAME_MODE = Literal[
    "soloShowdown",
    "duoShowdown",
    "heist",
    "bounty",
    "siege",
    "gemGrab",
    "brawlBall",
    "bigGame",
    "bossFight",
    "roboRumble",
    "takedown",
    "loneStar",
    "presentPlunder",
    "hotZone",
    "superCityRampage",
    "knockout",
    "volleyBrawl",
    "basketBrawl",
    "holdTheTrophy",
    "trophyThieves",
    "duels",
    "wipeout",
    "payload",
    "botDrop",
    "hunters",
    "lastStand",
    "snowtelThieves",
    "pumpkinPlunder",
    "trophyEscape",
    "wipeout5V5",
    "knockout5V5",
    "gemGrab5V5",
    "brawlBall5V5",
    "godzillaCitySmash",
    "paintBrawl",
    "trioShowdown",
    "zombiePlunder",
    "jellyfishing",
    "unknown",
]
