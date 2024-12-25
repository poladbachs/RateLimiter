# demo_rate_limiter.py
import ccxt.async_support as ccxt_async
import asyncio
import csv
from datetime import datetime
import os
from aiolimiter import AsyncLimiter

binance_exchange = ccxt_async.binance()
bybit_exchange = ccxt_async.bybit()

binance_limiter = AsyncLimiter(max_rate=9, time_period=60)
bybit_limiter = AsyncLimiter(max_rate=5, time_period=60)

log_lock = asyncio.Lock()

async def log_api_call(log_file, api_name, status):
    async with log_lock:
        await asyncio.to_thread(
            lambda: open(log_file, mode='a', newline='').write(f"{datetime.now().isoformat()},{api_name},{status}\n")
        )

async def real_binance_call():
    try:
        return await binance_exchange.public_get_exchangeinfo()
    except ccxt_async.RateLimitExceeded as e:
        print(f"Binance API call throttled: {e}")
        return "throttled"
    except ccxt_async.BaseError as e:
        print(f"Binance API call failed: {e}")
        return "failed"

async def real_bybit_call():
    try:
        return await bybit_exchange.fetch_markets()
    except ccxt_async.RateLimitExceeded as e:
        print(f"Bybit API call throttled: {e}")
        return "throttled"
    except ccxt_async.BaseError as e:
        print(f"Bybit API call failed: {e}")
        return "failed"

async def simulate_api_calls(api_name, limiter, call_function, count=10, log_file="rate_limit_log.csv"):
    for i in range(count):
        try:
            await asyncio.wait_for(limiter.acquire(), timeout=0.1)
            data = await call_function()
            if data == "throttled":
                status = "throttled"
                print(f"[{datetime.now()}] {api_name} - Throttled")
            elif data == "failed":
                status = "failed"
                print(f"[{datetime.now()}] {api_name} - Failed")
            else:
                status = "allowed"
                if "Binance" in api_name:
                    symbols = data.get('symbols', [])
                    print(f"[{datetime.now()}] {api_name} - Fetched {len(symbols)} symbols from Binance")
                elif "Bybit" in api_name:
                    symbols = data
                    print(f"[{datetime.now()}] {api_name} - Fetched {len(symbols)} symbols from Bybit")
        except asyncio.TimeoutError:
            status = "throttled (timeout)"
            print(f"[{datetime.now()}] {api_name} - Throttled (timeout)")
        except Exception as e:
            status = f"failed ({str(e)})"
            print(f"[{datetime.now()}] {api_name} - Failed: {e}")
        
        await log_api_call(log_file, api_name, status)

async def main():
    log_file = "rate_limit_log.csv"
    
    if os.path.exists(log_file):
        os.remove(log_file)
    
    with open(log_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "API Name", "Status"])
    
    total_calls = 20
    concurrent_tasks = 4
    calls_per_task = total_calls // concurrent_tasks
    
    tasks = []
    for i in range(concurrent_tasks // 2):
        tasks.append(
            simulate_api_calls(f"Binance_Thread-{i}", binance_limiter, real_binance_call, calls_per_task, log_file)
        )
        tasks.append(
            simulate_api_calls(f"Bybit_Thread-{i}", bybit_limiter, real_bybit_call, calls_per_task, log_file)
        )
    
    await asyncio.gather(*tasks)
    
    print("\nAll tests completed. Logs saved to rate_limit_log.csv.")
    
    await binance_exchange.close()
    await bybit_exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
