import time
import asyncio
import aiohttp
import statistics

async def benchmark_endpoint(url: str, count: int):
    latencies = []
    async with aiohttp.ClientSession() as session:
        for _ in range(count):
            start = time.time()
            try:
                async with session.get(url) as response:
                    await response.json()
                    latencies.append(time.time() - start)
            except Exception:
                pass
    
    if latencies:
        print(f"URL: {url}")
        print(f"  Avg Latency: {statistics.mean(latencies):.4f}s")
        print(f"  Max Latency: {max(latencies):.4f}s")
        print(f"  Throughput: {len(latencies)/sum(latencies):.2f} req/s")

if __name__ == "__main__":
    # Example usage (assuming nodes are running)
    # asyncio.run(benchmark_endpoint("http://localhost:8001/health", 100))
    pass
