#!/usr/bin/env python3
"""
MyPy configuration validator - ensures strict type checking is enabled for src/core.

Validates:
- mypy.ini has strict = True for [mypy] or [mypy-src.core*]
- No ignore_errors = True settings
- Type checking configuration is correct
"""

import configparser
import sys
from pathlib import Path
from typing import List, Tuple


def check_mypy_config(config_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate mypy.ini configuration.
    
    Returns: (is_valid, violations)
    """
    if not config_path.exists():
        return False, ["mypy.ini not found"]
    
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
    except Exception as e:
        return False, [f"Failed to parse mypy.ini: {e}"]
    
    violations = []
    
    # Check main mypy section
    if "mypy" in config:
        mypy_section = config["mypy"]
        
        # Check for ignore_errors
        if mypy_section.get("ignore_errors", "False").lower() == "true":
            violations.append("mypy.ini: ignore_errors = True (should be False)")
        
        # Check for strict mode
        strict_value = mypy_section.get("strict", "False").lower()
        if strict_value != "true":
            violations.append("mypy.ini: strict = False (should be True in [mypy] or section-specific)")
    
    # Check for src/core specific section with strict enabled
    has_core_strict = False
    for section in config.sections():
        if "src.core" in section:
            if config[section].get("strict", "False").lower() == "true":
                has_core_strict = True
                break
    
    # If we have src/core specific config, that's good enough
    # Otherwise, check that main section has strict
    if not has_core_strict and "mypy" in config:
        if config["mypy"].get("strict", "False").lower() != "true":
            violations.append("No strict=True found for src/core or global [mypy] section")
    
    return len(violations) == 0, violations


def validate_mypy_enforcement(config_path: Path) -> int:
    """
    Main validation function.
    
    Returns: 0 if valid, 1 if violations found
    """
    is_valid, violations = check_mypy_config(config_path)
    
    if not is_valid:
        print("ERROR: MyPy configuration violations found:", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation}", file=sys.stderr)
        return 1
    
    print("✓ MyPy strict enforcement enabled")
    return 0


if __name__ == "__main__":
    config_path = Path("mypy.ini")
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])
    
    sys.exit(validate_mypy_enforcement(config_path))
