"""
Terminal Tool - Safe command execution for the Engineer Agent.
"""
import asyncio
import os
import subprocess
from typing import Dict, Optional

# Blocked commands for safety
BLOCKED_COMMANDS = [
    "rm -rf /", "format", "mkfs", ":(){ :|:& };:"
]

class TerminalTool:
    """Tool for executing shell commands."""
    
    async def run_command(self, command: str, cwd: str = ".") -> Dict[str, str]:
        """
        Run a shell command and return output.
        """
        # 1. Safety Check
        for blocked in BLOCKED_COMMANDS:
            if blocked in command:
                return {"stdout": "", "stderr": f"Command blocked for safety: {blocked}", "exit_code": 1}
        
        # 2. Cwd Resolution
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        working_dir = os.path.abspath(os.path.join(root_dir, cwd))
        
        if not working_dir.startswith(root_dir):
             # Default to root if trying to escape
             working_dir = root_dir

        try:
            # 3. Execution (with 30s timeout)
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
            except asyncio.TimeoutError:
                process.kill()
                return {"stdout": "", "stderr": "Command timed out (30s limit).", "exit_code": 124}
                
            return {
                "stdout": stdout.decode(errors="replace").strip(),
                "stderr": stderr.decode(errors="replace").strip(),
                "exit_code": process.returncode
            }
            
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "exit_code": 1}

# Singleton
terminal = TerminalTool()
