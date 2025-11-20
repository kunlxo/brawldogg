# BrawlDogg: Asynchronous Brawl Stars API Wrapper

BrawlDogg is a asynchronous Python wrapper for the official Brawl Stars API. It is designed for high-performance applications, featuring built-in resilience and strict data validation against API limitations.

## Key Features

  * **Asynchronous:** Built on `httpx` and `asyncio` for non-blocking operations.
  * **Resilient Request Handling:** Includes token rotation, exponential backoff, and retries for handling 403 (Access Denied) and 429 (Rate Limited) errors.
  * **Built-in Caching:** Implements a thread-safe TTL (Time-To-Live) and LRU (Least Recently Used) cache for frequently accessed static data.
  * **Rate Limiting:** Uses an Asynchronous Token Bucket algorithm to respect the API's request limits automatically.
  * **Structured Error Handling:** API errors are mapped to specific, catchable Python exceptions (e.g., `NotFound`, `RateLimited`).
  * **Modern Python & Models:** Uses `Pydantic` for strict data validation and type checking, ensuring reliable model objects.

---

## Installation

```bash
pip install brawldogg 
```

---

## Usage

### Basic Example

To get started, you'll need an API token from the [Supercell Developer website](https://developer.supercell.com/).

```python
import asyncio
from brawldogg.client import BrawlStarsClient
from brawldogg.exceptions import BadRequest, NotFound, RateLimited

API_TOKEN = "YOUR_API_TOKEN_HERE" 

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
```

---

## Configuration

The `BrawlStarsClient` inherits its core behavior from the `HTTPClient` and uses your custom error handling and constants.

| Parameter    | Type              | Default     | Description |
|--------------|-------------------|-------------|-------------|
| `token`      | `str` or `list[str]` | **Required** | Your API key(s). If a list is provided, tokens will be rotated on 403 or 429 errors. |
| `timeout`    | `float`           | `10.0`      | Request timeout in seconds. |
| `cache_ttl`  | `int`             | `60`        | Default time (seconds) to cache responses. |
| `max_retries`| `int`             | `3`         | Maximum number of attempts for a request (used for retrying on 429 and rotating tokens on 403). |


### API Endpoints

The following base URL and structured endpoints are used internally:

  * **Base URL:** `https://api.brawlstars.com/v1`
  * **Endpoints include:** `/players/{tag}`, `/clubs/{tag}/members`, `/events/rotation`, `/rankings/{country}/players`, etc.

---

## Structured Error Handling

All HTTP errors returned by the API are caught and re-raised as custom, descriptive exceptions, making error handling clean and reliable. All custom exceptions inherit from the base `HTTPException`.

| Status Code | Exception Class | Description |
| :--- | :--- | :--- |
| 400 | `BadRequest` | Client provided incorrect parameters. |
| 403 | `AccessDenied` | Missing/incorrect API credentials. Triggers token rotation/retry. |
| 404 | `NotFound` | Resource not found (e.g., player tag does not exist). |
| 429 | `RateLimited` | Request throttled by the server. Triggers backoff/retry. |
| 500 | `InternalServerError` | Unknown error on the Supercell server. |
| 503 | `Unavailable` | Service temporarily unavailable. |

---

## Data Models and Types

BrawlDogg utilizes Pydantic models to provide fully validated, type-hinted, and robust data structures for every API endpoint. This eliminates guesswork and ensures type safety.

### Key Data Structures

  * `Player`: Contains core player stats, including trophies, level, and victories.
  * `Club`: Details about a club, including trophies, requirements and members.
  * `BattleLogEntry`: Represents a single match. The `battle` field handles different match formats through type-safe Unions, such as `TeamBattle`, `SoloBattle`, `DuelBattle` and `BossBattle`.
  * `Brawler`: Provides static information (Star Powers, Gadgets) for all brawlers.
  * `PlayerRanking`: Global or local leaderaboard entries

### Attribute Naming Convention

All attributes are automatically converted from the API's camelCase (e.g. highestTrophies) and non-standard formats to idiomatic Pythonic snake_case.
