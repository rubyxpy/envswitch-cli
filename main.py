#!/usr/bin/env python3
"""EnvSwitch - Manage and switch between environment configurations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

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
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save the environment configurations."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def add_env(name: str, vars_dict: Dict[str, str]) -> None:
    """Add or update an environment configuration."""
    config = load_config()
    config[name] = vars_dict
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
        print(f"Environment '{name}' not found.")
        sys.exit(1)


def list_envs() -> None:
    """List all stored environment configurations."""
    config = load_config()
    if not config:
        print("No environments stored.")
        return
    for name in config:
        print(f"- {name}")


def parse_vars(args: List[str]) -> Dict[str, str]:
    """Parse key=value pairs from command line arguments."""
    result: Dict[str, str] = {}
    for item in args:
        if "=" in item:
            k, v = item.split("=", 1)
            result[k] = v
    return result


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="EnvSwitch CLI")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add or update an environment")
    add_parser.add_argument("name", help="Environment name")
    add_parser.add_argument("vars", help="Variables as key=value pairs", nargs="*")

    remove_parser = subparsers.add_parser("remove", help="Remove an environment")
    remove_parser.add_argument("name", help="Environment name")

    subparsers.add_parser("list", help="List all environments")

    args = parser.parse_args()

    if args.command == "add":
        vars_dict = parse_vars(args.vars or [])
        add_env(args.name, vars_dict)
    elif args.command == "remove":
        remove_env(args.name)
    elif args.command == "list":
        list_envs()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()