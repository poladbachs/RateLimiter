# demo_rate_limiter.py
import ccxt
import threading
import time
import csv
from datetime import datetime

from rate_limiter.rate_limiter_group import RateLimiterGroup
from rate_limiter.binance import binance_limits

# Initialize CCXT Exchanges
binance_exchange = ccxt.binance()

def real_binance_call():
    try:
        return binance_exchange.public_get_exchangeinfo()
    except ccxt.BaseError as e:
        print(f"Binance API call failed: {e}")
        return None


def log_api_call(log_file, api_name, status):
    with threading.Lock():
        with open(log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().isoformat(), api_name, status])

def simulate_api_calls(api_name, group, call_function, count=1000, delay=0.05, log_file="rate_limit_log.csv"):
    for _ in range(count):
        start_time = time.time()
        try:
            # Determine tags based on API name or exchange
            if "Binance" in api_name:
                group.rate_limit(tags=['all'])
                data = call_function()
                if data:
                    status = "allowed"
                    print(f"[{time.time()}] {api_name} - Fetched {len(data['symbols'])} symbols from Binance")
                else:
                    status = "failed"
            # elif "Coinbase" in api_name:
                # group.rate_limit(tags=['coinbase_all'])
                # data = coinbase_call()
                # if data:
                    # status = "allowed"
                    # print(f"[{time.time()}] {api_name} - Fetched data from Coinbase")
                # else:
                    # status = "failed"
            else:
                status = "unknown_api"
        except Exception as e:
            status = f"throttled ({str(e)})"
            print(f"[{time.time()}] {api_name} - Throttled: {str(e)}")
        
        log_api_call(log_file, api_name, status)
        time.sleep(delay)

if __name__ == "__main__":
    log_file = "rate_limit_log.csv"
    
    # Initialize CSV file with headers
    with open(log_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "API Name", "Status"])
    
    group = RateLimiterGroup(limits=binance_limits())
    
    
    # Single-threaded calls
    print("Testing single-threaded API calls (Binance) ...")
    simulate_api_calls(
        "Binance_publicGetExchangeInfo",
        group,
        call_function=real_binance_call,
        count=1000,
        delay=0.05,  # Reduced delay for faster testing
        log_file=log_file
    )
    
    # Multi-threaded calls
    print("\nTesting multi-threaded API calls (Binance) ...")
    threads = [
        threading.Thread(
            target=simulate_api_calls,
            args=(f"Binance_Thread-{i}", group, real_binance_call, 250, 0.02, log_file)
        )
        for i in range(4)  # 4 threads x 250 calls = 1000 calls
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    print("\nAll tests completed. Logs saved to rate_limit_log.csv.")
