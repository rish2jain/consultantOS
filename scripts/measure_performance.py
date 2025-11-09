#!/usr/bin/env python3
"""
Performance Measurement Script for ConsultantOS

Measures:
- API response times (p50, p95, p99)
- Database query performance
- Cache hit rates
- Frontend bundle sizes
- Core Web Vitals (if browser available)

Usage:
    python scripts/measure_performance.py --baseline  # Create baseline
    python scripts/measure_performance.py --compare   # Compare to baseline
"""
import argparse
import asyncio
import json
import os
import statistics
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

try:
    import httpx
except ImportError:
    print("Installing httpx...")
    os.system("pip install httpx")
    import httpx


class PerformanceTester:
    """Performance measurement and benchmarking"""

    def __init__(self, api_url: str = "http://localhost:8080"):
        self.api_url = api_url
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "api_url": api_url,
            "api_performance": {},
            "cache_performance": {},
            "database_performance": {},
            "summary": {}
        }

    async def measure_api_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        num_requests: int = 10,
        data: Dict = None
    ) -> Dict[str, float]:
        """
        Measure API endpoint performance

        Returns percentiles: p50, p95, p99, min, max, mean
        """
        print(f"  Testing {method} {endpoint} ({num_requests} requests)...")

        latencies = []
        errors = 0

        async with httpx.AsyncClient() as client:
            for i in range(num_requests):
                try:
                    start = time.time()

                    if method == "GET":
                        response = await client.get(f"{self.api_url}{endpoint}", timeout=30.0)
                    elif method == "POST":
                        response = await client.post(
                            f"{self.api_url}{endpoint}",
                            json=data,
                            timeout=30.0
                        )

                    latency = (time.time() - start) * 1000  # ms

                    if response.status_code < 400:
                        latencies.append(latency)
                    else:
                        errors += 1
                        print(f"    Error: {response.status_code}")

                except Exception as e:
                    errors += 1
                    print(f"    Exception: {e}")

                # Rate limiting delay
                await asyncio.sleep(0.1)

        if not latencies:
            return {"error": "All requests failed"}

        latencies.sort()
        return {
            "requests": num_requests,
            "successful": len(latencies),
            "errors": errors,
            "min_ms": round(min(latencies), 2),
            "max_ms": round(max(latencies), 2),
            "mean_ms": round(statistics.mean(latencies), 2),
            "median_ms": round(statistics.median(latencies), 2),
            "p50_ms": round(latencies[int(len(latencies) * 0.50)], 2),
            "p95_ms": round(latencies[int(len(latencies) * 0.95)], 2),
            "p99_ms": round(latencies[min(int(len(latencies) * 0.99), len(latencies) - 1)], 2),
        }

    async def test_api_performance(self):
        """Test all API endpoints"""
        print("\n📊 Testing API Performance...")

        endpoints = {
            "health": ("/health", "GET", None),
            "list_reports": ("/reports?limit=10", "GET", None),
            "cache_stats": ("/metrics", "GET", None),
        }

        for name, (endpoint, method, data) in endpoints.items():
            try:
                stats = await self.measure_api_endpoint(endpoint, method, num_requests=10, data=data)
                self.results["api_performance"][name] = stats
                print(f"    ✓ {name}: {stats.get('p95_ms', 'N/A')}ms (p95)")
            except Exception as e:
                print(f"    ✗ {name}: {e}")
                self.results["api_performance"][name] = {"error": str(e)}

    async def test_cache_performance(self):
        """Test cache hit rates"""
        print("\n💾 Testing Cache Performance...")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/metrics", timeout=10.0)

                if response.status_code == 200:
                    data = response.json()
                    cache_stats = data.get("cache_stats", {})

                    self.results["cache_performance"] = {
                        "disk_cache_available": cache_stats.get("disk_cache", {}).get("available", False),
                        "disk_cache_size_mb": round(
                            cache_stats.get("disk_cache", {}).get("size", 0) / (1024 * 1024), 2
                        ),
                        "disk_cache_entries": cache_stats.get("disk_cache", {}).get("entries", 0),
                        "semantic_cache_available": cache_stats.get("semantic_cache", {}).get("available", False),
                        "semantic_cache_entries": cache_stats.get("semantic_cache", {}).get("entries", 0),
                    }

                    # Add performance metrics if available
                    perf = cache_stats.get("performance", {})
                    if perf:
                        self.results["cache_performance"]["hit_rate_percent"] = perf.get("hit_rate_percent", 0)
                        self.results["cache_performance"]["avg_latency_ms"] = perf.get("avg_latency_ms", 0)

                    print(f"    ✓ Disk cache: {cache_stats.get('disk_cache', {}).get('entries', 0)} entries")
                    print(f"    ✓ Semantic cache: {cache_stats.get('semantic_cache', {}).get('entries', 0)} entries")

                    if perf:
                        print(f"    ✓ Hit rate: {perf.get('hit_rate_percent', 0)}%")
                        print(f"    ✓ Avg latency: {perf.get('avg_latency_ms', 0)}ms")
                else:
                    print(f"    ✗ Failed to fetch cache stats: {response.status_code}")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.results["cache_performance"] = {"error": str(e)}

    def measure_frontend_bundle(self):
        """Measure frontend bundle sizes"""
        print("\n📦 Measuring Frontend Bundle Sizes...")

        frontend_dir = Path(__file__).parent.parent / "frontend"
        next_dir = frontend_dir / ".next"

        if not next_dir.exists():
            print("    ⚠️  Frontend not built. Run 'npm run build' first.")
            return

        # Measure build output
        build_stats = {}

        # App chunks
        app_dir = next_dir / "static" / "chunks" / "app"
        if app_dir.exists():
            total_size = sum(f.stat().st_size for f in app_dir.rglob("*.js"))
            build_stats["app_chunks_kb"] = round(total_size / 1024, 2)

        # Main chunks
        chunks_dir = next_dir / "static" / "chunks"
        if chunks_dir.exists():
            js_files = list(chunks_dir.glob("*.js"))
            total_size = sum(f.stat().st_size for f in js_files)
            build_stats["static_chunks_kb"] = round(total_size / 1024, 2)
            build_stats["num_chunks"] = len(js_files)

        self.results["frontend_bundle"] = build_stats

        for key, value in build_stats.items():
            print(f"    ✓ {key}: {value}")

    def generate_summary(self):
        """Generate performance summary"""
        print("\n📈 Generating Summary...")

        summary = {}

        # API summary
        api_perf = self.results.get("api_performance", {})
        if api_perf:
            p95_times = [stats.get("p95_ms") for stats in api_perf.values() if isinstance(stats, dict) and "p95_ms" in stats]
            if p95_times:
                summary["avg_api_p95_ms"] = round(statistics.mean(p95_times), 2)
                summary["max_api_p95_ms"] = round(max(p95_times), 2)

        # Cache summary
        cache_perf = self.results.get("cache_performance", {})
        if cache_perf and "hit_rate_percent" in cache_perf:
            summary["cache_hit_rate"] = cache_perf["hit_rate_percent"]

        # Bundle summary
        bundle = self.results.get("frontend_bundle", {})
        if bundle:
            summary["total_bundle_kb"] = bundle.get("app_chunks_kb", 0) + bundle.get("static_chunks_kb", 0)

        self.results["summary"] = summary

        for key, value in summary.items():
            print(f"    • {key}: {value}")

    def save_results(self, filename: str = "performance_results.json"):
        """Save results to JSON file"""
        output_dir = Path(__file__).parent.parent / "performance_reports"
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / filename

        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")
        return output_file

    def compare_to_baseline(self, baseline_file: str):
        """Compare current results to baseline"""
        print("\n🔍 Comparing to Baseline...")

        try:
            with open(baseline_file, "r") as f:
                baseline = json.load(f)

            # Compare API performance
            print("\n  API Performance Changes:")
            for endpoint, current_stats in self.results["api_performance"].items():
                if endpoint in baseline.get("api_performance", {}):
                    baseline_stats = baseline["api_performance"][endpoint]

                    if "p95_ms" in current_stats and "p95_ms" in baseline_stats:
                        current_p95 = current_stats["p95_ms"]
                        baseline_p95 = baseline_stats["p95_ms"]
                        change_pct = ((current_p95 - baseline_p95) / baseline_p95) * 100

                        emoji = "🚀" if change_pct < -10 else "⚠️" if change_pct > 10 else "✓"
                        print(f"    {emoji} {endpoint}: {baseline_p95}ms → {current_p95}ms ({change_pct:+.1f}%)")

            # Compare bundle size
            if "frontend_bundle" in self.results and "frontend_bundle" in baseline:
                current_total = self.results.get("summary", {}).get("total_bundle_kb", 0)
                baseline_total = baseline.get("summary", {}).get("total_bundle_kb", 0)

                if current_total and baseline_total:
                    change_pct = ((current_total - baseline_total) / baseline_total) * 100
                    emoji = "🚀" if change_pct < -10 else "⚠️" if change_pct > 10 else "✓"
                    print(f"\n  Bundle Size Change:")
                    print(f"    {emoji} {baseline_total}KB → {current_total}KB ({change_pct:+.1f}%)")

        except FileNotFoundError:
            print(f"  ✗ Baseline file not found: {baseline_file}")
        except Exception as e:
            print(f"  ✗ Error comparing to baseline: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Measure ConsultantOS performance")
    parser.add_argument("--api-url", default="http://localhost:8080", help="API URL")
    parser.add_argument("--baseline", action="store_true", help="Create baseline")
    parser.add_argument("--compare", action="store_true", help="Compare to baseline")
    parser.add_argument("--output", default="performance_results.json", help="Output filename")

    args = parser.parse_args()

    print("🚀 ConsultantOS Performance Measurement")
    print("=" * 50)

    tester = PerformanceTester(api_url=args.api_url)

    # Run tests
    await tester.test_api_performance()
    await tester.test_cache_performance()
    tester.measure_frontend_bundle()
    tester.generate_summary()

    # Save results
    if args.baseline:
        output_file = tester.save_results("baseline.json")
        print(f"\n✅ Baseline created: {output_file}")
    else:
        output_file = tester.save_results(args.output)

    # Compare to baseline if requested
    if args.compare:
        baseline_path = Path(__file__).parent.parent / "performance_reports" / "baseline.json"
        if baseline_path.exists():
            tester.compare_to_baseline(str(baseline_path))
        else:
            print("\n⚠️  No baseline found. Create one with --baseline flag.")

    print("\n" + "=" * 50)
    print("✅ Performance measurement complete!")


if __name__ == "__main__":
    asyncio.run(main())
