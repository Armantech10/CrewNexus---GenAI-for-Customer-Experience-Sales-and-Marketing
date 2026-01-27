import json
import os
import jsonschema
from typing import Dict, List, Any
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("validators.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SpecValidator")

class SpecValidator:
    """
    Validator for specs.json and components.json structure.
    """
    def __init__(self):
        self.specs_path = "specs.json"
        self.components_path = "components.json"
        self.schema_path = "schemas/specs_schema.json" # Assumed path, checks if exists

    async def run(self) -> Dict[str, Any]:
        """
        Run the specification validation.
        """
        logger.info("Starting Spec Validator...")
        results = {
            "name": "spec_validator",
            "status": "FAILED",
            "duration_ms": 0,
            "checks": []
        }
        start_time = asyncio.get_event_loop().time()

        checks = []
        
        # Check 1: specs.json existence
        checks.append(self._check_file_exists(self.specs_path))
        
        # Check 2: components.json existence
        checks.append(self._check_file_exists(self.components_path))

        # Check 3: Validate specs.json
        if self._file_exists(self.specs_path):
             checks.append(self._validate_json_structure(self.specs_path))

        # Check 4: Validate components.json
        if self._file_exists(self.components_path):
             checks.append(self._validate_json_structure(self.components_path))

        # Determine status
        failed_checks = [c for c in checks if c["status"] == "FAILED"]
        if not failed_checks:
            results["status"] = "PASSED"
        else:
            results["status"] = "FAILED"
            results["errors"] = [c["message"] for c in failed_checks]

        end_time = asyncio.get_event_loop().time()
        results["duration_ms"] = int((end_time - start_time) * 1000)
        results["checks"] = checks
        
        logger.info(f"Spec Validator finished with status: {results['status']}")
        return results

    def _file_exists(self, path: str) -> bool:
        return os.path.exists(path)

    def _check_file_exists(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            return {"name": f"Check {path} exists", "status": "PASSED", "message": f"{path} found."}
        else:
            return {"name": f"Check {path} exists", "status": "FAILED", "message": f"{path} not found."}

    def _validate_json_structure(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            # Basic type check
            if not isinstance(data, (dict, list)):
                 return {"name": f"Validate {path} structure", "status": "FAILED", "message": "Root must be object or array."}
            
            # TODO: Implement schema validation if schema exists
            # For now, just valid JSON check is passing
            return {"name": f"Validate {path} JSON syntax", "status": "PASSED", "message": "Valid JSON."}
        except json.JSONDecodeError as e:
            return {"name": f"Validate {path} JSON syntax", "status": "FAILED", "message": f"Invalid JSON: {str(e)}"}
        except Exception as e:
            return {"name": f"Validate {path} JSON syntax", "status": "FAILED", "message": f"Error reading file: {str(e)}"}

if __name__ == "__main__":
    validator = SpecValidator()
    # Run async in main
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(validator.run())
    print(json.dumps(result, indent=2))
