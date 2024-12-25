import asyncio
import time
from collections import deque

class AsyncRateLimiter:
    def __init__(self, period_sec, max_calls):
        self.period_sec = period_sec
        self.max_calls = max_calls
        self.call_times = deque()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            current = time.time()
            while self.call_times and self.call_times[0] <= current - self.period_sec:
                self.call_times.popleft()
            if len(self.call_times) >= self.max_calls:
                sleep_time = self.period_sec - (current - self.call_times[0])
                await asyncio.sleep(sleep_time)
                self.call_times.popleft()
            self.call_times.append(time.time())

class RateLimiterGroup:
    def __init__(self, limits):
        self.limiters = {}
        for limit in limits:
            tag = limit['tag']
            period = limit['period_sec']
            count = limit['count']
            if tag not in self.limiters:
                self.limiters[tag] = AsyncRateLimiter(period, count)
            else:
                # For simplicity, we'll keep the existing limiter
                pass

    async def rate_limit(self, tags):
        tasks = [self.limiters[tag].acquire() for tag in tags if tag in self.limiters]
        if tasks:
            await asyncio.gather(*tasks)

    def status_info(self):
        info = {}
        for tag, limiter in self.limiters.items():
            info[tag] = {
                'recent_count': len(limiter.call_times)
            }
        return info
