#!/usr/bin/env python3
"""EnvSwitch library module - Core functionality for environment management."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List


class EnvSwitchError(Exception):
    """Base exception for EnvSwitch operations."""
    pass


class ConfigNotFoundError(EnvSwitchError):
    """Raised when environment configuration is not found."""
    pass


class InvalidConfigError(EnvSwitchError):
    """Raised when configuration format is invalid."""
    pass


class EnvironmentNotFoundError(EnvSwitchError):
    """Raised when specified environment does not exist."""
    pass


class EnvSwitch:
    """Core class for managing environment configurations."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialize EnvSwitch with optional custom config directory."""
        self.config_dir = config_dir or Path.home() / ".envswitch"
        self.config_file = self.config_dir / "envs.json"
        self._ensure_config_exists()

    def _ensure_config_exists(self) -> None:
        """Ensure config directory and file exist with valid structure."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            self._write_config({})

    def _read_config(self) -> Dict[str, Any]:
        """Read and return the configuration dictionary."""
        try:
            with open(self.config_file, "r") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise InvalidConfigError("Configuration must be a JSON object")
            return data
        except json.JSONDecodeError as e:
            raise InvalidConfigError(f"Invalid JSON in config file: {e}")

    def _write_config(self, config: Dict[str, Any]) -> None:
        """Write configuration dictionary to file."""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def list_envs(self) -> List[str]:
        """List all available environment names."""
        config = self._read_config()
        return list(config.keys())

    def get_env(self, name: str) -> Optional[Dict[str, Any]]:
        """Get environment configuration by name."""
        config = self._read_config()
        if name not in config:
            return None
        return config[name]

    def add_env(self, name: str, env_data: Dict[str, Any]) -> None:
        """Add or update an environment configuration."""
        config = self._read_config()
        config[name] = env_data
        self._write_config(config)

    def remove_env(self, name: str) -> bool:
        """Remove an environment configuration. Returns True if removed."""
        config = self._read_config()
        if name not in config:
            return False
        del config[name]
        self._write_config(config)
        return True

    def switch(self, name: str) -> Dict[str, Any]:
        """Switch to specified environment. Returns env config or raises error."""
        config = self._read_config()
        if name not in config:
            available = ", ".join(config.keys()) if config else "none"
            raise EnvironmentNotFoundError(
                f"Environment '{name}' not found. Available: {available}"
            )
        return config[name]

    def apply_env(self, env_data: Dict[str, Any]) -> None:
        """Apply environment variables to current process."""
        for key, value in env_data.get("env", {}).items():
            os.environ[key] = str(value)

    def run_with_env(self, name: str, command: List[str]) -> int:
        """Switch to environment and run command."""
        env_data = self.switch(name)
        self.apply_env(env_data)
        return os.execvpe(command[0], command, os.environ)
