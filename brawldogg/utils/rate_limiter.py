import time
import asyncio


class RateLimiter:
    """
    Asynchronous Token Bucket Rate Limiter.
    """

    def __init__(self, rate: int = 20, per: float = 1.0):
        self.rate = rate  # Max tokens per 'per' period
        self.per = per  # Time period (e.g., 1.0 second)
        self.allowance = float(rate)  # Initial tokens
        self.last_check = time.time()
        self.lock = asyncio.Lock()
        self.refill_time = self.per / self.rate  # Time required to earn one token

    async def acquire(self):
        async with self.lock:
            current = time.time()
            time_passed = current - self.last_check
            self.last_check = current

            # 1. Refill allowance
            self.allowance += time_passed / self.refill_time

            # 2. Cap at maximum capacity
            if self.allowance > self.rate:
                self.allowance = float(self.rate)

            # 3. Check for consumption
            if self.allowance >= 1.0:
                # If we have enough, consume one token and exit
                self.allowance -= 1.0
            else:
                # If not enough, calculate wait time to earn the token

                # How many tokens we are short of (1.0 - allowance)
                tokens_needed = 1.0 - self.allowance

                # Time to wait to earn those tokens (tokens_needed * refill_time)
                wait_time = tokens_needed * self.refill_time

                # Log or debug here if needed
                # print(f"Insufficient tokens. Waiting for {wait_time:.3f}s")

                # Wait for the required time
                await asyncio.sleep(wait_time)

                # Since we waited exactly the time needed to earn the token,
                # the allowance is now 1.0, so we set it back to 0.
                self.allowance = 0.0
