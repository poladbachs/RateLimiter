import asyncio
from rate_limiters.binance import binance_limits
from rate_limiters.bybit import bybit_limits
from rate_limiter import RateLimiterGroup
import ccxt.async_support as ccxt_async

async def fetch_binance_info(rate_group):
    binance = ccxt_async.binance()
    for _ in range(10):  # Example: 10 API calls
        await rate_group.rate_limit(['binance_all'])
        data = await binance.public_get_exchangeinfo()
        print(f"Binance symbols fetched: {len(data['symbols'])}")
    await binance.close()

async def fetch_bybit_info(rate_group):
    bybit = ccxt_async.bybit()
    for _ in range(5):  # Example: 5 API calls
        await rate_group.rate_limit(['bybit_all'])
        data = await bybit.fetch_markets()
        print(f"Bybit symbols fetched: {len(data)}")
    await bybit.close()

async def main():
    rate_group = RateLimiterGroup(binance_limits() + bybit_limits())
    await asyncio.gather(fetch_binance_info(rate_group), fetch_bybit_info(rate_group))

if __name__ == "__main__":
    asyncio.run(main())
