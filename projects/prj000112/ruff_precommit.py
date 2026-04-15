"""Pre-commit Ruff Integration

This module handles pre-commit hook configuration and execution for Ruff linter.
"""

import os
import subprocess
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class RuffViolation:
    """Represents a Ruff linting violation."""
    file: str
    line: int
    column: int
    code: str
    message: str
    severity: str = "warning"


class RuffConfig:
    """Manages Ruff configuration."""
    
    def __init__(self, config_path: str = ".ruff.toml"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load Ruff configuration from file."""
        config = {
            "line-length": 100,
            "select": ["E", "F", "W"],
            "ignore": ["E203", "W503"],
            "exclude": ["__pycache__", ".git", ".venv"],
            "per-file-ignores": {}
        }
        
        if os.path.exists(self.config_path):
            # Simple TOML parsing (minimal implementation)
            try:
                with open(self.config_path) as f:
                    content = f.read()
                    # Parse basic key = value pairs
                    for line in content.split('\n'):
                        if '=' in line and not line.strip().startswith('#'):
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            if key in config:
                                if isinstance(config[key], int):
                                    config[key] = int(value)
                                else:
                                    config[key] = value
            except Exception:
                pass
        
        return config
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate configuration."""
        errors = []
        
        if not isinstance(self.config.get("line-length"), int):
            errors.append("line-length must be an integer")
        
        if not isinstance(self.config.get("select"), (list, str)):
            errors.append("select must be a list or string")
        
        return len(errors) == 0, errors
    
    def get_config(self) -> Dict:
        """Get the loaded configuration."""
        return self.config


class RuffVersionManager:
    """Manages Ruff version checking and compatibility."""
    
    def __init__(self, min_version: str = "0.1.0"):
        self.min_version = min_version
    
    def get_installed_version(self) -> Optional[str]:
        """Get installed Ruff version."""
        try:
            result = subprocess.run(
                ["ruff", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse version from output like "ruff 0.1.0"
                match = re.search(r'(\d+\.\d+\.\d+)', result.stdout)
                return match.group(1) if match else None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return None
    
    def compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings. Returns -1 if v1<v2, 0 if equal, 1 if v1>v2."""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        for p1, p2 in zip(v1_parts, v2_parts):
            if p1 < p2:
                return -1
            elif p1 > p2:
                return 1
        
        if len(v1_parts) < len(v2_parts):
            return -1
        elif len(v1_parts) > len(v2_parts):
            return 1
        return 0
    
    def check_version_compatibility(self) -> Tuple[bool, str]:
        """Check if installed version meets minimum requirement."""
        installed = self.get_installed_version()
        if installed is None:
            return False, "Ruff not installed"
        
        if self.compare_versions(installed, self.min_version) < 0:
            return False, f"Ruff {installed} < required {self.min_version}"
        
        return True, f"Ruff {installed} OK"


class PreCommitRuffHook:
    """Handles pre-commit hook execution for Ruff."""
    
    def __init__(self, config: RuffConfig):
        self.config = config
        self.violations: List[RuffViolation] = []
    
    def run_check(self, files: List[str] = None) -> Tuple[bool, List[RuffViolation]]:
        """Run Ruff check on specified files."""
        self.violations = []
        
        if not files:
            files = ["."]
        
        try:
            result = subprocess.run(
                ["ruff", "check", "--json"] + files,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse JSON output
            if result.stdout:
                try:
                    output = json.loads(result.stdout)
                    if isinstance(output, list):
                        for item in output:
                            violation = RuffViolation(
                                file=item.get("filename", ""),
                                line=item.get("line_number", 0),
                                column=item.get("column_number", 0),
                                code=item.get("code", ""),
                                message=item.get("message", "")
                            )
                            self.violations.append(violation)
                except json.JSONDecodeError:
                    pass
            
            return result.returncode == 0, self.violations
        
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return False, []
    
    def format_violations(self) -> str:
        """Format violations for display."""
        if not self.violations:
            return "No violations found"
        
        lines = [f"Found {len(self.violations)} violations:\n"]
        for v in self.violations:
            lines.append(f"{v.file}:{v.line}:{v.column}: {v.code} - {v.message}")
        
        return "\n".join(lines)
