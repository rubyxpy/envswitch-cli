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
        """Ensure the config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {}
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidConfigError(f"Invalid JSON in config file: {e}")

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def create_environment(self, name: str, variables: Dict[str, str]) -> None:
        """Create a new environment with given variables."""
        config = self._load_config()
        if name in config:
            raise EnvSwitchError(f"Environment '{name}' already exists")
        config[name] = {"variables": variables, "active": False}
        self._save_config(config)

    def switch(self, name: str) -> None:
        """Switch to specified environment."""
        config = self._load_config()
        if name not in config:
            raise EnvironmentNotFoundError(f"Environment '{name}' not found")
        
        # Deactivate all environments
        for env_name in config:
            config[env_name]["active"] = False
        
        # Activate the target environment
        config[name]["active"] = True
        self._save_config(config)
        
        # Export variables to current shell
        for key, value in config[name]["variables"].items():
            os.environ[key] = value

    def list_environments(self) -> List[str]:
        """List all environments."""
        config = self._load_config()
        return list(config.keys())

    def get_active_environment(self) -> Optional[str]:
        """Get the currently active environment name."""
        config = self._load_config()
        for name, env_config in config.items():
            if env_config.get("active", False):
                return name
        return None

    def remove_environment(self, name: str) -> None:
        """Remove an environment."""
        config = self._load_config()
        if name not in config:
            raise EnvironmentNotFoundError(f"Environment '{name}' not found")
        del config[name]
        self._save_config(config)

    def get_variables(self, name: str) -> Dict[str, str]:
        """Get variables for a specific environment."""
        config = self._load_config()
        if name not in config:
            raise EnvironmentNotFoundError(f"Environment '{name}' not found")
        return config[name].get("variables", {})
