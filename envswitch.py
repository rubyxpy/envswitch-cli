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
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            self._write_config({"environments": {}})

    def _read_config(self) -> Dict[str, Any]:
        """Read and parse configuration file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidConfigError(f"Invalid JSON in config file: {e}")
        except FileNotFoundError:
            raise ConfigNotFoundError(f"Config file not found: {self.config_file}")

    def _write_config(self, config: Dict[str, Any]) -> None:
        """Write configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def add_environment(self, name: str, variables: Dict[str, str]) -> None:
        """Add or update an environment configuration."""
        if not name:
            raise ValueError("Environment name cannot be empty")
        if not isinstance(variables, dict):
            raise ValueError("Variables must be a dictionary")
        
        config = self._read_config()
        config["environments"][name] = variables
        self._write_config(config)

    def get_environment(self, name: str) -> Dict[str, str]:
        """Get environment variables for a specific environment."""
        config = self._read_config()
        if name not in config["environments"]:
            raise EnvironmentNotFoundError(f"Environment '{name}' not found")
        return config["environments"][name]

    def list_environments(self) -> List[str]:
        """List all configured environments."""
        config = self._read_config()
        return list(config["environments"].keys())

    def remove_environment(self, name: str) -> None:
        """Remove an environment configuration."""
        config = self._read_config()
        if name not in config["environments"]:
            raise EnvironmentNotFoundError(f"Environment '{name}' not found")
        del config["environments"][name]
        self._write_config(config)

    def switch_environment(self, name: str) -> Dict[str, str]:
        """Switch to specified environment and return variables to set."""
        return self.get_environment(name)

    def export_environment(self, name: str, format: str = "shell") -> str:
        """Export environment variables in specified format."""
        variables = self.get_environment(name)
        
        if format == "shell":
            lines = [f"export {key}='{value}'" for key, value in variables.items()]
            return "\n".join(lines)
        elif format == "json":
            return json.dumps(variables, indent=2)
        elif format == "dotenv":
            lines = [f"{key}={value}" for key, value in variables.items()]
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")
