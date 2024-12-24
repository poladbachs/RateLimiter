import threading
import time

class RateLimiter:
    def __init__(self, period_sec=None, count=none, wait_sec=0.1):
        self.period_sec = period_sec
        self.count = count
        self.rate_limit_history = []
        self.lock = threading.Lock()
        self.wait_sec = wait_sec
    
    def rate_limit(self):
        while True:
            if self.recent_count < self.count:
                break
            time.sleep(self.wait_sec)

        with self.lock:
            self.rate_limit_history.append(time.time())
        
    