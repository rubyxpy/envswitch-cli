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


class EnvSwitch:
    """Core class for managing environment configurations."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialize EnvSwitch with optional custom config directory."""
        self.config_dir = config_dir or Path.home() / ".envswitch"
        self.config_file = self.config_dir / "envs.json"
        self._ensure_config_exists()

    def _ensure_config_exists(self) -> None:
        """Ensure configuration directory and file exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            self._save_config({})

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                config = json.loads(content)
                if not isinstance(config, dict):
                    raise InvalidConfigError("Configuration must be a JSON object")
                return config
        except json.JSONDecodeError as e:
            raise InvalidConfigError(f"Invalid JSON in config file: {e}")
        except (FileNotFoundError, PermissionError) as e:
            raise EnvSwitchError(f"Cannot read config file: {e}")

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except (PermissionError, OSError) as e:
            raise EnvSwitchError(f"Cannot write config file: {e}")

    def add_environment(self, name: str, env_vars: Dict[str, str]) -> None:
        """Add or update an environment configuration."""
        if not name or not name.strip():
            raise ValueError("Environment name cannot be empty")
        if not isinstance(env_vars, dict):
            raise ValueError("Environment variables must be a dictionary")
        
        config = self._load_config()
        config[name] = env_vars
        self._save_config(config)

    def remove_environment(self, name: str) -> None:
        """Remove an environment configuration."""
        config = self._load_config()
        if name not in config:
            raise ConfigNotFoundError(f"Environment '{name}' not found")
        
        del config[name]
        self._save_config(config)

    def get_environment(self, name: str) -> Dict[str, str]:
        """Get environment variables for a specific configuration."""
        config = self._load_config()
        if name not in config:
            raise ConfigNotFoundError(f"Environment '{name}' not found")
        return config[name]

    def list_environments(self) -> List[str]:
        """List all available environment names."""
        config = self._load_config()
        return sorted(config.keys())

    def apply_environment(self, name: str) -> Dict[str, str]:
        """Apply environment variables to current process."""
        env_vars = self.get_environment(name)
        for key, value in env_vars.items():
            os.environ[key] = value
        return env_vars

    def export_environment(self, name: str, format: str = "bash") -> str:
        """Export environment variables as shell commands."""
        env_vars = self.get_environment(name)
        
        if format == "bash" or format == "sh":
            lines = [f"export {key}='{value}'" for key, value in env_vars.items()]
            return "\n".join(lines)
        elif format == "fish":
            lines = [f"set -x {key} '{value}'" for key, value in env_vars.items()]
            return "\n".join(lines)
        elif format == "powershell":
            lines = [f"$env:{key} = '{value}'" for key, value in env_vars.items()]
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def validate_environment(self, name: str) -> bool:
        """Validate that an environment configuration exists and is valid."""
        try:
            env_vars = self.get_environment(name)
            return isinstance(env_vars, dict) and all(
                isinstance(k, str) and isinstance(v, str) 
                for k, v in env_vars.items()
            )
        except ConfigNotFoundError:
            return False
