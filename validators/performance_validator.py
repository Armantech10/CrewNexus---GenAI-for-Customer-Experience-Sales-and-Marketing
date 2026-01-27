import asyncio
import json
import logging
import time
import httpx
import statistics
import os
import shutil
from typing import Dict, Any, List

logger = logging.getLogger("PerformanceValidator")

class PerformanceValidator:
    """
    Validator for performance (API response times, lighthouse).
    """
    async def run(self) -> Dict[str, Any]:
        logger.info("Starting Performance Validator...")
        start_time = asyncio.get_event_loop().time()
        
        results = {
            "name": "performance_validator",
            "status": "PASSED",
            "duration_ms": 0,
            "checks": []
        }

        # Checks
        results["checks"].append(await self._check_api_performance())
        results["checks"].append(await self._check_frontend_lighthouse())

        # Determine status
        for check in results["checks"]:
            if check["status"] == "FAILED":
                results["status"] = "PASSED_WITH_WARNINGS" # Downgrade
                # If critical thresholds missed
                if "P95" in check.get("message", "") and "API" in check["name"]:
                     results["status"] = "FAILED"
                if "Lighthouse" in check["name"] and check.get("score", 100) < 50:
                     results["status"] = "FAILED"

        end_time = asyncio.get_event_loop().time()
        results["duration_ms"] = int((end_time - start_time) * 1000)
        
        logger.info(f"Performance Validator finished with status: {results['status']}")
        return results

    async def _check_api_performance(self) -> Dict[str, Any]:
        """
        Simple load test: send N requests and measure latencies.
        """
        url = os.getenv("API_URL", "http://localhost:8000/health")
        latencies = []
        num_requests = 20
        concurrency = 5

        async def fetch(client):
            t0 = time.time()
            try:
                await client.get(url)
                t1 = time.time()
                return (t1 - t0) * 1000 # ms
            except:
                return None

        try:
            async with httpx.AsyncClient() as client:
                tasks = [fetch(client) for _ in range(num_requests)]
                # batching if needed, but 20 is small
                responses = await asyncio.gather(*tasks)
                latencies = [r for r in responses if r is not None]
        except Exception as e:
             return {"name": "API Latency", "status": "FAILED", "message": f"Load test failed: {e}"}

        if not latencies:
            return {"name": "API Latency", "status": "FAILED", "message": "All requests failed"}

        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
        # using max as proxy for p99/p95 if small sample
        
        # Targets: P50 < 500ms, P95 < 2000ms
        status = "PASSED"
        if p50 > 500: status = "FAILED"
        if p95 > 2000: status = "FAILED"

        return {
            "name": "API Response Time",
            "status": status,
            "metrics": {
                "p50_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "samples": len(latencies)
            },
            "message": f"P50: {round(p50)}ms, P95: {round(p95)}ms"
        }

    async def _check_frontend_lighthouse(self) -> Dict[str, Any]:
        """
        Run lighthouse via CLI if available.
        """
        if not shutil.which("lighthouse"):
            return {"name": "Lighthouse Performance", "status": "SKIPPED", "message": "Lighthouse CLI not found"}

        # Assuming frontend running at localhost:3000
        url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # lighthouse <url> --output json --quiet --chrome-flags="--headless"
        cmd = [
            "lighthouse", 
            url, 
            "--output=json", 
            "--quiet", 
            "--chrome-flags='--headless --no-sandbox'"
        ]
        
        # This might take time, ensure timeout handling in orchestrator
        try:
            process = await asyncio.create_subprocess_shell(
                " ".join(cmd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                 return {"name": "Lighthouse", "status": "FAILED", "message": "Lighthouse failed", "details": stderr.decode()}

            # Parse JSON output (stdout might contain logs, lighthouse usually writes to file or stdout)
            # With --output=json, it prints json to stdout.
            try:
                report = json.loads(stdout)
                categories = report.get("categories", {})
                perf_score = categories.get("performance", {}).get("score", 0) * 100
                access_score = categories.get("accessibility", {}).get("score", 0) * 100
                
                status = "PASSED"
                if perf_score < 90: status = "PASSED_WITH_WARNINGS"
                if perf_score < 50: status = "FAILED"

                return {
                    "name": "Lighthouse Scores",
                    "status": status,
                    "score": perf_score,
                    "metrics": {
                        "performance": perf_score,
                        "accessibility": access_score
                    },
                    "message": f"Perf: {perf_score}, Access: {access_score}"
                }
            except:
                 return {"name": "Lighthouse", "status": "FAILED", "message": "Could not parse Lighthouse JSON"}

        except Exception as e:
            return {"name": "Lighthouse", "status": "FAILED", "message": str(e)}

if __name__ == "__main__":
    validator = PerformanceValidator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(validator.run())
    print(json.dumps(result, indent=2))
