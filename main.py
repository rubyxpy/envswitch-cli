#!/usr/bin/env python3
"""EnvSwitch - Manage and switch between environment configurations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path.home() / ".envswitch"
CONFIG_FILE = CONFIG_DIR / "envs.json"


def init_config() -> None:
    """Initialize the configuration directory and file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_config({})


def load_config() -> Dict[str, Any]:
    """Load the environment configurations."""
    init_config()
    try:
        with open(CONFIG_FILE, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save the environment configurations."""
    init_config()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def add_env(name: str, variables: Dict[str, str]) -> None:
    """Add or update an environment configuration."""
    config = load_config()
    config[name] = variables
    save_config(config)
    print(f"Environment '{name}' added/updated.")


def remove_env(name: str) -> None:
    """Remove an environment configuration."""
    config = load_config()
    if name in config:
        del config[name]
        save_config(config)
        print(f"Environment '{name}' removed.")
    else:
        print(f"Environment '{name}' not found.", file=sys.stderr)
        sys.exit(1)


def list_envs() -> None:
    """List all saved environments."""
    config = load_config()
    if not config:
        print("No environments configured.")
        return
    print("Configured environments:")
    for name in config:
        print(f"  - {name}")


def switch_env(name: str) -> None:
    """Switch to a specified environment and export variables."""
    config = load_config()
    if name not in config:
        print(f"Error: Environment '{name}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    exports = []
    for key, value in config[name].items():
        safe_value = value.replace("'", "'\"'\"'")
        exports.append(f"export {key}='{safe_value}'")
    
    print("\n".join(exports))


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage and switch between environment configurations.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    add_parser = subparsers.add_parser("add", help="Add/update an environment")
    add_parser.add_argument("name", help="Environment name")
    add_parser.add_argument("key_values", nargs="+", help="Key=value pairs")
    
    remove_parser = subparsers.add_parser("remove", help="Remove an environment")
    remove_parser.add_argument("name", help="Environment name")
    
    subparsers.add_parser("list", help="List all environments")
    
    switch_parser = subparsers.add_parser("switch", help="Switch to an environment")
    switch_parser.add_argument("name", help="Environment name")
    
    args = parser.parse_args()
    
    if args.command == "add":
        variables: Dict[str, str] = {}
        for kv in args.key_values:
            if "=" not in kv:
                print(f"Invalid format '{kv}'. Use KEY=VALUE.", file=sys.stderr)
                sys.exit(1)
            k, v = kv.split("=", 1)
            variables[k] = v
        add_env(args.name, variables)
    elif args.command == "remove":
        remove_env(args.name)
    elif args.command == "list":
        list_envs()
    elif args.command == "switch":
        switch_env(args.name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()