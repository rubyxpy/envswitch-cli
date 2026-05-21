#!/usr/bin/env python3
"""Environment variable validation utility.

Provides functionality to validate environment variable files and check for
common issues like syntax errors, missing values, or invalid formats.
"""

import json
import os
import sys
from typing import Dict, List, Tuple


class ValidationError:
    """Represents a validation error found in an environment file."""
    
    def __init__(self, line_number: int, message: str, severity: str = "error"):
        self.line_number = line_number
        self.message = message
        self.severity = severity
    
    def __repr__(self):
        return f"Line {self.line_number}: [{self.severity.upper()}] {self.message}"


def validate_env_file(file_path: str) -> Tuple[bool, List[ValidationError]]:
    """Validate an environment variable file.
    
    Args:
        file_path: Path to the environment file to validate
        
    Returns:
        Tuple of (is_valid, list of ValidationError objects)
    """
    errors = []
    
    if not os.path.exists(file_path):
        errors.append(ValidationError(0, f"File not found: {file_path}"))
        return False, errors
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        errors.append(ValidationError(0, f"Cannot read file: {str(e)}"))
        return False, errors
    
    seen_vars = set()
    
    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            continue
        
        # Check for basic KEY=VALUE format
        if '=' not in stripped:
            errors.append(ValidationError(
                line_num,
                f"Invalid format: missing '=' separator"
            ))
            continue
        
        # Split on first '=' only
        parts = stripped.split('=', 1)
        key = parts[0].strip()
        value = parts[1].strip() if len(parts) > 1 else ""
        
        # Validate key format
        if not key:
            errors.append(ValidationError(
                line_num,
                "Empty variable name"
            ))
            continue
        
        if not key.replace('_', '').isalnum():
            errors.append(ValidationError(
                line_num,
                f"Invalid variable name '{key}': must contain only alphanumeric characters and underscores",
                severity="warning"
            ))
        
        if not key[0].isalpha() and key[0] != '_':
            errors.append(ValidationError(
                line_num,
                f"Invalid variable name '{key}': must start with a letter or underscore",
                severity="warning"
            ))
        
        # Check for duplicates
        if key in seen_vars:
            errors.append(ValidationError(
                line_num,
                f"Duplicate variable '{key}'",
                severity="warning"
            ))
        
        seen_vars.add(key)
        
        # Check for unquoted values with spaces (potential issue)
        if value and ' ' in value and not (
            (value.startswith('"') and value.endswith('"')) or
            (value.startswith("'") and value.endswith("'"))
        ):
            errors.append(ValidationError(
                line_num,
                f"Value for '{key}' contains spaces but is not quoted",
                severity="warning"
            ))
    
    # Only return False if there are actual errors (not warnings)
    has_errors = any(e.severity == "error" for e in errors)
    return not has_errors, errors


def validate_env_dict(env_dict: Dict[str, str]) -> Tuple[bool, List[ValidationError]]:
    """Validate an environment variable dictionary.
    
    Args:
        env_dict: Dictionary of environment variables to validate
        
    Returns:
        Tuple of (is_valid, list of ValidationError objects)
    """
    errors = []
    
    for key, value in env_dict.items():
        if not isinstance(key, str):
            errors.append(ValidationError(
                0,
                f"Variable name must be a string, got {type(key).__name__}"
            ))
            continue
        
        if not key:
            errors.append(ValidationError(0, "Empty variable name"))
            continue
        
        if not key.replace('_', '').isalnum():
            errors.append(ValidationError(
                0,
                f"Invalid variable name '{key}': must contain only alphanumeric characters and underscores",
                severity="warning"
            ))
        
        if not isinstance(value, str):
            errors.append(ValidationError(
                0,
                f"Value for '{key}' must be a string, got {type(value).__name__}",
                severity="warning"
            ))
    
    has_errors = any(e.severity == "error" for e in errors)
    return not has_errors, errors


def main():
    """Main entry point for the validation utility."""
    if len(sys.argv) < 2:
        print("Usage: validate_env.py <env_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    is_valid, errors = validate_env_file(file_path)
    
    if not errors:
        print(f"✓ {file_path} is valid")
        sys.exit(0)
    
    print(f"Validation results for {file_path}:")
    print()
    
    error_count = sum(1 for e in errors if e.severity == "error")
    warning_count = sum(1 for e in errors if e.severity == "warning")
    
    for error in errors:
        symbol = "✗" if error.severity == "error" else "⚠"
        print(f"{symbol} {error}")
    
    print()
    print(f"Found {error_count} error(s) and {warning_count} warning(s)")
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
