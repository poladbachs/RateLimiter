import asyncio
from helpers import create_rate_limiter_group, fetch_binance_ticker, fetch_bybit_ticker, StatsTracker
from aiohttp import web
import os
import ccxt.async_support as ccxt

async def monitor_rate_limits(rate_limiter_group, app):
    while True:
        status = rate_limiter_group.status_info()
        app['status'] = status
        app['stats'] = app['tracker'].get_aggregate_metrics()
        print("\nRate Limits Status:")
        for tag, info in status.items():
            print(f"Tag: {tag}, Recent Count: {info['recent_count']}")
        await asyncio.sleep(5)

async def start_dashboard(app):
    async def handle_dashboard(request):
        return web.json_response({
            "rate_limits": app["status"],
            "prices": app["price_aggregation"],
            "call_metrics": app['stats']
        })

    async def handle_calls(request):
        return web.json_response(app["call_logs"])

    static_path = os.path.join(os.path.dirname(__file__), "static")
    app.router.add_get("/dashboard", handle_dashboard)
    app.router.add_get("/calls", handle_calls)
    app.router.add_static("/static", path=static_path, show_index=True)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()

async def main():
    tracker = StatsTracker()
    rate_limiter_group = create_rate_limiter_group()
    app = web.Application()
    app['status'] = {}
    app['tracker'] = tracker
    app['price_aggregation'] = {
        "average_binance": 0.0,
        "max_binance": 0.0,
        "average_bybit": 0.0,
        "max_bybit": 0.0,
    }
    app['call_logs'] = []

    binance = ccxt.binance()
    bybit = ccxt.bybit()

    try:
        await asyncio.gather(
            fetch_binance_ticker("Binance", binance, rate_limiter_group, tracker, app),
            fetch_bybit_ticker("Bybit", bybit, rate_limiter_group, tracker, app),
            monitor_rate_limits(rate_limiter_group, app),
            start_dashboard(app),
        )
    finally:
        await binance.close()
        await bybit.close()

if __name__ == "__main__":
    asyncio.run(main())
