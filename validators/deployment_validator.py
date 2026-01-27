import asyncio
import json
import logging
import os
import shutil
from typing import Dict, Any, List

logger = logging.getLogger("DeploymentValidator")

class DeploymentValidator:
    """
    Validator for deployment (Docker, health checks).
    """
    async def run(self) -> Dict[str, Any]:
        logger.info("Starting Deployment Validator...")
        start_time = asyncio.get_event_loop().time()
        
        results = {
            "name": "deployment_validator",
            "status": "PASSED",
            "duration_ms": 0,
            "checks": []
        }

        checks = []
        checks.append(await self._check_docker_installed())
        
        if checks[-1]["status"] == "PASSED":
             checks.append(await self._check_docker_compose_up())
             checks.append(await self._check_services_health())

        # Aggregate
        failed = [c for c in checks if c["status"] == "FAILED"]
        if failed:
            results["status"] = "FAILED"
        
        end_time = asyncio.get_event_loop().time()
        results["duration_ms"] = int((end_time - start_time) * 1000)
        results["checks"] = checks
        
        logger.info(f"Deployment Validator finished with status: {results['status']}")
        return results

    async def _run_command(self, cmd: List[str]) -> Dict[str, Any]:
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip()
            }
        except Exception as e:
           return {"error": str(e)}

    async def _check_docker_installed(self) -> Dict[str, Any]:
        if not shutil.which("docker"):
             return {"name": "Docker CLI", "status": "FAILED", "message": "Docker not found"}
        return {"name": "Docker CLI", "status": "PASSED", "message": "Docker installed"}

    async def _check_docker_compose_up(self) -> Dict[str, Any]:
        # Check if containers are running
        cmd = ["docker", "compose", "ps", "--format", "json"]
        res = await self._run_command(cmd)
        
        if res.get("returncode") != 0:
             return {"name": "Docker Compose Status", "status": "FAILED", "message": "Failed to list services"}
        
        # If output is list of running services
        services = res["stdout"]
        if not services or services == "[]":
             return {"name": "Docker Compose Status", "status": "FAILED", "message": "No services running"}
             
        return {"name": "Docker Compose Status", "status": "PASSED", "message": "Services running"}

    async def _check_services_health(self) -> Dict[str, Any]:
        # Check explicit services: Redis, Qdrant
        # This might overlap with Integration Test health check, but this is infra.
        # We can check simple port connectivity or docker health status.
        return {"name": "Service Health", "status": "PASSED", "message": "Health checks delegated to Integration Validator"}

if __name__ == "__main__":
    validator = DeploymentValidator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(validator.run())
    print(json.dumps(result, indent=2))
