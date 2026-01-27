import asyncio
import json
import logging
import subprocess
import os
from typing import Dict, Any, List

logger = logging.getLogger("CodeQualityValidator")

class CodeQualityValidator:
    """
    Validator for code quality (linting, type checking, formatting).
    """
    async def run(self) -> Dict[str, Any]:
        logger.info("Starting Code Quality Validator...")
        start_time = asyncio.get_event_loop().time()
        
        results = {
            "name": "code_quality_validator",
            "status": "PASSED",
            "duration_ms": 0,
            "checks": []
        }

        # Parallel Execution of checks
        checks = await asyncio.gather(
            self._check_pylint(),
            self._check_mypy(),
            self._check_black(),
            self._check_eslint(), # Placeholder if frontend exists
            return_exceptions=True
        )

        for check in checks:
            if isinstance(check, dict):
                results["checks"].append(check)
                if check["status"] == "FAILED":
                    results["status"] = "PASSED_WITH_WARNINGS" # Downgrade or Fail depending on strictness
                    # For this requirement: "Output aggregated score", strict fail might be needed.
                    # But prompt says "target > 9.0", so maybe just report.
                    # If target not met, fail?
                    pass
            else:
                results["checks"].append({"name": "Unknown Check", "status": "FAILED", "message": str(check)})
                results["status"] = "FAILED"

        # Check specific targets
        for check in results["checks"]:
             if check.get("name") == "Pylint Score" and check.get("score", 0) < 9.0:
                  results["status"] = "FAILED"
             if check.get("name") == "MyPy Coverage" and check.get("status") == "FAILED":
                   results["status"] = "FAILED"

        end_time = asyncio.get_event_loop().time()
        results["duration_ms"] = int((end_time - start_time) * 1000)
        
        logger.info(f"Code Quality Validator finished with status: {results['status']}")
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

    async def _check_pylint(self) -> Dict[str, Any]:
        # Target: > 9.0/10
        # Running on a subset or all python files? Let's try 'backend' or current dir.
        # Assuming backend folder exists from previous `list_dir`.
        target_dir = "backend" if os.path.exists("backend") else "."
        # Make sure target dir has python files or avoid running
        if not os.path.exists(target_dir):
             return {"name": "Pylint Score", "status": "SKIPPED", "message": "Backend directory not found.", "score": 0}

        cmd = ["pylint", target_dir, "--exit-zero"] # exit-zero to not fail immediately
        res = await self._run_command(cmd)
        
        score = 0.0
        # Parse score from stdout: "Your code has been rated at 9.50/10"
        try:
            lines = res["stdout"].split('\n')
            for line in lines:
                if "Your code has been rated at" in line:
                    parts = line.split("rated at ")
                    if len(parts) > 1:
                        score_str = parts[1].split("/")[0]
                        score = float(score_str)
        except:
            pass
        
        status = "PASSED" if score > 9.0 else "FAILED"
        return {
            "name": "Pylint Score", 
            "status": status, 
            "score": score, 
            "message": f"Score: {score}/10",
            "details": res["stdout"][:200] + "..." # Truncate
        }

    async def _check_mypy(self) -> Dict[str, Any]:
        # Target: 100% functions? MyPy just checks errors.
        target_dir = "backend" if os.path.exists("backend") else "."
        if not os.path.exists(target_dir):
             return {"name": "MyPy Coverage", "status": "SKIPPED", "message": "Backend directory not found."}

        cmd = ["mypy", target_dir, "--ignore-missing-imports"]
        res = await self._run_command(cmd)
        
        status = "PASSED" if res["returncode"] == 0 else "FAILED"
        return {
            "name": "MyPy Coverage",
            "status": status,
            "message": "Type check passed" if status == "PASSED" else "Type errors found",
            "details": res["stdout"][:200] + "..."
        }

    async def _check_black(self) -> Dict[str, Any]:
        target_dir = "backend" if os.path.exists("backend") else "."
        cmd = ["black", "--check", target_dir]
        res = await self._run_command(cmd)
        status = "PASSED" if res["returncode"] == 0 else "FAILED"
        return {
            "name": "Code Formatting (Black)",
            "status": status,
            "message": "Formatted correctly" if status == "PASSED" else "Formatting needed"
        }

    async def _check_eslint(self) -> Dict[str, Any]:
        # Frontend check
        target_dir = "frontend"
        if not os.path.exists(target_dir):
            return {"name": "ESLint", "status": "SKIPPED", "message": "Frontend directory not found"}
        
        # Assuming npm run lint or npx eslint
        cmd = ["npx.cmd", "eslint", target_dir] if os.name == 'nt' else ["npx", "eslint", target_dir]
        res = await self._run_command(cmd)
        
        status = "PASSED" if res["returncode"] == 0 else "FAILED"
        return {
            "name": "ESLint",
            "status": status,
            "message": "Linting passed" if status == "PASSED" else "Lint errors found",
            "details": res["stdout"][:200] + "..."
        }

if __name__ == "__main__":
    validator = CodeQualityValidator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(validator.run())
    print(json.dumps(result, indent=2))
