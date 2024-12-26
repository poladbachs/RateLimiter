import asyncio
import random
from aiohttp import web
from helpers import StatsTracker
import os

async def start_dashboard(app):
    async def handle_dashboard(request):
        return web.json_response({
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

async def simulate_trades(app, max_trades=10000, interval=0.001):
    tracker = app['tracker']
    prices = []

    for _ in range(max_trades):
        price = random.uniform(98000, 99000)
        tracker.log_call(0)
        prices.append(price)

        app['price_aggregation']["average_simulated"] = round(sum(prices) / len(prices), 2)
        app['price_aggregation']["max_simulated"] = round(max(prices), 2)

        print(f"Simulated Trade: {price}")
        await asyncio.sleep(interval)

async def main():
    app = {
        "tracker": StatsTracker(),
        "price_aggregation": {
            "average_simulated": 0.0,
            "max_simulated": 0.0,
        },
    }

    await asyncio.gather(simulate_trades(app), start_dashboard(app))

if __name__ == "__main__":
    asyncio.run(main())