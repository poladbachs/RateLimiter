import asyncio
import random
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
            "average_latency": round(sum(self.calls) / len(self.calls), 4),
            "max_latency": round(max(self.calls), 4),
        }

    def reset(self):
        """Reset all stored metrics."""
        self.calls = []

async def simulate_trades(app, max_trades=20000):
    """Simulate high-frequency trades."""
    tracker = app['tracker']
    prices = []
    rate_limiter = app['rate_limiter']
    semaphore = asyncio.Semaphore(500)

    async def rate_limit():
        current_time = asyncio.get_event_loop().time()
        rate_limiter['recent_calls'].append(current_time)
        while rate_limiter['recent_calls'] and rate_limiter['recent_calls'][0] < current_time - 1:
            rate_limiter['recent_calls'].popleft()
        if len(rate_limiter['recent_calls']) >= rate_limiter['max_limit']:
            await asyncio.sleep(0.001)

    async def trade_simulation(call_id):
        async with semaphore:
            await rate_limit()
            latency = random.uniform(0.0005, 0.002)
            await asyncio.sleep(latency)

            price = random.uniform(98000, 99000)
            tracker.log_call(latency)
            prices.append(price)

            app['price_aggregation']["average_BTC_price"] = round(sum(prices) / len(prices), 2)
            app['price_aggregation']["max_BTC_price"] = round(max(prices), 2)

            print(f"Simulated Trade {call_id}: Price={price}, Latency={latency:.4f}s")

    tasks = [trade_simulation(i + 1) for i in range(max_trades)]
    await asyncio.gather(*tasks)

    print("Simulation completed. Waiting for reset.")
    app['simulation_running'] = False
    app['simulation_ended'] = True

async def start_simulation(request):
    """API endpoint to start the simulation."""
    app = request.app
    if app['simulation_running']:
        return web.json_response({'status': 'error', 'message': 'Simulation is already running.'}, status=400)
    if app['simulation_ended']:
        return web.json_response({'status': 'error', 'message': 'Simulation ended. Please reset first.'}, status=400)

    app['simulation_running'] = True
    asyncio.create_task(simulate_trades(app))
    return web.json_response({'status': 'success', 'message': 'Simulation started.'})

async def reset_simulation(request):
    """API endpoint to reset the simulation."""
    app = request.app
    if app['simulation_running']:
        return web.json_response({'status': 'error', 'message': 'Simulation is still running.'}, status=400)

    app['tracker'].reset()
    app['price_aggregation'] = {
        "average_BTC_price": 0.0,
        "max_BTC_price": 0.0,
    }
    app['rate_limiter']['recent_calls'].clear()
    app['simulation_ended'] = False
    return web.json_response({'status': 'success', 'message': 'Simulation reset. You can start again.'})

async def create_app():
    """Create the aiohttp app with routes and shared state."""
    app = web.Application()

    app['tracker'] = StatsTracker()
    app['price_aggregation'] = {
        "average_BTC_price": 0.0,
        "max_BTC_price": 0.0,
    }
    app['rate_limiter'] = {
        "recent_calls": deque(),
        "max_limit": 10000,
    }
    app['simulation_running'] = False
    app['simulation_ended'] = False

    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

    async def handle_dashboard(request):
        return web.json_response({
            "rate_limits": {
                "current_rate": len(app['rate_limiter']['recent_calls']),
                "limit": app['rate_limiter']['max_limit']
            },
            "prices": app['price_aggregation'],
            "call_metrics": app['tracker'].get_aggregate_metrics(),
        })

    async def handle_index(request):
        index_file = os.path.join(static_folder, "index.html")
        if os.path.exists(index_file):
            return web.FileResponse(index_file)
        else:
            return web.Response(status=404, text="index.html not found")

    app.router.add_get("/dashboard", handle_dashboard)
    app.router.add_static("/static", path=static_folder, show_index=True)
    app.router.add_get("/", handle_index)
    app.router.add_post('/start-simulation', start_simulation)
    app.router.add_post('/reset-simulation', reset_simulation)

    return app

if __name__ == "__main__":
    web.run_app(create_app(), host='0.0.0.0', port=8080)
