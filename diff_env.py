#!/usr/bin/env python3
"""Environment variable diff utility for EnvSwitch.

Compares two environment snapshots and shows differences.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Set, Tuple


class EnvDiff:
    """Compare and diff environment variable snapshots."""

    def __init__(self, env1: Dict[str, str], env2: Dict[str, str]):
        """Initialize with two environment dictionaries.
        
        Args:
            env1: First environment snapshot (e.g., 'before')
            env2: Second environment snapshot (e.g., 'after')
        """
        self.env1 = env1
        self.env2 = env2

    def get_added(self) -> Dict[str, str]:
        """Get variables added in env2."""
        return {k: v for k, v in self.env2.items() if k not in self.env1}

    def get_removed(self) -> Dict[str, str]:
        """Get variables removed from env1."""
        return {k: v for k, v in self.env1.items() if k not in self.env2}

    def get_modified(self) -> Dict[str, Tuple[str, str]]:
        """Get variables with modified values.
        
        Returns:
            Dict mapping variable name to (old_value, new_value)
        """
        modified = {}
        common_keys = set(self.env1.keys()) & set(self.env2.keys())
        for key in common_keys:
            if self.env1[key] != self.env2[key]:
                modified[key] = (self.env1[key], self.env2[key])
        return modified

    def get_unchanged(self) -> Set[str]:
        """Get variables that exist in both with same values."""
        common_keys = set(self.env1.keys()) & set(self.env2.keys())
        return {k for k in common_keys if self.env1[k] == self.env2[k]}

    def summary(self) -> Dict[str, int]:
        """Get summary statistics of the diff."""
        return {
            "added": len(self.get_added()),
            "removed": len(self.get_removed()),
            "modified": len(self.get_modified()),
            "unchanged": len(self.get_unchanged())
        }

    def format_diff(self, show_unchanged: bool = False) -> str:
        """Format diff as human-readable string.
        
        Args:
            show_unchanged: Whether to show unchanged variables
            
        Returns:
            Formatted diff string
        """
        lines = []
        lines.append("Environment Diff")
        lines.append("=" * 50)
        
        added = self.get_added()
        if added:
            lines.append("\n[ADDED]")
            for key, value in sorted(added.items()):
                lines.append(f"+ {key}={value}")
        
        removed = self.get_removed()
        if removed:
            lines.append("\n[REMOVED]")
            for key, value in sorted(removed.items()):
                lines.append(f"- {key}={value}")
        
        modified = self.get_modified()
        if modified:
            lines.append("\n[MODIFIED]")
            for key, (old_val, new_val) in sorted(modified.items()):
                lines.append(f"~ {key}")
                lines.append(f"  - {old_val}")
                lines.append(f"  + {new_val}")
        
        if show_unchanged:
            unchanged = self.get_unchanged()
            if unchanged:
                lines.append("\n[UNCHANGED]")
                for key in sorted(unchanged):
                    lines.append(f"  {key}={self.env1[key]}")
        
        summary = self.summary()
        lines.append("\n" + "=" * 50)
        lines.append(f"Summary: +{summary['added']} ~{summary['modified']} "
                    f"-{summary['removed']} ={summary['unchanged']}")
        
        return "\n".join(lines)


def load_env_file(filepath: str) -> Dict[str, str]:
    """Load environment variables from JSON file.
    
    Args:
        filepath: Path to JSON file containing environment variables
        
    Returns:
        Dictionary of environment variables
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(path, 'r') as f:
        data = json.load(f)
    
    # Handle both direct dict and wrapped format
    if isinstance(data, dict):
        if 'variables' in data:
            return data['variables']
        return data
    
    raise ValueError(f"Invalid environment file format: {filepath}")


def main():
    """CLI interface for environment diff utility."""
    if len(sys.argv) < 3:
        print("Usage: python diff_env.py <env1.json> <env2.json> [--show-unchanged]")
        print("\nCompare two environment snapshots and show differences.")
        sys.exit(1)
    
    env1_path = sys.argv[1]
    env2_path = sys.argv[2]
    show_unchanged = "--show-unchanged" in sys.argv
    
    try:
        env1 = load_env_file(env1_path)
        env2 = load_env_file(env2_path)
        
        differ = EnvDiff(env1, env2)
        print(differ.format_diff(show_unchanged=show_unchanged))
        
        # Exit with non-zero if there are differences
        summary = differ.summary()
        if summary['added'] > 0 or summary['removed'] > 0 or summary['modified'] > 0:
            sys.exit(1)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file - {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
