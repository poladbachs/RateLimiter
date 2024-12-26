import asyncio
import time
import ccxt.async_support as ccxt
from aiohttp import web
from helpers import StatsTracker, create_rate_limiter_group
import os

async def start_dashboard(app):
    async def handle_dashboard(request):
        return web.json_response({
            "rate_limits": app['rate_limiter'].status_info(),
            "prices": app['price_aggregation'],
            "call_metrics": app['tracker'].get_aggregate_metrics(),
        })

    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    dashboard_app = web.Application()
    dashboard_app.router.add_get("/dashboard", handle_dashboard)
    dashboard_app.router.add_static("/static", path=static_folder, show_index=True)
    runner = web.AppRunner(dashboard_app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()

async def fetch_bybit_ticker(app):
    tracker = app['tracker']
    rate_limiter_group = app['rate_limiter']
    bybit = ccxt.bybit()
    max_calls = 1000
    semaphore = asyncio.Semaphore(100)  # Adjust concurrency
    prices = []

    async def fetch_single_bybit(call_id):
        async with semaphore:
            await rate_limiter_group.rate_limit(["bybit_all"])
            start_time = time.time()
            try:
                ticker = await bybit.fetch_ticker('BTC/USDT')
                latency = time.time() - start_time
                tracker.log_call(latency)
                price = ticker['last']

                # Update price aggregation
                prices.append(price)
                app['price_aggregation']["average_bybit"] = round(sum(prices) / len(prices), 2)
                app['price_aggregation']["max_bybit"] = round(max(prices), 2)

                print(f"Bybit REST - Call {call_id} completed, price: {price}")
            except Exception as e:
                print(f"Bybit REST - Call {call_id} failed: {str(e)}")

    tasks = [fetch_single_bybit(i + 1) for i in range(max_calls)]
    await asyncio.gather(*tasks)

async def main():
    app = {
        "tracker": StatsTracker(),
        "rate_limiter": create_rate_limiter_group(),
        "call_logs": [],
        "price_aggregation": {
            "average_bybit": 0.0,
            "max_bybit": 0.0,
        },
    }

    await asyncio.gather(fetch_bybit_ticker(app), start_dashboard(app))

if __name__ == "__main__":
    asyncio.run(main())
