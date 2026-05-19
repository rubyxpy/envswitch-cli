#!/usr/bin/env python3
"""EnvSwitch - Environment variable management library."""

import os
import json
from typing import Dict, Optional, List
from pathlib import Path


class EnvSwitch:
    """Manages environment variable switching and profiles."""

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize EnvSwitch with optional config directory.
        
        Args:
            config_dir: Directory to store environment profiles. 
                       Defaults to ~/.envswitch
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".envswitch"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_dir = self.config_dir / "profiles"
        self.profiles_dir.mkdir(exist_ok=True)

    def save_profile(self, profile_name: str, env_vars: Dict[str, str]) -> None:
        """Save environment variables to a named profile.
        
        Args:
            profile_name: Name of the profile to save
            env_vars: Dictionary of environment variables to save
        """
        profile_path = self.profiles_dir / f"{profile_name}.json"
        with open(profile_path, 'w') as f:
            json.dump(env_vars, f, indent=2)

    def load_profile(self, profile_name: str) -> Dict[str, str]:
        """Load environment variables from a named profile.
        
        Args:
            profile_name: Name of the profile to load
            
        Returns:
            Dictionary of environment variables
            
        Raises:
            FileNotFoundError: If profile does not exist
        """
        profile_path = self.profiles_dir / f"{profile_name}.json"
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile '{profile_name}' not found")
        
        with open(profile_path, 'r') as f:
            return json.load(f)

    def apply_profile(self, profile_name: str) -> None:
        """Apply a profile by setting environment variables.
        
        Args:
            profile_name: Name of the profile to apply
        """
        env_vars = self.load_profile(profile_name)
        for key, value in env_vars.items():
            os.environ[key] = value

    def list_profiles(self) -> List[str]:
        """List all available profiles.
        
        Returns:
            List of profile names
        """
        profiles = []
        for profile_file in self.profiles_dir.glob("*.json"):
            profiles.append(profile_file.stem)
        return sorted(profiles)

    def delete_profile(self, profile_name: str) -> None:
        """Delete a profile.
        
        Args:
            profile_name: Name of the profile to delete
            
        Raises:
            FileNotFoundError: If profile does not exist
        """
        profile_path = self.profiles_dir / f"{profile_name}.json"
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile '{profile_name}' not found")
        
        profile_path.unlink()

    def get_current_env(self, keys: Optional[List[str]] = None) -> Dict[str, str]:
        """Get current environment variables.
        
        Args:
            keys: Optional list of specific keys to retrieve.
                 If None, returns all environment variables.
                 
        Returns:
            Dictionary of environment variables
        """
        if keys:
            return {key: os.environ.get(key, "") for key in keys}
        return dict(os.environ)

    def export_profile(self, profile_name: str, export_path: str) -> None:
        """Export a profile to a specified file path.
        
        Args:
            profile_name: Name of the profile to export
            export_path: File path to export to
        """
        env_vars = self.load_profile(profile_name)
        export_file = Path(export_path)
        with open(export_file, 'w') as f:
            json.dump(env_vars, f, indent=2)

    def import_profile(self, profile_name: str, import_path: str) -> None:
        """Import a profile from a specified file path.
        
        Args:
            profile_name: Name to save the imported profile as
            import_path: File path to import from
            
        Raises:
            FileNotFoundError: If import file does not exist
            json.JSONDecodeError: If import file is not valid JSON
        """
        import_file = Path(import_path)
        if not import_file.exists():
            raise FileNotFoundError(f"Import file '{import_path}' not found")
        
        with open(import_file, 'r') as f:
            env_vars = json.load(f)
        
        self.save_profile(profile_name, env_vars)
