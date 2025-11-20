import asyncio
from brawldogg import BrawlStarsClient
from brawldogg.exceptions import BadRequest, NotFound, RateLimited

API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ5MTdmZjQ2LTliN2MtNGQyOC04MzAxLTc1OTBlMDU5MjZiZSIsImlhdCI6MTc2Mjk1NTYxMywic3ViIjoiZGV2ZWxvcGVyLzY4OTQ2ZGZlLTU4YzUtZmE0MS0yZDQzLTBjNDY4NGUwMWFiMCIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiODkuMTA3LjExLjM5Il0sInR5cGUiOiJjbGllbnQifV19.lxvvFFn8X90LPtu4yYXcCTPVSILDH8fs695XDHdkEJTvBvIsOWFVVGjttJkV9MRGArFu2T-RHLJLzNi2gP1oSw"

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
            print(f"Last Battle Mode: {battlelog[0].battle.mode}")

        except BadRequest:
            print(f"Error: Incorrect parameteres for the request. Make sure API_TOKEN is valid.")
        except NotFound:
            print(f"Error: Player {player_tag} not found.")
        except RateLimited:
            print("Error: We were rate limited, but the client handled retries and backoff!")

if __name__ == "__main__":
    asyncio.run(main())
