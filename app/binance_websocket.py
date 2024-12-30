import asyncio
import aiohttp
from aiohttp import web
import os
from collections import deque
import json

class StatsTracker:
    """Helper class to track WebSocket call statistics."""
    def __init__(self):
        self.messages = []
        self.connection_status = "Disconnected"

    def log_message(self, latency):
        self.messages.append(latency)

    def get_aggregate_metrics(self):
        if not self.messages:
            return {
                "total_messages": 0,
                "average_latency": 0.0,
                "max_latency": 0.0,
            }
        return {
            "total_messages": len(self.messages),
            "average_latency": round(sum(self.messages), 3),
            "max_latency": round(max(self.messages), 3),
        }

    def reset(self):
        """Reset all stored metrics."""
        self.messages = []
        self.connection_status = "Disconnected"

async def fetch_binance_ws(app, max_messages=1000):
    """Fetch data from Binance WebSocket API."""
    tracker = app['tracker']
    message_count = 0
    url = "wss://stream.binance.com:9443/ws/btcusdt@trade"

    async def connect_ws():
        nonlocal message_count
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(url) as ws:
                tracker.connection_status = "Connected"
                print("WebSocket connected.")
                async for msg in ws:
                    start_time = asyncio.get_event_loop().time()
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        latency = asyncio.get_event_loop().time() - start_time
                        tracker.log_message(latency)
                        message_count += 1
                        print(f"WebSocket Message {message_count}: Latency={latency:.3f}s")
                        if message_count >= max_messages:
                            await ws.close()
                            break
                    elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        break
                tracker.connection_status = "Disconnected"

    await connect_ws()
    app['fetch_running'] = False
    app['fetch_ended'] = True
    print("WebSocket fetching completed.")

async def start_fetch(request):
    """API endpoint to start the Binance WebSocket fetch."""
    app = request.app
    if app['fetch_running']:
        return web.json_response({'status': 'error', 'message': 'Fetch already running.'}, status=400)
    if app['fetch_ended']:
        return web.json_response({'status': 'error', 'message': 'Fetch ended. Reset first.'}, status=400)

    app['fetch_running'] = True
    asyncio.create_task(fetch_binance_ws(app))
    return web.json_response({'status': 'success', 'message': 'Fetch started.'})

async def reset_fetch(request):
    """API endpoint to reset the fetch."""
    app = request.app
    if app['fetch_running']:
        return web.json_response({'status': 'error', 'message': 'Fetch is running.'}, status=400)

    app['tracker'].reset()
    app['fetch_ended'] = False
    return web.json_response({'status': 'success', 'message': 'Fetch reset.'})

async def create_app():
    """Create aiohttp app for Binance WebSocket."""
    app = web.Application()
    app['tracker'] = StatsTracker()
    app['fetch_running'] = False
    app['fetch_ended'] = False

    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

    async def handle_dashboard(request):
        return web.json_response({
            "connection_status": app['tracker'].connection_status,
            "call_metrics": app['tracker'].get_aggregate_metrics(),
        })

    async def handle_index(request):
        index_file = os.path.join(static_folder, "binance_ws.html")
        if os.path.exists(index_file):
            return web.FileResponse(index_file)
        return web.Response(status=404, text="binance_ws.html not found")

    app.router.add_get("/dashboard", handle_dashboard)
    app.router.add_static("/static", path=static_folder, show_index=True)
    app.router.add_get("/", handle_index)
    app.router.add_post('/start-fetch', start_fetch)
    app.router.add_post('/reset-fetch', reset_fetch)

    return app

if __name__ == "__main__":
    web.run_app(create_app(), host='0.0.0.0', port=8082)
