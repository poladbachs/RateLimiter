import asyncio

class Monitor:
    def __init__(self, rate_limiter_group, interval=2):
        self.rate_limiter_group = rate_limiter_group
        self.interval = interval
        self.running = False

    async def display_status(self):
        while self.running:
            limiter_status = self.rate_limiter_group.status_info()
            print("\n--- Rate Limiter Status ---")
            for tag, status in limiter_status.items():
                print(f"{tag}: {status['recent_count']} requests in current period")
            await asyncio.sleep(self.interval)

    async def start(self):
        self.running = True
        asyncio.create_task(self.display_status())

    async def stop(self):
        self.running = False
