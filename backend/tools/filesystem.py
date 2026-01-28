"""
FileSystem Tool - Safe file operations for the Engineer Agent.
Allows listing, reading, and writing files within a sandboxed directory.
"""
import os
import shutil
from typing import List, Dict, Optional, Union
from pydantic import BaseModel

# Project Root (Sandboxed to current project)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

class FileSystemTool:
    """Tool for safe file system interactions."""
    
    def _validate_path(self, path: str) -> str:
        """Ensure path is within PROJECT_ROOT to prevent jailbreak."""
        # Handle absolute or relative paths
        if os.path.isabs(path):
            abs_path = os.path.abspath(path)
        else:
            abs_path = os.path.abspath(os.path.join(PROJECT_ROOT, path))
            
        if not abs_path.startswith(PROJECT_ROOT):
            raise ValueError(f"Access denied: Path '{path}' is outside project root.")
            
        return abs_path

    async def list_dir(self, path: str = ".") -> List[Dict[str, str]]:
        """List contents of a directory."""
        target_path = self._validate_path(path)
        
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Directory not found: {path}")
            
        items = []
        for name in os.listdir(target_path):
            if name.startswith(".") and name != ".env": # Skip hidden files except .env
                continue
            
            full_path = os.path.join(target_path, name)
            is_dir = os.path.isdir(full_path)
            
            items.append({
                "name": name,
                "type": "directory" if is_dir else "file",
                "path": os.path.relpath(full_path, PROJECT_ROOT).replace("\\", "/") # Normalize for frontend
            })
            
        return sorted(items, key=lambda x: (x["type"] != "directory", x["name"]))

    async def read_file(self, path: str) -> str:
        """Read file content."""
        target_path = self._validate_path(path)
        
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"File not found: {path}")
            
        if os.path.getsize(target_path) > 100_000: # 100KB limit for safety
            return "[Error: File too large to read directly. Use search or outline.]"
            
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            return "[Error: Binary file detected]"

    async def write_file(self, path: str, content: str) -> str:
        """Write content to a file (overwrites existing)."""
        target_path = self._validate_path(path)
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Create backup if file exists
        if os.path.exists(target_path):
            backup_path = f"{target_path}.bak"
            shutil.copy2(target_path, backup_path)
            
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Successfully wrote to {path}"

    async def get_file_tree(self) -> Dict:
        """Get recursive file tree (simplified for UI)."""
        # TODO: Implement cached recursive tree for large projects
        return await self.list_dir(".")

# Singleton
filesystem = FileSystemTool()
