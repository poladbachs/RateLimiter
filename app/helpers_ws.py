import time

class StatsTracker:
    def __init__(self):
        self.total_calls = 0
        self.allowed_calls = 0
        self.latencies = []

    def log_call(self, latency):
        self.total_calls += 1
        self.allowed_calls += 1
        self.latencies.append(latency)

    def get_aggregate_metrics(self):
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        max_latency = max(self.latencies) if self.latencies else 0
        std_dev_latency = (sum((x - avg_latency) ** 2 for x in self.latencies) / len(self.latencies)) ** 0.5 if self.latencies else 0
        return {
            "total_calls": self.total_calls,
            "allowed_calls": self.allowed_calls,
            "average_latency": f"{avg_latency:.3f}s",
            "max_latency": f"{max_latency:.3f}s",
            "latency_std_dev": f"{std_dev_latency:.3f}s"
        }
