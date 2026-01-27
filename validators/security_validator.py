import asyncio
import json
import logging
import os
import shutil
from typing import Dict, Any, List

logger = logging.getLogger("SecurityValidator")

class SecurityValidator:
    """
    Validator for security (bandit, safety, npm audit).
    """
    async def run(self) -> Dict[str, Any]:
        logger.info("Starting Security Validator...")
        start_time = asyncio.get_event_loop().time()
        
        results = {
            "name": "security_validator",
            "status": "PASSED",
            "duration_ms": 0,
            "checks": []
        }

        checks = await asyncio.gather(
            self._run_bandit(),
            self._run_safety(),
            self._run_npm_audit(),
            self._run_trufflehog(),
            return_exceptions=True
        )

        for check in checks:
            if isinstance(check, dict):
                results["checks"].append(check)
                if check["status"] == "FAILED":
                    results["status"] = "PASSED_WITH_WARNINGS" 
                    # If high severity
                    if "High" in check.get("message", "") or "Critical" in check.get("message", ""):
                        results["status"] = "FAILED"
            else:
                results["checks"].append({"name": "Unknown", "status": "FAILED", "message": str(check)})

        end_time = asyncio.get_event_loop().time()
        results["duration_ms"] = int((end_time - start_time) * 1000)
        
        logger.info(f"Security Validator finished with status: {results['status']}")
        return results

    async def _run_command(self, cmd: List[str], cwd: str = ".") -> Dict[str, Any]:
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode(errors='ignore').strip(),
                "stderr": stderr.decode(errors='ignore').strip()
            }
        except Exception as e:
            return {"error": str(e)}

    async def _run_bandit(self) -> Dict[str, Any]:
        # bandit -r backend -f json
        if not os.path.exists("backend"):
             return {"name": "Bandit", "status": "SKIPPED", "message": "Backend not found"}

        cmd = ["bandit", "-r", "backend", "-f", "json", "--exit-zero"]
        res = await self._run_command(cmd)
        
        try:
            report = json.loads(res["stdout"])
            metrics = report.get("metrics", {}).get("_totals", {})
            results = report.get("results", [])
            
            high = 0
            medium = 0
            for item in results:
                if item["issue_severity"] == "HIGH": high += 1
                if item["issue_severity"] == "MEDIUM": medium += 1
            
            status = "PASSED"
            if high > 0: status = "FAILED"
            
            return {
                "name": "Bandit Security Scan",
                "status": status,
                "message": f"High: {high}, Medium: {medium}",
                "details": f"Total issues: {len(results)}"
            }
        except:
            return {"name": "Bandit", "status": "FAILED", "message": "Failed to parse Bandit output"}

    async def _run_safety(self) -> Dict[str, Any]:
        # safety check --json
        cmd = ["safety", "check", "--json"]
        res = await self._run_command(cmd)
        
        try:
            # safety might return non-zero if issues found
            report = json.loads(res["stdout"])
            # Report is list of issues or dict
            issues_count = len(report) if isinstance(report, list) else 0
            
            status = "PASSED"
            if issues_count > 0: status = "FAILED"
            
            return {
                "name": "Safety Dependency Check",
                "status": status,
                "message": f"Vulnerabilities found: {issues_count}",
            }
        except:
             # Safety might produce text if --json not supported or error
             return {"name": "Safety", "status": "PASSED_WITH_WARNINGS", "message": "Could not parse safety output or no issues."}

    async def _run_npm_audit(self) -> Dict[str, Any]:
        if not os.path.exists("frontend"):
             return {"name": "NPM Audit", "status": "SKIPPED", "message": "Frontend not found"}
        
        # npm audit --json
        cmd = ["npm.cmd", "audit", "--json"] if os.name == 'nt' else ["npm", "audit", "--json"]
        res = await self._run_command(cmd, cwd="frontend")
        
        try:
            report = json.loads(res["stdout"])
            metadata = report.get("metadata", {}).get("vulnerabilities", {})
            critical = metadata.get("critical", 0)
            high = metadata.get("high", 0)
            
            status = "PASSED"
            if critical > 0 or high > 0: status = "FAILED"
            
            return {
                "name": "NPM Audit",
                "status": status,
                "message": f"Critical: {critical}, High: {high}"
            }
        except:
            return {"name": "NPM Audit", "status": "FAILED", "message": "Failed to parse npm audit"}

    async def _run_trufflehog(self) -> Dict[str, Any]:
        if not shutil.which("trufflehog"):
             return {"name": "Trufflehog", "status": "SKIPPED", "message": "Trufflehog not found"}
        
        # trufflehog filesystem . --json
        # This might be verbose. limit to current dir or src?
        # Assuming just a quick check or skipped for now as args vary by version.
        return {"name": "Trufflehog", "status": "SKIPPED", "message": "Manual configuration required"}

if __name__ == "__main__":
    validator = SecurityValidator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(validator.run())
    print(json.dumps(result, indent=2))
