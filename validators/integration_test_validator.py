import asyncio
import json
import logging
import httpx
import os
from typing import Dict, Any, List

logger = logging.getLogger("IntegrationTestValidator")

class IntegrationTestValidator:
    """
    Validator for integration tests (API endpoints, workflows).
    """
    async def run(self) -> Dict[str, Any]:
        logger.info("Starting Integration Test Validator...")
        start_time = asyncio.get_event_loop().time()
        
        results = {
            "name": "integration_test_validator",
            "status": "PASSED",
            "duration_ms": 0,
            "checks": []
        }

        # Pre-check: Is server running?
        # User prompt implies this validator "tests API endpoints". 
        # The deployment validator checks if built/deployed.
        # Often integration tests run against a running instance.
        # I will assume localhost:8000 based on previous context ("curl localhost:8000/health").
        base_url = os.getenv("API_URL", "http://localhost:8000")

        checks = []
        
        # Check 1: Health
        checks.append(await self._check_endpoint(base_url, "/health"))
        
        # Check 2: API Docs (often available)
        checks.append(await self._check_endpoint(base_url, "/docs"))

        # Check 3: Run pytest integration suite if exists
        pytest_check = await self._run_integration_suite()
        checks.append(pytest_check)

        # Aggregate status
        failed = [c for c in checks if c["status"] == "FAILED"]
        if failed:
            results["status"] = "FAILED"
            results["errors"] = [c["message"] for c in failed]
        
        end_time = asyncio.get_event_loop().time()
        results["duration_ms"] = int((end_time - start_time) * 1000)
        results["checks"] = checks
        
        logger.info(f"Integration Validator finished with status: {results['status']}")
        return results

    async def _check_endpoint(self, base_url: str, path: str) -> Dict[str, Any]:
        url = f"{base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                if resp.status_code in [200, 201]:
                    return {"name": f"GET {path}", "status": "PASSED", "message": f"Status {resp.status_code}"}
                else:
                    return {"name": f"GET {path}", "status": "FAILED", "message": f"Status {resp.status_code}"}
        except Exception as e:
            return {"name": f"GET {path}", "status": "FAILED", "message": f"Connection error: {str(e)}"}

    async def _run_integration_suite(self) -> Dict[str, Any]:
        # If there is a tests/integration folder
        target = "tests/integration"
        if not os.path.exists(target):
             return {"name": "Integration Suite", "status": "SKIPPED", "message": "No integration tests found"}

        cmd = ["pytest", target]
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        
        status = "PASSED" if process.returncode == 0 else "FAILED"
        return {
            "name": "Integration Suite",
            "status": status,
            "message": "Tests passed" if status == "PASSED" else "Tests failed",
            "details": stdout.decode()[:200]
        }

if __name__ == "__main__":
    validator = IntegrationTestValidator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(validator.run())
    print(json.dumps(result, indent=2))
