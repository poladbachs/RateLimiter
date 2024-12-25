# rate_limiter/rate_limiter_group.py
import copy
from .rate_limiter import RateLimiter
import threading

class RateLimiterGroup:
    def __init__(self, limits=[], wait_sec=0.1):
        self.limits = copy.deepcopy(limits)
        self.limiters = []
        for limit in limits:
            self.limiters.append(RateLimiter(
                period_sec=limit['period_sec'],
                count=limit['count'],
                wait_sec=wait_sec
            ))
        self.lock = threading.Lock()

    def rate_limit(self, tags=None, count=1):
        if not tags:
            return
        with self.lock:
            for i, limit in enumerate(self.limits):
                if limit['tag'] in tags:
                    for _ in range(count):
                        self.limiters[i].rate_limit()

    def status_info(self):
        return [{
            'tag': limit['tag'],
            'recent_count': limiter.recent_count()
        } for limit, limiter in zip(self.limits, self.limiters)]
