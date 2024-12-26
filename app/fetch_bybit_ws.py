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

async def fetch_bybit_websocket(app):
    tracker = app['tracker']
    url = "wss://stream.bybit.com/realtime_public"
    prices = []

    async with websockets.connect(url) as websocket:
        print("Connected to Bybit WebSocket.")

        # Subscribe to the BTC/USDT ticker channel
        subscription_message = json.dumps({
            "op": "subscribe",
            "args": ["trade.BTCUSDT"]
        })
        await websocket.send(subscription_message)

        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                if "data" in data:
                    for trade in data["data"]:
                        price = float(trade['price'])
                        prices.append(price)
                        tracker.log_call(0)  # Assume near-zero latency for WebSocket

                        # Update price aggregation dynamically
                        app['price_aggregation']["average_bybit"] = round(sum(prices) / len(prices), 2)
                        app['price_aggregation']["max_bybit"] = round(max(prices), 2)

                        print(f"Bybit Price: {price}")
            except Exception as e:
                print(f"WebSocket error: {str(e)}")
                break

async def main():
    app = {
        "tracker": StatsTracker(),
        "price_aggregation": {
            "average_bybit": 0.0,
            "max_bybit": 0.0,
        },
    }

    await asyncio.gather(fetch_bybit_websocket(app), start_dashboard(app))

if __name__ == "__main__":
    asyncio.run(main())
