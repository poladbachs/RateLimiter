import asyncio
import json
import websockets
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

async def fetch_bybit_websocket(app):
    tracker = app['tracker']
    url = "wss://stream.bybit.com/v5/public/spot"
    params = {
        "op": "subscribe",
        "args": ["tickers.BTCUSDT"]
    }
    prices = []

    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(params))
        while True:
            message = await websocket.recv()
            data = json.loads(message)

            if "data" in data and isinstance(data["data"], list):
                price = float(data["data"][0]["lastPrice"])
                tracker.log_call(0)
                prices.append(price)

                # Update price aggregation
                app['price_aggregation']["average_bybit_ws"] = round(sum(prices) / len(prices), 2)
                app['price_aggregation']["max_bybit_ws"] = round(max(prices), 2)

                print(f"Bybit WebSocket - Price: {price}")

async def main():
    app = {
        "tracker": StatsTracker(),
        "price_aggregation": {
            "average_bybit_ws": 0.0,
            "max_bybit_ws": 0.0,
        },
    }

    await asyncio.gather(fetch_bybit_websocket(app), start_dashboard(app))

if __name__ == "__main__":
    asyncio.run(main())
