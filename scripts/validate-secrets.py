#!/usr/bin/env python3
"""
Secret validation script - detects and prevents private keys from being committed.

Patterns detected:
- Private key files (.pem, .key, .priv, .ppk)
- AWS credential files
- OpenSSH private keys
- PGP private keys
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


# Patterns for common private key formats
SECRET_PATTERNS = {
    "rsa_private": re.compile(r"-----BEGIN RSA PRIVATE KEY-----", re.MULTILINE),
    "openssh_private": re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----", re.MULTILINE),
    "private_key_generic": re.compile(r"-----BEGIN PRIVATE KEY-----", re.MULTILINE),
    "pgp_private": re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----", re.MULTILINE),
    "aws_secret": re.compile(r"aws_secret_access_key\s*=", re.MULTILINE | re.IGNORECASE),
    "api_key": re.compile(r"(api_key|apikey|api-key|secret)\s*[=:]\s*['\"]?[a-zA-Z0-9]{20,}", re.IGNORECASE),
}

# File extensions that commonly contain secrets
DANGEROUS_EXTENSIONS = {".pem", ".key", ".priv", ".ppk", ".pfx", ".p12"}


def check_file_content(file_path: Path) -> Tuple[bool, str]:
    """
    Check if a file contains secret patterns.
    
    Returns: (is_secret, reason)
    """
    try:
        content = file_path.read_text(errors="ignore")
    except Exception:
        return False, ""
    
    for pattern_name, pattern in SECRET_PATTERNS.items():
        if pattern.search(content):
            return True, f"Detected {pattern_name}"
    
    return False, ""


def check_file_extension(file_path: Path) -> Tuple[bool, str]:
    """Check if file has dangerous extension."""
    if file_path.suffix.lower() in DANGEROUS_EXTENSIONS:
        return True, f"Dangerous file extension: {file_path.suffix}"
    return False, ""


def validate_files(file_paths: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate that none of the files contain secrets.
    
    Returns: (is_valid, violations)
    """
    violations = []
    
    for file_path_str in file_paths:
        file_path = Path(file_path_str)
        
        # Check extension
        has_dangerous_ext, reason = check_file_extension(file_path)
        if has_dangerous_ext:
            violations.append(f"{file_path}: {reason}")
            continue
        
        # Check content
        has_secret, reason = check_file_content(file_path)
        if has_secret:
            violations.append(f"{file_path}: {reason}")
    
    return len(violations) == 0, violations


def main() -> int:
    """
    Main entry point. Reads file paths from stdin or arguments.
    Returns 0 if valid, 1 if secrets detected.
    """
    # Get file paths from command line arguments
    if len(sys.argv) > 1:
        file_paths = sys.argv[1:]
    else:
        # Read from stdin (one file per line)
        file_paths = [line.strip() for line in sys.stdin if line.strip()]
    
    if not file_paths:
        return 0
    
    is_valid, violations = validate_files(file_paths)
    
    if not is_valid:
        print("ERROR: Secret material detected in commit:", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
