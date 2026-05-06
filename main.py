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
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save the environment configurations."""
    init_config()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def add_env(name: str, path: str) -> None:
    """Add a new environment configuration."""
    config = load_config()
    if name in config:
        print(f"Error: Environment '{name}' already exists.")
        sys.exit(1)
    config[name] = {"path": path}
    save_config(config)
    print(f"Environment '{name}' added successfully.")


def remove_env(name: str) -> None:
    """Remove an existing environment configuration."""
    config = load_config()
    if name not in config:
        print(f"Error: Environment '{name}' not found.")
        sys.exit(1)
    del config[name]
    save_config(config)
    print(f"Environment '{name}' removed.")


def list_envs() -> None:
    """List all configured environments."""
    config = load_config()
    if not config:
        print("No environments configured.")
        return
    print("Configured Environments:")
    for env_name, details in config.items():
        print(f"  - {env_name}: {details.get('path', 'N/A')}")


def switch_env(name: str) -> None:
    """Switch to a specified environment (placeholder logic)."""
    config = load_config()
    if name not in config:
        print(f"Error: Environment '{name}' not found.")
        sys.exit(1)
    path = config[name].get("path", "")
    print(f"Switching to '{name}' (Path: {path})")
    # In a real scenario, this would export vars or modify .env files


def main() -> None:
    parser = argparse.ArgumentParser(description="EnvSwitch: Manage environment configurations")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Add subcommand
    add_parser = subparsers.add_parser("add", help="Add a new environment")
    add_parser.add_argument("name", type=str, help="Name of the environment")
    add_parser.add_argument("path", type=str, help="Path to the environment config")
    add_parser.set_defaults(func=add_env)

    # Remove subcommand
    remove_parser = subparsers.add_parser("remove", help="Remove an environment")
    remove_parser.add_argument("name", type=str, help="Name of the environment to delete")
    remove_parser.set_defaults(func=remove_env)

    # List subcommand
    list_parser = subparsers.add_parser("list", help="List all environments")
    list_parser.set_defaults(func=list_envs)

    # Switch subcommand
    switch_parser = subparsers.add_parser("switch", help="Switch to an environment")
    switch_parser.add_argument("name", type=str, help="Name of the environment to switch to")
    switch_parser.set_defaults(func=switch_env)

    args = parser.parse_args()

    if hasattr(args, "func"):
        if args.command == "add":
            args.func(args.name, args.path)
        elif args.command == "remove":
            args.func(args.name)
        elif args.command == "switch":
            args.func(args.name)
        elif args.command == "list":
            args.func()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()