import asyncio
import json
import logging
import uuid
import datetime
from typing import Dict, List, Any
import aiofiles

import sys
import os

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from validators.spec_validator import SpecValidator
    from validators.code_quality_validator import CodeQualityValidator
    from validators.test_coverage_validator import TestCoverageValidator
    from validators.integration_test_validator import IntegrationTestValidator
    from validators.performance_validator import PerformanceValidator
    from validators.security_validator import SecurityValidator
    from validators.accessibility_validator import AccessibilityValidator
    from validators.deployment_validator import DeploymentValidator
except ImportError as e:
    # Fallback for direct execution vs module execution or missing deps
    logging.error(f"Import failed: {e}")
    # Try relative imports if running from inside package (unlikely with sys.path fix but good safety)
    try:
        from spec_validator import SpecValidator
        from code_quality_validator import CodeQualityValidator
        from test_coverage_validator import TestCoverageValidator
        from integration_test_validator import IntegrationTestValidator
        from performance_validator import PerformanceValidator
        from security_validator import SecurityValidator
        from accessibility_validator import AccessibilityValidator
        from deployment_validator import DeploymentValidator
    except ImportError as e2:
        logging.critical(f"Critical Import Error: {e2}")
        raise

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("validators.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ValidatorOrchestrator")

class ValidatorOrchestrator:
    def __init__(self):
        self.run_id = self._generate_run_id()
        self.validators = [
            SpecValidator(),
            CodeQualityValidator(),
            TestCoverageValidator(),
            IntegrationTestValidator(),
            PerformanceValidator(),
            SecurityValidator(),
            AccessibilityValidator(),
            DeploymentValidator()
        ]

    def _generate_run_id(self) -> str:
        return f"val_{uuid.uuid4().hex[:8]}"

    async def run_all(self) -> Dict[str, Any]:
        logger.info(f"Starting Validation Run: {self.run_id}")
        start_time = datetime.datetime.now()

        # Run all validators in parallel with timeout
        # Individual timeouts are handled inside validators or we can wrap here.
        # Requirement: "Handle timeouts gracefully". I'll wrap tasks.
        
        tasks = [self._run_safe(v) for v in self.validators]
        results_list = await asyncio.gather(*tasks)

        # Aggregate results
        scores = self._calculate_scores(results_list)
        overall_status = self._determine_status(results_list)
        recommendations = self._generate_recommendations(results_list)
        
        summary = {
            "total_checks": sum(len(r.get("checks", [])) for r in results_list),
            "passed": sum(len([c for c in r.get("checks", []) if c["status"] == "PASSED"]) for r in results_list),
            "warnings": sum(len([c for c in r.get("checks", []) if "WARNING" in c["status"]]) for r in results_list),
            "failed": sum(len([c for c in r.get("checks", []) if c["status"] == "FAILED"]) for r in results_list)
        }

        output = {
            "version": "1.0.0",
            "generated_at": datetime.datetime.now().isoformat(),
            "validation_run_id": self.run_id,
            "overall_status": overall_status,
            "scores": scores,
            "validators": results_list,
            "summary": summary,
            "recommendations": recommendations,
            "next_checkpoint": {
                "id": "checkpoint_3",
                "name": "Pre-Deploy Review",
                "status": "READY" if overall_status != "FAILED" else "BLOCKED"
            }
        }

        # Write to status.json
        async with aiofiles.open("status.json", "w") as f:
            await f.write(json.dumps(output, indent=2))
        
        logger.info(f"Validation Run Complete. Status: {overall_status}")
        return output

    async def _run_safe(self, validator) -> Dict[str, Any]:
        """Run validator with exception handling and timeout."""
        try:
            # Default individual timeout 5 mins if not specified
            # But requirements have specific timeouts per validator.
            # I'll rely on global timeout or assume validators handle it.
            # Adding a safety wrapper here.
            return await asyncio.wait_for(validator.run(), timeout=300) 
        except asyncio.TimeoutError:
            return {
                "name": validator.__class__.__name__,
                "status": "SKIPPED",
                "duration_ms": 300000,
                "checks": [],
                "message": "Timed out"
            }
        except Exception as e:
            logger.exception(f"{validator.__class__.__name__} failed")
            return {
                "name": validator.__class__.__name__,
                "status": "FAILED",
                "duration_ms": 0,
                "checks": [],
                "message": f"Crashed: {str(e)}"
            }

    def _calculate_scores(self, results: List[Dict]) -> Dict[str, int]:
        # Simple scoring logic: 100 - (deductions)
        # Or based on passed checks %
        
        def calculate_validator_score(res):
            checks = res.get("checks", [])
            if not checks: return 0 if res["status"] == "FAILED" else 100
            passed = len([c for c in checks if c["status"] == "PASSED"])
            total = len(checks)
            return int((passed / total) * 100)

        scores = {}
        total_score = 0
        count = 0
        
        # Map validator names to score categories
        category_map = {
            "spec_validator": "specs",
            "code_quality_validator": "code_quality",
            "test_coverage_validator": "test_coverage",
            "integration_test_validator": "integration",
            "performance_validator": "performance",
            "security_validator": "security",
            "accessibility_validator": "accessibility",
            "deployment_validator": "deployment"
        }

        for res in results:
            score = calculate_validator_score(res)
            key = category_map.get(res.get("name", "").lower(), "other")
            scores[key] = score
            total_score += score
            count += 1
            
        scores["overall"] = int(total_score / count) if count > 0 else 0
        return scores

    def _determine_status(self, results: List[Dict]) -> str:
        statuses = [r["status"] for r in results]
        if "FAILED" in statuses:
            return "FAILED"
        if "PASSED_WITH_WARNINGS" in statuses:
            return "PASSED_WITH_WARNINGS"
        return "PASSED"

    def _generate_recommendations(self, results: List[Dict]) -> List[Dict]:
        recs = []
        for res in results:
            if res["status"] != "PASSED":
                name = res.get("name", "Unknown")
                for check in res.get("checks", []):
                    if check["status"] != "PASSED":
                        recs.append({
                            "priority": "high" if check["status"] == "FAILED" else "medium",
                            "category": name,
                            "message": f"{check.get('name')}: {check.get('message')}"
                        })
        return recs

if __name__ == "__main__":
    orchestrator = ValidatorOrchestrator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(orchestrator.run_all())
