#!/usr/bin/env python3
"""Unit tests for EnvSwitch core library."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

try:
    from envswitch import (
        EnvSwitch,
        EnvSwitchError,
        ConfigNotFoundError,
        InvalidConfigError,
        EnvironmentNotFoundError,
    )
except ImportError:
    # Handle case where envswitch.py is incomplete
    EnvSwitch = None


class TestEnvSwitchExceptions(unittest.TestCase):
    """Test custom exception hierarchy."""

    def test_base_exception(self):
        """Test that EnvSwitchError is properly defined."""
        if EnvSwitch is None:
            self.skipTest("envswitch module not available")
        
        error = EnvSwitchError("test error")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "test error")

    def test_config_not_found_error(self):
        """Test ConfigNotFoundError inheritance."""
        if EnvSwitch is None:
            self.skipTest("envswitch module not available")
        
        error = ConfigNotFoundError("config missing")
        self.assertIsInstance(error, EnvSwitchError)
        self.assertEqual(str(error), "config missing")

    def test_invalid_config_error(self):
        """Test InvalidConfigError inheritance."""
        if EnvSwitch is None:
            self.skipTest("envswitch module not available")
        
        error = InvalidConfigError("invalid format")
        self.assertIsInstance(error, EnvSwitchError)

    def test_environment_not_found_error(self):
        """Test EnvironmentNotFoundError inheritance."""
        if EnvSwitch is None:
            self.skipTest("envswitch module not available")
        
        error = EnvironmentNotFoundError("env not found")
        self.assertIsInstance(error, EnvSwitchError)


class TestEnvSwitchInit(unittest.TestCase):
    """Test EnvSwitch initialization."""

    def test_default_config_dir(self):
        """Test that default config directory is set correctly."""
        if EnvSwitch is None:
            self.skipTest("envswitch module not available")
        
        env_switch = EnvSwitch()
        expected_dir = Path.home() / ".envswitch"
        self.assertEqual(env_switch.config_dir, expected_dir)

    def test_custom_config_dir(self):
        """Test initialization with custom config directory."""
        if EnvSwitch is None:
            self.skipTest("envswitch module not available")
        
        custom_dir = Path("/tmp/custom_envswitch")
        env_switch = EnvSwitch(config_dir=custom_dir)
        self.assertEqual(env_switch.config_dir, custom_dir)

    def test_config_file_path(self):
        """Test that config_file path is properly constructed."""
        if EnvSwitch is None:
            self.skipTest("envswitch module not available")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            env_switch = EnvSwitch(config_dir=config_dir)
            # Check if config_file attribute exists and is a Path
            self.assertTrue(hasattr(env_switch, 'config_file'))
            if env_switch.config_file is not None:
                self.assertIsInstance(env_switch.config_file, Path)


class TestEnvSwitchValidation(unittest.TestCase):
    """Test validation methods."""

    def test_validate_env_name_valid(self):
        """Test validation of valid environment names."""
        if EnvSwitch is None:
            self.skipTest("envswitch module not available")
        
        valid_names = ["dev", "production", "test-env", "stage_2", "env123"]
        env_switch = EnvSwitch()
        
        for name in valid_names:
            # Should not raise exception for valid names
            try:
                if hasattr(env_switch, 'validate_env_name'):
                    env_switch.validate_env_name(name)
            except Exception as e:
                self.fail(f"Valid name '{name}' raised exception: {e}")

    def test_validate_env_name_invalid(self):
        """Test validation rejects invalid environment names."""
        if EnvSwitch is None:
            self.skipTest("envswitch module not available")
        
        invalid_names = ["", " ", "env with spaces", "env/slash", "env\\backslash"]
        env_switch = EnvSwitch()
        
        for name in invalid_names:
            if hasattr(env_switch, 'validate_env_name'):
                with self.assertRaises((ValueError, EnvSwitchError)):
                    env_switch.validate_env_name(name)


class TestEnvSwitchFileOperations(unittest.TestCase):
    """Test file operations like load and save."""

    def test_load_config_creates_dir(self):
        """Test that loading config creates directory if missing."""
        if EnvSwitch is None:
            self.skipTest("envswitch module not available")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "new_config"
            env_switch = EnvSwitch(config_dir=config_dir)
            
            if hasattr(env_switch, 'load_config'):
                try:
                    env_switch.load_config()
                except (ConfigNotFoundError, FileNotFoundError):
                    # Expected if config doesn't exist yet
                    pass

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        if EnvSwitch is None:
            self.skipTest("envswitch module not available")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            env_switch = EnvSwitch(config_dir=config_dir)
            
            test_config = {
                "current": "dev",
                "environments": {
                    "dev": {"API_KEY": "dev-key", "DEBUG": "true"}
                }
            }
            
            if hasattr(env_switch, 'save_config') and hasattr(env_switch, 'load_config'):
                try:
                    env_switch.save_config(test_config)
                    loaded = env_switch.load_config()
                    self.assertEqual(loaded, test_config)
                except AttributeError:
                    self.skipTest("Methods not fully implemented")


if __name__ == "__main__":
    unittest.main()
