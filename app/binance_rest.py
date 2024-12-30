import asyncio
import aiohttp
from aiohttp import web
import os
from collections import deque

class StatsTracker:
    """Helper class to track API call statistics."""
    def __init__(self):
        self.calls = []

    def log_call(self, latency):
        self.calls.append(latency)

    def get_aggregate_metrics(self):
        if not self.calls:
            return {
                "total_calls": 0,
                "average_latency": 0.0,
                "max_latency": 0.0,
            }
        return {
            "total_calls": len(self.calls),
            "average_latency": round(sum(self.calls), 3),
            "max_latency": round(max(self.calls), 3),
        }

    def reset(self):
        """Reset all stored metrics."""
        self.calls = []

async def fetch_binance_rest(app, max_calls=1000):
    """Fetch data from Binance REST API."""
    tracker = app['tracker']
    rate_limiter = app['rate_limiter']
    semaphore = asyncio.Semaphore(500)
    call_count = 0

    async def rate_limit():
        current_time = asyncio.get_event_loop().time()
        rate_limiter['recent_calls'].append(current_time)
        while rate_limiter['recent_calls'] and rate_limiter['recent_calls'][0] < current_time - 1:
            rate_limiter['recent_calls'].popleft()
        if len(rate_limiter['recent_calls']) >= rate_limiter['max_limit']:
            await asyncio.sleep(0.001)

    async def fetch_data(call_id):
        nonlocal call_count  # Ensure call_count is modified in the outer scope
        async with semaphore:
            if call_count >= max_calls:
                return
            await rate_limit()
            async with aiohttp.ClientSession() as session:
                start_time = asyncio.get_event_loop().time()
                try:
                    async with session.get("https://api.binance.com/api/v3/ticker/price") as response:
                        if response.status == 200:
                            await response.json()
                            latency = asyncio.get_event_loop().time() - start_time
                            tracker.log_call(latency)
                            call_count += 1
                            print(f"REST Call {call_id}: Latency={latency:.3f}s")
                        elif response.status == 418:
                            print(f"REST Call {call_id}: Temporary Ban (418). Retrying...")
                            await asyncio.sleep(2)  # Wait before retrying
                        else:
                            print(f"REST Call {call_id}: Failed with status {response.status}")
                except aiohttp.ClientError as e:
                    print(f"REST Call {call_id}: Network error: {str(e)}")


    tasks = [fetch_data(i + 1) for i in range(max_calls)]
    await asyncio.gather(*tasks)

    app['fetch_running'] = False
    app['fetch_ended'] = True
    print("Fetching completed.")

async def start_fetch(request):
    """API endpoint to start the Binance REST fetch."""
    app = request.app
    if app['fetch_running']:
        return web.json_response({'status': 'error', 'message': 'Fetch already running.'}, status=400)
    if app['fetch_ended']:
        return web.json_response({'status': 'error', 'message': 'Fetch ended. Reset first.'}, status=400)

    app['fetch_running'] = True
    asyncio.create_task(fetch_binance_rest(app))
    return web.json_response({'status': 'success', 'message': 'Fetch started.'})

async def reset_fetch(request):
    """API endpoint to reset the fetch."""
    app = request.app
    if app['fetch_running']:
        return web.json_response({'status': 'error', 'message': 'Fetch is running.'}, status=400)

    app['tracker'].reset()
    app['rate_limiter']['recent_calls'].clear()
    app['fetch_ended'] = False
    return web.json_response({'status': 'success', 'message': 'Fetch reset.'})

async def create_app():
    """Create aiohttp app for Binance REST."""
    app = web.Application()
    app['tracker'] = StatsTracker()
    app['rate_limiter'] = {
        "recent_calls": deque(),
        "max_limit": 1100,
    }
    app['fetch_running'] = False
    app['fetch_ended'] = False

    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

    async def handle_dashboard(request):
        return web.json_response({
            "rate_limits": {
                "current_rate": len(app['rate_limiter']['recent_calls']),
                "limit": app['rate_limiter']['max_limit']
            },
            "call_metrics": app['tracker'].get_aggregate_metrics(),
        })

    async def handle_index(request):
        index_file = os.path.join(static_folder, "binance_rest.html")
        if os.path.exists(index_file):
            return web.FileResponse(index_file)
        return web.Response(status=404, text="binance_rest.html not found")

    app.router.add_get("/dashboard", handle_dashboard)
    app.router.add_static("/static", path=static_folder, show_index=True)
    app.router.add_get("/", handle_index)
    app.router.add_post('/start-fetch', start_fetch)
    app.router.add_post('/reset-fetch', reset_fetch)

    return app

if __name__ == "__main__":
    web.run_app(create_app(), host='0.0.0.0', port=8081)
