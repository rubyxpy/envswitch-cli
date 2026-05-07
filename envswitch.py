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
        self._ensure_config_exists()

    def _ensure_config_exists(self) -> None:
        """Ensure config directory and file exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            self._save_config({})

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            raise InvalidConfigError(f"Invalid JSON in config file: {e}")

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def list_envs(self) -> List[str]:
        """List all saved environment names."""
        config = self._load_config()
        return list(config.keys())

    def current_env(self) -> Optional[str]:
        """Get the currently active environment name."""
        config = self._load_config()
        return config.get("_current")

    def add_env(self, name: str, variables: Dict[str, str]) -> None:
        """Add a new environment configuration."""
        config = self._load_config()
        if not name or not isinstance(name, str):
            raise InvalidConfigError("Environment name must be a non-empty string")
        if not isinstance(variables, dict):
            raise InvalidConfigError("Variables must be a dictionary")
        config[name] = {"variables": variables}
        self._save_config(config)

    def remove_env(self, name: str) -> None:
        """Remove an environment configuration."""
        config = self._load_config()
        if name not in config:
            raise EnvironmentNotFoundError(f"Environment '{name}' does not exist")
        if name == "_current":
            raise InvalidConfigError("Cannot remove the _current metadata key")
        del config[name]
        # Clear current if it was the removed env
        if config.get("_current") == name:
            config["_current"] = None
        self._save_config(config)

    def switch_env(self, name: str) -> None:
        """Switch to a different environment and set variables."""
        config = self._load_config()
        if name not in config:
            raise EnvironmentNotFoundError(f"Environment '{name}' does not exist")
        
        env_data = config[name]
        variables = env_data.get("variables", {})
        
        # Set environment variables
        for key, value in variables.items():
            os.environ[key] = value
        
        # Update current environment
        config["_current"] = name
        self._save_config(config)

    def get_env(self, name: str) -> Optional[Dict[str, str]]:
        """Get environment variables for a given environment."""
        config = self._load_config()
        if name not in config:
            return None
        return config[name].get("variables", {})

    def export_env(self, name: str, output_file: Path) -> None:
        """Export environment variables to a shell script."""
        variables = self.get_env(name)
        if variables is None:
            raise EnvironmentNotFoundError(f"Environment '{name}' does not exist")
        
        with open(output_file, "w") as f:
            f.write("#!/bin/bash\n")
            for key, value in variables.items():
                # Escape single quotes in value
                escaped_value = value.replace("'", "'\\''")
                f.write(f"export {key}='{escaped_value}'\n")


if __name__ == "__main__":
    # Simple test interface
    es = EnvSwitch()
    print(f"Config directory: {es.config_dir}")
    print(f"Available environments: {es.list_envs()}")
    print(f"Current environment: {es.current_env()}")
