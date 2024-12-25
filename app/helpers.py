import json
import os
from rate_limiter import RateLimiterGroup
import time

def load_rate_limits(config_path="rate_limits.json"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, config_path)
    with open(full_path, "r") as f:
        config = json.load(f)
    return config["binance"], config["bybit"]

def create_rate_limiter_group():
    binance_limits, bybit_limits = load_rate_limits()
    return RateLimiterGroup(binance_limits + bybit_limits)

class StatsTracker:
    def __init__(self):
        self.total_calls = 0
        self.allowed_calls = 0
        self.throttled_calls = 0
        self.latencies = []

    def log_call(self, latency, throttled=False):
        self.total_calls += 1
        self.latencies.append(latency)
        if throttled:
            self.throttled_calls += 1
        else:
            self.allowed_calls += 1

    def get_aggregate_metrics(self):
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        max_latency = max(self.latencies) if self.latencies else 0
        std_dev_latency = (sum((x - avg_latency) ** 2 for x in self.latencies) / len(self.latencies)) ** 0.5 if self.latencies else 0
        return {
            "total_calls": self.total_calls,
            "allowed_calls": self.allowed_calls,
            "throttled_calls": self.throttled_calls,
            "rate_limit_compliance": f"{(self.allowed_calls / self.total_calls) * 100:.2f}%" if self.total_calls > 0 else "0%",
            "average_latency": f"{avg_latency:.3f}s",
            "max_latency": f"{max_latency:.3f}s",
            "latency_std_dev": f"{std_dev_latency:.3f}s"
        }


import asyncio

async def fetch_binance_ticker(api_name, exchange, rate_limiter_group, tracker, app):
    async def fetch_call(call_id):
        await rate_limiter_group.rate_limit(["binance_all"])
        start_time = time.time()
        try:
            ticker = await exchange.fetch_ticker('BTC/USDT')
            latency = time.time() - start_time
            tracker.log_call(latency)
            price = ticker['last']
            app['call_logs'].append({"api": api_name, "latency": latency, "timestamp": time.time()})

            # Dynamically update price aggregation
            app['price_aggregation']["average_binance"] = round(
                (app['price_aggregation'].get("average_binance", 0) * (call_id - 1) + price) / call_id, 2
            )
            app['price_aggregation']["max_binance"] = max(app['price_aggregation'].get("max_binance", 0), price)

            print(f"{api_name} - Call {call_id} completed, price: {price}")
        except Exception as e:
            print(f"{api_name} - Call {call_id} failed: {str(e)}")

    await asyncio.gather(*[fetch_call(i + 1) for i in range(1000)])  # Run 100 calls concurrently


async def fetch_bybit_ticker(api_name, exchange, rate_limiter_group, tracker, app):
    async def fetch_call(call_id):
        await rate_limiter_group.rate_limit(["bybit_all"])
        start_time = time.time()
        try:
            ticker = await exchange.fetch_ticker('BTC/USDT')
            latency = time.time() - start_time
            tracker.log_call(latency)
            price = ticker['last']
            app['call_logs'].append({"api": api_name, "latency": latency, "timestamp": time.time()})

            # Dynamically update price aggregation
            app['price_aggregation']["average_bybit"] = round(
                (app['price_aggregation'].get("average_bybit", 0) * (call_id - 1) + price) / call_id, 2
            )
            app['price_aggregation']["max_bybit"] = max(app['price_aggregation'].get("max_bybit", 0), price)

            print(f"{api_name} - Call {call_id} completed, price: {price}")
        except Exception as e:
            print(f"{api_name} - Call {call_id} failed: {str(e)}")

    await asyncio.gather(*[fetch_call(i + 1) for i in range(1000)])  # Run 100 calls concurrently
