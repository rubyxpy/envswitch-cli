#!/usr/bin/env python3
"""Environment validation utility for envswitch-cli.

Provides functionality to validate environment configurations before switching,
ensuring required variables are present and values meet expected formats.
"""

import re
from typing import Dict, List, Optional, Set, Tuple


class EnvValidator:
    """Validates environment variable configurations."""

    def __init__(self):
        """Initialize the validator with default rules."""
        self.required_vars: Set[str] = set()
        self.pattern_rules: Dict[str, str] = {}
        self.custom_validators: Dict[str, callable] = {}

    def add_required_var(self, var_name: str) -> None:
        """Add a variable name that must be present in the environment.
        
        Args:
            var_name: Name of the required environment variable
        """
        self.required_vars.add(var_name)

    def add_pattern_rule(self, var_name: str, pattern: str) -> None:
        """Add a regex pattern that a variable's value must match.
        
        Args:
            var_name: Name of the environment variable
            pattern: Regular expression pattern to validate against
        """
        self.pattern_rules[var_name] = pattern

    def add_custom_validator(self, var_name: str, validator_func: callable) -> None:
        """Add a custom validation function for a variable.
        
        Args:
            var_name: Name of the environment variable
            validator_func: Function that takes a value and returns True if valid
        """
        self.custom_validators[var_name] = validator_func

    def validate(self, env_vars: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate environment variables against all rules.
        
        Args:
            env_vars: Dictionary of environment variable names and values
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []

        # Check required variables
        for required_var in self.required_vars:
            if required_var not in env_vars:
                errors.append(f"Missing required variable: {required_var}")
            elif not env_vars[required_var]:
                errors.append(f"Required variable is empty: {required_var}")

        # Check pattern rules
        for var_name, pattern in self.pattern_rules.items():
            if var_name in env_vars:
                value = env_vars[var_name]
                if not re.match(pattern, value):
                    errors.append(
                        f"Variable '{var_name}' value '{value}' does not match pattern '{pattern}'"
                    )

        # Check custom validators
        for var_name, validator_func in self.custom_validators.items():
            if var_name in env_vars:
                value = env_vars[var_name]
                try:
                    if not validator_func(value):
                        errors.append(
                            f"Variable '{var_name}' failed custom validation"
                        )
                except Exception as e:
                    errors.append(
                        f"Error validating '{var_name}': {str(e)}"
                    )

        return (len(errors) == 0, errors)

    def validate_url(self, value: str) -> bool:
        """Validate that a value is a valid URL.
        
        Args:
            value: String to validate as URL
            
        Returns:
            True if valid URL, False otherwise
        """
        url_pattern = r'^https?://[\w\-\.]+(:\d+)?(/.*)?$'
        return bool(re.match(url_pattern, value))

    def validate_port(self, value: str) -> bool:
        """Validate that a value is a valid port number.
        
        Args:
            value: String to validate as port number
            
        Returns:
            True if valid port (1-65535), False otherwise
        """
        try:
            port = int(value)
            return 1 <= port <= 65535
        except (ValueError, TypeError):
            return False

    def validate_email(self, value: str) -> bool:
        """Validate that a value is a valid email address.
        
        Args:
            value: String to validate as email
            
        Returns:
            True if valid email format, False otherwise
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, value))


def create_common_validator() -> EnvValidator:
    """Create a validator with common environment variable rules.
    
    Returns:
        EnvValidator configured with common validation rules
    """
    validator = EnvValidator()
    
    # Common patterns
    validator.add_pattern_rule('DATABASE_URL', r'^(postgresql|mysql|sqlite)://.*')
    validator.add_pattern_rule('API_KEY', r'^[A-Za-z0-9_-]{16,}$')
    validator.add_pattern_rule('ENV', r'^(development|staging|production)$')
    
    # Custom validators for common variables
    validator.add_custom_validator('PORT', validator.validate_port)
    validator.add_custom_validator('API_URL', validator.validate_url)
    validator.add_custom_validator('ADMIN_EMAIL', validator.validate_email)
    
    return validator


if __name__ == '__main__':
    # Example usage
    validator = create_common_validator()
    validator.add_required_var('DATABASE_URL')
    validator.add_required_var('API_KEY')
    
    # Test with sample environment
    test_env = {
        'DATABASE_URL': 'postgresql://localhost/mydb',
        'API_KEY': 'abcd1234efgh5678ijkl',
        'ENV': 'development',
        'PORT': '8080',
        'API_URL': 'https://api.example.com',
        'ADMIN_EMAIL': 'admin@example.com'
    }
    
    is_valid, errors = validator.validate(test_env)
    
    if is_valid:
        print("✓ All environment variables are valid")
    else:
        print("✗ Validation errors:")
        for error in errors:
            print(f"  - {error}")
