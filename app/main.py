import asyncio
from helpers import simulate_api_calls, create_rate_limiter_group

async def main_simulation(rate_limiter_group):
    while True:
        print("Starting Binance simulation...")
        await simulate_api_calls("Binance", rate_limiter_group, 1000)  # Simulating 1000 requests

        print("Starting Bybit simulation...")
        await simulate_api_calls("Bybit", rate_limiter_group, 800)  # Simulating 800 requests

        await asyncio.sleep(1)  # Short pause for burst simulation

async def monitor_rate_limits(rate_limiter_group):
    while True:
        print("\nRate Limits Status:")
        for tag, info in rate_limiter_group.status_info().items():
            print(f"Tag: {tag}, Recent Count: {info['recent_count']}")
        await asyncio.sleep(1)  # Refresh every second for HFT monitoring

async def main():
    rate_limiter_group = create_rate_limiter_group()

    await asyncio.gather(
        main_simulation(rate_limiter_group),
        monitor_rate_limits(rate_limiter_group),
    )

if __name__ == "__main__":
    asyncio.run(main())
