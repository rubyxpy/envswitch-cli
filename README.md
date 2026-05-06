# EnvSwitch CLI

Manage and switch between environment configurations via the command line.

## Overview

EnvSwitch is a lightweight tool designed to help developers organize and swap between different environment presets. It uses JSON for configuration storage, persisting data to `~/.envswitch/envs.json`.

## Features

- **JSON Persistence**: All environments are stored in a standard `envs.json` file.
- **Type Safety**: Built with Python 3.13+ type hints and strict annotation support.
- **CLI Management**: Add, list, and switch configurations using `argparse`.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rubyxpy/envswitch-cli.git
   cd envswitch-cli
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

## Usage

EnvSwitch exposes standard commands to manage your state:

```bash
# Add a new environment configuration
envswitch add <environment_name>

# List all available configurations
envswitch list

# Switch active configuration
envswitch switch <environment_name>
```

## Configuration

The CLI initializes a configuration directory at `~/.envswitch/` upon first run. The structure is maintained automatically by `main.py`.

## Development

- **Python Version**: 3.13+
- **Type Hints**: Enforced via `from __future__ import annotations`
- **Related**: PR #1 addresses missing type hints and completes the CLI implementation.

## Contributing

Please review existing issues and ensure all code adheres to the existing type-hinting standards before submitting a pull request.>