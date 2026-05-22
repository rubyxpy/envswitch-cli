#!/usr/bin/env python3
"""Environment variable validation utility.

Provides functionality to validate environment variables against defined schemas,
check for required variables, and validate value formats.
"""

import os
import re
import sys
from typing import Dict, List, Optional, Any, Callable


class ValidationError(Exception):
    """Raised when environment variable validation fails."""
    pass


class EnvValidator:
    """Validates environment variables against defined rules."""

    def __init__(self):
        self.rules: Dict[str, Dict[str, Any]] = {}
        self.errors: List[str] = []

    def add_rule(self, var_name: str, required: bool = False,
                 pattern: Optional[str] = None,
                 allowed_values: Optional[List[str]] = None,
                 validator: Optional[Callable[[str], bool]] = None,
                 error_message: Optional[str] = None) -> 'EnvValidator':
        """Add a validation rule for an environment variable.

        Args:
            var_name: Name of the environment variable
            required: Whether the variable must be set
            pattern: Regex pattern the value must match
            allowed_values: List of allowed values
            validator: Custom validation function
            error_message: Custom error message for this rule

        Returns:
            Self for method chaining
        """
        self.rules[var_name] = {
            'required': required,
            'pattern': pattern,
            'allowed_values': allowed_values,
            'validator': validator,
            'error_message': error_message
        }
        return self

    def validate(self, env: Optional[Dict[str, str]] = None) -> bool:
        """Validate environment variables against defined rules.

        Args:
            env: Environment dict to validate (defaults to os.environ)

        Returns:
            True if all validations pass, False otherwise
        """
        if env is None:
            env = dict(os.environ)

        self.errors = []

        for var_name, rule in self.rules.items():
            value = env.get(var_name)

            # Check if required
            if rule['required'] and value is None:
                error_msg = rule['error_message'] or f"Required variable '{var_name}' is not set"
                self.errors.append(error_msg)
                continue

            # Skip further validation if not set and not required
            if value is None:
                continue

            # Check against pattern
            if rule['pattern'] and not re.match(rule['pattern'], value):
                error_msg = rule['error_message'] or f"Variable '{var_name}' value '{value}' does not match pattern '{rule['pattern']}'"
                self.errors.append(error_msg)

            # Check against allowed values
            if rule['allowed_values'] and value not in rule['allowed_values']:
                error_msg = rule['error_message'] or f"Variable '{var_name}' value '{value}' not in allowed values: {rule['allowed_values']}"
                self.errors.append(error_msg)

            # Run custom validator
            if rule['validator']:
                try:
                    if not rule['validator'](value):
                        error_msg = rule['error_message'] or f"Variable '{var_name}' failed custom validation"
                        self.errors.append(error_msg)
                except Exception as e:
                    error_msg = rule['error_message'] or f"Variable '{var_name}' validation error: {str(e)}"
                    self.errors.append(error_msg)

        return len(self.errors) == 0

    def get_errors(self) -> List[str]:
        """Get list of validation errors from last validation.

        Returns:
            List of error messages
        """
        return self.errors.copy()

    def validate_or_exit(self, env: Optional[Dict[str, str]] = None, exit_code: int = 1) -> None:
        """Validate and exit with error code if validation fails.

        Args:
            env: Environment dict to validate (defaults to os.environ)
            exit_code: Exit code to use on failure
        """
        if not self.validate(env):
            for error in self.errors:
                print(f"ERROR: {error}", file=sys.stderr)
            sys.exit(exit_code)


def validate_url(value: str) -> bool:
    """Validate that a value is a valid URL."""
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(url_pattern, value))


def validate_port(value: str) -> bool:
    """Validate that a value is a valid port number."""
    try:
        port = int(value)
        return 1 <= port <= 65535
    except ValueError:
        return False


def validate_boolean(value: str) -> bool:
    """Validate that a value is a valid boolean string."""
    return value.lower() in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off')


def validate_email(value: str) -> bool:
    """Validate that a value is a valid email address."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, value))


def main():
    """Example usage of the environment validator."""
    import argparse

    parser = argparse.ArgumentParser(description='Validate environment variables')
    parser.add_argument('--check-required', nargs='+', help='Check that these variables are set')
    parser.add_argument('--check-url', nargs='+', help='Check that these variables contain valid URLs')
    parser.add_argument('--check-port', nargs='+', help='Check that these variables contain valid ports')
    parser.add_argument('--check-email', nargs='+', help='Check that these variables contain valid emails')
    args = parser.parse_args()

    validator = EnvValidator()

    # Add rules based on arguments
    if args.check_required:
        for var in args.check_required:
            validator.add_rule(var, required=True)

    if args.check_url:
        for var in args.check_url:
            validator.add_rule(var, validator=validate_url,
                             error_message=f"Variable '{var}' must be a valid URL")

    if args.check_port:
        for var in args.check_port:
            validator.add_rule(var, validator=validate_port,
                             error_message=f"Variable '{var}' must be a valid port (1-65535)")

    if args.check_email:
        for var in args.check_email:
            validator.add_rule(var, validator=validate_email,
                             error_message=f"Variable '{var}' must be a valid email address")

    # Validate and report
    if validator.validate():
        print("✓ All environment variables are valid")
        return 0
    else:
        print("✗ Environment validation failed:", file=sys.stderr)
        for error in validator.get_errors():
            print(f"  - {error}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
