BASE_URL = "https://api.brawlstars.com/v1"

ENDPOINTS = {
    "player": "/players/{tag}",
    "battlelog": "/players/{tag}/battlelog",
    "club": "/clubs/{tag}",
    "club_members": "/clubs/{tag}/members",
    "gamemodes": "/gamemodes",
    "events": "/events/rotation",
    "brawlers": "/brawlers",
    "brawler": "/brawlers/{id}",
    "rankings_players": "/rankings/{country}/players",
    "rankings_clubs": "/rankings/{country}/clubs",
    "rankings_brawlers": "/rankings/{country}/brawlers/{id}",
}
