import time
import collections
from typing import Dict

class MetricsCollector:
    def __init__(self):
        self.latencies = collections.defaultdict(list)
        self.counters = collections.defaultdict(int)
        self.start_time = time.time()

    def record_latency(self, operation: str, duration: float):
        self.latencies[operation].append(duration)

    def increment_counter(self, name: str):
        self.counters[name] += 1

    def get_report(self) -> Dict[str, Any]:
        report = {
            "uptime": time.time() - self.start_time,
            "counters": dict(self.counters),
            "latencies": {}
        }
        for op, times in self.latencies.items():
            if times:
                report["latencies"][op] = {
                    "avg": sum(times) / len(times),
                    "max": max(times),
                    "min": min(times),
                    "count": len(times)
                }
        return report
