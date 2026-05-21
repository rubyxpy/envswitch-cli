import pytest
import os
import tempfile
from validate_env import validate_env_file, validate_env_vars, ValidationResult


class TestValidateEnvFile:
    """Test suite for validate_env_file function."""

    def test_validate_valid_env_file(self):
        """Test validation of a valid .env file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
            f.write("API_KEY=secret123\n")
            f.write("DATABASE_URL=postgresql://localhost/db\n")
            f.write("DEBUG=true\n")
            temp_path = f.name

        try:
            result = validate_env_file(temp_path)
            assert result.is_valid is True
            assert len(result.errors) == 0
            assert len(result.warnings) == 0
        finally:
            os.unlink(temp_path)

    def test_validate_file_with_empty_values(self):
        """Test validation with empty variable values."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
            f.write("API_KEY=\n")
            f.write("DATABASE_URL=postgresql://localhost/db\n")
            temp_path = f.name

        try:
            result = validate_env_file(temp_path)
            assert len(result.warnings) > 0
            assert any('empty value' in w.lower() for w in result.warnings)
        finally:
            os.unlink(temp_path)

    def test_validate_file_with_invalid_syntax(self):
        """Test validation with invalid syntax lines."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
            f.write("VALID_VAR=value\n")
            f.write("INVALID LINE WITHOUT EQUALS\n")
            f.write("ANOTHER_VALID=test\n")
            temp_path = f.name

        try:
            result = validate_env_file(temp_path)
            assert result.is_valid is False
            assert len(result.errors) > 0
            assert any('invalid syntax' in e.lower() for e in result.errors)
        finally:
            os.unlink(temp_path)

    def test_validate_file_with_duplicate_keys(self):
        """Test validation with duplicate variable names."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
            f.write("API_KEY=first_value\n")
            f.write("DATABASE_URL=postgresql://localhost/db\n")
            f.write("API_KEY=second_value\n")
            temp_path = f.name

        try:
            result = validate_env_file(temp_path)
            assert len(result.warnings) > 0
            assert any('duplicate' in w.lower() for w in result.warnings)
        finally:
            os.unlink(temp_path)

    def test_validate_nonexistent_file(self):
        """Test validation of a file that doesn't exist."""
        result = validate_env_file('/nonexistent/path/to/file.env')
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any('not found' in e.lower() or 'does not exist' in e.lower() for e in result.errors)

    def test_validate_file_with_comments(self):
        """Test that comments are properly ignored."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
            f.write("# This is a comment\n")
            f.write("API_KEY=secret\n")
            f.write("# Another comment\n")
            f.write("DATABASE_URL=postgresql://localhost/db\n")
            temp_path = f.name

        try:
            result = validate_env_file(temp_path)
            assert result.is_valid is True
            assert len(result.errors) == 0
        finally:
            os.unlink(temp_path)

    def test_validate_file_with_quoted_values(self):
        """Test validation with quoted values."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
            f.write('API_KEY="secret with spaces"\n')
            f.write("DATABASE_URL='postgresql://localhost/db'\n")
            f.write('MESSAGE="Hello, World!"\n')
            temp_path = f.name

        try:
            result = validate_env_file(temp_path)
            assert result.is_valid is True
            assert len(result.errors) == 0
        finally:
            os.unlink(temp_path)


class TestValidateEnvVars:
    """Test suite for validate_env_vars function."""

    def test_validate_valid_env_dict(self):
        """Test validation of a valid environment dictionary."""
        env_vars = {
            'API_KEY': 'secret123',
            'DATABASE_URL': 'postgresql://localhost/db',
            'DEBUG': 'true'
        }
        result = validate_env_vars(env_vars)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_env_dict_with_empty_values(self):
        """Test validation with empty values in dictionary."""
        env_vars = {
            'API_KEY': '',
            'DATABASE_URL': 'postgresql://localhost/db'
        }
        result = validate_env_vars(env_vars)
        assert len(result.warnings) > 0
        assert any('empty value' in w.lower() for w in result.warnings)

    def test_validate_env_dict_with_invalid_keys(self):
        """Test validation with invalid variable names."""
        env_vars = {
            'VALID_KEY': 'value',
            '123_INVALID': 'value',
            'invalid-key': 'value'
        }
        result = validate_env_vars(env_vars)
        assert len(result.warnings) > 0
        assert any('invalid' in w.lower() or 'name' in w.lower() for w in result.warnings)

    def test_validate_empty_env_dict(self):
        """Test validation of an empty dictionary."""
        env_vars = {}
        result = validate_env_vars(env_vars)
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any('empty' in w.lower() for w in result.warnings)


class TestValidationResult:
    """Test suite for ValidationResult class."""

    def test_validation_result_initialization(self):
        """Test ValidationResult object creation."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_validation_result_with_errors(self):
        """Test ValidationResult with errors."""
        errors = ['Error 1', 'Error 2']
        result = ValidationResult(is_valid=False, errors=errors, warnings=[])
        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_validation_result_with_warnings(self):
        """Test ValidationResult with warnings."""
        warnings = ['Warning 1', 'Warning 2']
        result = ValidationResult(is_valid=True, errors=[], warnings=warnings)
        assert result.is_valid is True
        assert len(result.warnings) == 2
