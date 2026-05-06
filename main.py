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
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save the environment configurations."""
    init_config()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        f.write("\n")


def cmd_add(args: argparse.Namespace) -> int:
    """Add or update an environment configuration."""
    config = load_config()
    config[args.name] = args.pairs
    save_config(config)
    print(f"Environment '{args.name}' added successfully.")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List all saved environments."""
    config = load_config()
    if not config:
        print("No environments saved.")
        return 0
    print("Saved environments:")
    for name in config:
        print(f"  - {name}")
    return 0


def cmd_switch(args: argparse.Namespace) -> int:
    """Switch to a saved environment configuration."""
    config = load_config()
    if args.name not in config:
        print(f"Error: Environment '{args.name}' not found.", file=sys.stderr)
        return 1
    env_vars = config[args.name]
    print(f"Switching to '{args.name}'...")
    for key, value in env_vars.items():
        print(f"export {key}=\"{value}\"")
    return 0


def main() -> int:
    """Main entry point for the CLI."""
    init_config()
    parser = argparse.ArgumentParser(
        prog="envswitch",
        description="Manage and switch between environment configurations."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    add_parser = subparsers.add_parser("add", help="Add a new environment")
    add_parser.add_argument("name", help="Environment name")
    add_parser.add_argument("pairs", nargs="+", help="KEY=VALUE pairs")
    add_parser.set_defaults(func=cmd_add)

    subparsers.add_parser("list", help="List saved environments").set_defaults(func=cmd_list)

    switch_parser = subparsers.add_parser("switch", help="Switch to an environment")
    switch_parser.add_argument("name", help="Environment name")
    switch_parser.set_defaults(func=cmd_switch)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    if args.command == "add":
        parsed_vars: Dict[str, str] = {}
        for item in args.pairs:
            if "=" in item:
                k, v = item.split("=", 1)
                parsed_vars[k] = v
            else:
                print(f"Error: Invalid format '{item}'. Use KEY=VALUE.", file=sys.stderr)
                return 1
        args.pairs = parsed_vars

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
