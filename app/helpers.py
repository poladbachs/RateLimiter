import asyncio
import json
from rate_limiter import RateLimiterGroup
from ccxt.async_support import binance, bybit
import time


import os

def load_rate_limits(config_path="rate_limits.json"):
    # Get the directory of the current file (helpers.py)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to rate_limits.json
    full_path = os.path.join(base_dir, config_path)

    with open(full_path, "r") as f:
        config = json.load(f)
    return config["binance"], config["bybit"]

def create_rate_limiter_group():
    from rate_limiter import RateLimiterGroup
    binance_limits, bybit_limits = load_rate_limits()
    return RateLimiterGroup(binance_limits + bybit_limits)

async def simulate_api_calls(exchange_name, rate_limiter_group, num_calls):
    exchange = binance() if exchange_name == "Binance" else bybit()

    for i in range(num_calls):
        start_time = time.time()

        if exchange_name == "Binance":
            await rate_limiter_group.rate_limit(["binance_all"])
            await exchange.fetch_ticker("BTC/USDT")  # Example: Fetch ticker data
        elif exchange_name == "Bybit":
            await rate_limiter_group.rate_limit(["bybit_all"])
            await exchange.fetch_order_book("BTC/USDT")  # Example: Fetch order book

        latency = time.time() - start_time
        print(f"{exchange_name} - Call {i + 1} completed in {latency:.4f} seconds")

    await exchange.close()