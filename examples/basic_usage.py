import asyncio

from brawldogg import BrawlStarsClient
from brawldogg.exceptions import BadRequest, NotFound, RateLimited

API_TOKEN = ""


async def main():
    # Use the client as an async context manager to ensure the session closes
    async with BrawlStarsClient(API_TOKEN) as bs:
        player_tag = "#2GCJ0UR02"

        try:
            # 1. Fetch Player Data
            player = await bs.get_player(player_tag)
            print(f"Name: {player.name} | Trophies: {player.trophies}")

            # 2. Fetch Battle Log
            battlelog = await bs.get_player_battlelog(player_tag)
            print(f"Last Battle Mode: {battlelog.items[0].battle.mode}")

            # 3. Fetch Club Members using paging
            if club := player.club:
                top3 = await bs.get_club_members(club.tag, limit=3)
                print(f"Top3 of the club {[member.name for member in top3.items]}")

                rest = await bs.get_club_members(
                    club.tag, after=top3.paging.cursors.after
                )
                print(f"The rest of the club {[member.name for member in rest.items]}")

        except BadRequest:
            print(
                "Error: Incorrect parameteres for the request. Make sure API_TOKEN is valid."
            )
        except NotFound:
            print(f"Error: Player {player_tag} not found.")
        except RateLimited:
            print(
                "Error: We were rate limited, but the client handled retries and backoff!"
            )


if __name__ == "__main__":
    asyncio.run(main())
