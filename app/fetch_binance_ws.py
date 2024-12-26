import asyncio
import websockets
import json
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

async def fetch_binance_websocket(app):
    tracker = app['tracker']
    url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
    prices = []

    async with websockets.connect(url) as websocket:
        print("Connected to Binance WebSocket.")
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                # Extract price
                price = float(data['p'])
                prices.append(price)
                tracker.log_call(0)  # Assume near-zero latency for WebSocket

                # Update price aggregation dynamically
                app['price_aggregation']["average_binance"] = round(sum(prices) / len(prices), 2)
                app['price_aggregation']["max_binance"] = round(max(prices), 2)

                print(f"Binance BTC Price: {price}")
            except Exception as e:
                print(f"WebSocket error: {str(e)}")
                break

async def main():
    app = {
        "tracker": StatsTracker(),
        "price_aggregation": {
            "average_binance": 0.0,
            "max_binance": 0.0,
        },
    }

    await asyncio.gather(fetch_binance_websocket(app), start_dashboard(app))

if __name__ == "__main__":
    asyncio.run(main())
