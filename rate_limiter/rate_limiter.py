# rate_limiter/rate_limiter.py
import threading
import time

class RateLimiter:
    def __init__(self, period_sec, count, wait_sec=0.1):
        self.period_sec = period_sec
        self.count = count
        self.rate_limit_history = []
        self.lock = threading.Lock()
        self.wait_sec = wait_sec

    def rate_limit(self):
        while True:
            with self.lock:
                self.update_history()
                if len(self.rate_limit_history) < self.count:
                    self.rate_limit_history.append(time.time())
                    break
            time.sleep(self.wait_sec)

    def recent_count(self):
        with self.lock:
            self.update_history()
            return len(self.rate_limit_history)

    def update_history(self):
        now = time.time()
        cutoff = now - self.period_sec
        self.rate_limit_history = [timestamp for timestamp in self.rate_limit_history if timestamp > cutoff]
