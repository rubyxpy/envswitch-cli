#!/usr/bin/env python3
"""EnvSwitch - Manage and switch between environment configurations."""

import argparse
import json
import os
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".envswitch"
CONFIG_FILE = CONFIG_DIR / "envs.json"


def init_config():
    """Initialize the configuration directory and file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_config({})


def load_config() -> dict:
    """Load the environment configurations."""
    init_config()
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_config(config: dict):
    """Save the environment configurations."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def add_env(name: str, vars_dict: dict):
    """Add or update an environment configuration."""
    config = load_config()
    config[name] = vars_dict
    save_config(config)
    print(f"Added/updated environment: {name}")


def list_envs():
    """List all saved environments."""
    config = load_config()
    if not config:
        print("No environments configured. Use 'add' to create one.")
        return
    print("Configured environments:")
    for name in config:
        print(f"  - {name}")


def switch_env(name: str):
    """Print commands to switch to an environment."""
    config = load_config()
    if name not in config:
        print(f"Error: Environment '{name}' not found.")
        sys.exit(1)
    
    env_vars = config[name]
    print(f"# Environment: {name}")
    for key, value in env_vars.items():
        print(f"export {key}="{value}" ")


def show_env(name: str):
    """Show environment variables for a configuration."""
    config = load_config()
    if name not in config:
        print(f"Error: Environment '{name}' not found.")
        sys.exit(1)
    
    env_vars = config[name]
    print(f"Environment: {name}")
    for key, value in env_vars.items():
        print(f"  {key}={value}")


def remove_env(name: str):
    """Remove an environment configuration."""
    config = load_config()
    if name not in config:
        print(f"Error: Environment '{name}' not found.")
        sys.exit(1)
    del config[name]
    save_config(config)
    print(f"Removed environment: {name}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage and switch between environment configurations"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add or update an environment")
    add_parser.add_argument("name", help="Name of the environment")
    add_parser.add_argument("variables", nargs="+", help="KEY=VALUE pairs")
    
    # List command
    subparsers.add_parser("list", help="List all environments")
    
    # Switch command
    switch_parser = subparsers.add_parser("switch", help="Generate export commands")
    switch_parser.add_argument("name", help="Name of the environment")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show environment variables")
    show_parser.add_argument("name", help="Name of the environment")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove an environment")
    remove_parser.add_argument("name", help="Name of the environment")
    
    args = parser.parse_args()
    
    if args.command == "add":
        vars_dict = {}
        for var in args.variables:
            if "=" not in var:
                print(f"Error: Invalid format '{var}', use KEY=VALUE")
                sys.exit(1)
            key, value = var.split("=", 1)
            vars_dict[key] = value
        add_env(args.name, vars_dict)
    elif args.command == "list":
        list_envs()
    elif args.command == "switch":
        switch_env(args.name)
    elif args.command == "show":
        show_env(args.name)
    elif args.command == "remove":
        remove_env(args.name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
