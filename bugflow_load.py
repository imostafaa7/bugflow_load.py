#!/usr/bin/env python3
import argparse
import asyncio
import aiohttp
import time
import statistics
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Result:
    ok: int = 0
    fail: int = 0
    latencies: list = None

    def __post_init__(self):
        if self.latencies is None:
            self.latencies = []

class RateLimiter:
    def __init__(self, rps: float):
        self.interval = 1.0 / rps if rps > 0 else 0.0
        self.last = 0.0
        self.lock = asyncio.Lock()

    async def wait(self):
        async with self.lock:
            now = time.monotonic()
            delta = now - self.last
            if delta < self.interval:
                await asyncio.sleep(self.interval - delta)
            self.last = time.monotonic()

async def worker(name, session, target, limiter, end_at, stats, timeout):
    while time.monotonic() < end_at:
        await limiter.wait()
        t0 = time.perf_counter()
        try:
            async with session.get(target, timeout=timeout) as resp:
                await resp.read()
                dt = (time.perf_counter() - t0) * 1000
                stats.latencies.append(dt)
                if resp.status < 400:
                    stats.ok += 1
                else:
                    stats.fail += 1
        except Exception:
            stats.fail += 1

async def ramp_run(target, users, duration, rps, timeout):
    limiter = RateLimiter(rps)
    stats = Result()
    end_at = time.monotonic() + duration
    connector = aiohttp.TCPConnector(limit=users, ssl=False)
    timeout_cfg = aiohttp.ClientTimeout(total=timeout)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout_cfg) as session:
        tasks = [asyncio.create_task(worker(f"u{i}", session, target, limiter, end_at, stats, timeout_cfg)) for i in range(users)]
        await asyncio.gather(*tasks, return_exceptions=True)

    return stats

def summarize(stats):
    total = stats.ok + stats.fail
    if stats.latencies:
        avg = statistics.mean(stats.latencies)
        p95 = sorted(stats.latencies)[int(len(stats.latencies) * 0.95) - 1]
        mx = max(stats.latencies)
    else:
        avg = p95 = mx = 0.0
    fail_rate = (stats.fail / total * 100) if total else 0.0
    return {
        "total_requests": total,
        "success": stats.ok,
        "failed": stats.fail,
        "fail_rate_pct": round(fail_rate, 2),
        "avg_ms": round(avg, 2),
        "p95_ms": round(p95, 2),
        "max_ms": round(mx, 2),
    }

def save_report(outdir, data):
    outdir.mkdir(parents=True, exist_ok=True)
    md = outdir / "report.md"
    txt = outdir / "report.txt"
    csv = outdir / "results.csv"

    with md.open("w") as f:
        f.write("# BugFlow Load Test Report\n\n")
        for k, v in data.items():
            f.write(f"- **{k}**: {v}\n")

    with txt.open("w") as f:
        for k, v in data.items():
            f.write(f"{k}: {v}\n")

    with csv.open("w") as f:
        f.write("metric,value\n")
        for k, v in data.items():
            f.write(f"{k},{v}\n")

def main():
    p = argparse.ArgumentParser(description="Authorized load testing tool")
    p.add_argument("--target", required=True)
    p.add_argument("--users", type=int, default=10)
    p.add_argument("--duration", type=int, default=60)
    p.add_argument("--rps", type=float, default=5.0)
    p.add_argument("--timeout", type=float, default=10.0)
    p.add_argument("--out", default="results")
    args = p.parse_args()

    stats = asyncio.run(ramp_run(args.target, args.users, args.duration, args.rps, args.timeout))
    data = summarize(stats)
    save_report(Path(args.out), data)

    for k, v in data.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
