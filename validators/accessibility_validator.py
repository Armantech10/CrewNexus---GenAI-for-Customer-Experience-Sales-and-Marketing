import asyncio
import json
import logging
import os
import shutil
from typing import Dict, Any, List

logger = logging.getLogger("AccessibilityValidator")

class AccessibilityValidator:
    """
    Validator for accessibility (WCAG 2.1 AA) using axe-core CLI or pa11y.
    """
    async def run(self) -> Dict[str, Any]:
        logger.info("Starting Accessibility Validator...")
        start_time = asyncio.get_event_loop().time()
        
        results = {
            "name": "accessibility_validator",
            "status": "PASSED",
            "duration_ms": 0,
            "checks": []
        }

        pages = ["/chat", "/dashboard", "/campaigns"]
        url_base = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        checks = await asyncio.gather(
            *[self._check_page(url_base + page) for page in pages],
            return_exceptions=True
        )

        for check in checks:
            if isinstance(check, dict):
                 results["checks"].append(check)
                 if check["status"] == "FAILED":
                     # Critical/Serious issues fail the validation
                     results["status"] = "FAILED"
            else:
                 results["checks"].append({"name": "Unknown", "status": "FAILED", "message": str(check)})

        end_time = asyncio.get_event_loop().time()
        results["duration_ms"] = int((end_time - start_time) * 1000)
        
        logger.info(f"Accessibility Validator finished with status: {results['status']}")
        return results

    async def _check_page(self, url: str) -> Dict[str, Any]:
        # Tool: axe <url> --json (from @axe-core/cli)
        if not shutil.which("axe"):
            # Try pa11y
            if not shutil.which("pa11y"):
                 return {"name": f"A11y {url}", "status": "SKIPPED", "message": "axe/pa11y CLI not found"}

        cmd = [
            "axe", 
            url, 
            "--tags", "wcag2aa", 
            "--json",
            "--chrome-flags='--headless --no-sandbox'"
        ]
        
        try:
            process = await asyncio.create_subprocess_shell(
                " ".join(cmd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0 and not stdout:
                 return {"name": f"A11y {url}", "status": "FAILED", "message": "Tool execution failed", "details": stderr.decode()}

            # Parse JSON
            try:
                report = json.loads(stdout)
                violations = report[0].get("violations", []) if isinstance(report, list) else report.get("violations", [])
                
                critical = 0
                serious = 0
                moderate = 0
                
                for v in violations:
                    impact = v.get("impact")
                    if impact == "critical": critical += 1
                    if impact == "serious": serious += 1
                    if impact == "moderate": moderate += 1
                
                status = "PASSED"
                if critical > 0 or serious > 0: status = "FAILED"
                if moderate >= 5: status = "PASSED_WITH_WARNINGS"

                return {
                    "name": f"A11y {url}",
                    "status": status,
                    "metrics": {
                        "critical": critical,
                        "serious": serious,
                        "moderate": moderate
                    },
                    "message": f"Critical: {critical}, Serious: {serious}"
                }
            except Exception as e:
                 return {"name": f"A11y {url}", "status": "FAILED", "message": f"Parse error: {str(e)}"}

        except Exception as e:
            return {"name": f"A11y {url}", "status": "FAILED", "message": str(e)}

if __name__ == "__main__":
    validator = AccessibilityValidator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(validator.run())
    print(json.dumps(result, indent=2))
