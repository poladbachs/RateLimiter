import threading
import time

class RateLimiter:
    def __init__(self, period_sec=None, count=none, wait_sec=0.1):
        self.period_sec = period_sec
        self.count = count
        self.rate_limit_history = []
        self.lock = threading.Lock()
        self.wait_sec = wait_sec
    