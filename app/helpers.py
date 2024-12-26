import time
from collections import deque
import json
import os
import asyncio

# Stats Tracker for all three approaches
class StatsTracker:
    def __init__(self):
        self.total_calls = 0
        self.latencies = []

    def log_call(self, latency):
        self.total_calls += 1
        self.latencies.append(latency)

    def get_aggregate_metrics(self):
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        max_latency = max(self.latencies) if self.latencies else 0
        return {
            "total_calls": self.total_calls,
            "average_latency": f"{avg_latency:.3f}s",
            "max_latency": f"{max_latency:.3f}s",
        }


# Rate Limiter for REST APIs
class AsyncRateLimiter:
    def __init__(self, period_sec, max_calls):
        self.period_sec = period_sec
        self.max_calls = max_calls
        self.call_times = deque()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            current_time = time.time()
            while self.call_times and self.call_times[0] <= current_time - self.period_sec:
                self.call_times.popleft()
            if len(self.call_times) >= self.max_calls:
                sleep_time = self.period_sec - (current_time - self.call_times[0])
                await asyncio.sleep(sleep_time)
                self.call_times.popleft()
            self.call_times.append(time.time())


class RateLimiterGroup:
    def __init__(self, limits):
        self.limiters = {limit['tag']: AsyncRateLimiter(limit['period_sec'], limit['count']) for limit in limits}

    async def rate_limit(self, tags):
        tasks = [self.limiters[tag].acquire() for tag in tags if tag in self.limiters]
        if tasks:
            await asyncio.gather(*tasks)

    def status_info(self):
        return {tag: {'recent_count': len(limiter.call_times)} for tag, limiter in self.limiters.items()}


# Load rate limits from JSON
def load_rate_limits(config_path="rate_limits.json"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, config_path)
    with open(full_path, "r") as f:
        config = json.load(f)
    return config["binance"], config["bybit"]


# Create a RateLimiterGroup for REST APIs
def create_rate_limiter_group():
    binance_limits, bybit_limits = load_rate_limits()
    return RateLimiterGroup(binance_limits + bybit_limits)
