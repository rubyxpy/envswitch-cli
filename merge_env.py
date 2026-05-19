#!/usr/bin/env python3
"""Merge multiple environment variable sets into one."""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List


def load_env_file(file_path: Path) -> Dict[str, str]:
    """Load environment variables from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError(f"Invalid format in {file_path}: expected JSON object")
            return {k: str(v) for k, v in data.items()}
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def merge_environments(env_files: List[Path], strategy: str = 'last') -> Dict[str, str]:
    """Merge multiple environment variable files.
    
    Args:
        env_files: List of paths to environment JSON files
        strategy: Merge strategy - 'last' (last wins), 'first' (first wins)
    
    Returns:
        Merged environment dictionary
    """
    merged = {}
    
    if strategy == 'last':
        # Last file wins on conflicts
        for env_file in env_files:
            env_vars = load_env_file(env_file)
            merged.update(env_vars)
    elif strategy == 'first':
        # First file wins on conflicts
        for env_file in env_files:
            env_vars = load_env_file(env_file)
            for key, value in env_vars.items():
                if key not in merged:
                    merged[key] = value
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    return merged


def save_merged_env(merged: Dict[str, str], output_path: Path) -> None:
    """Save merged environment to a JSON file."""
    try:
        with open(output_path, 'w') as f:
            json.dump(merged, f, indent=2, sort_keys=True)
        print(f"Merged environment saved to: {output_path}")
    except Exception as e:
        print(f"Error saving merged environment: {e}", file=sys.stderr)
        sys.exit(1)


def print_merge_summary(env_files: List[Path], merged: Dict[str, str]) -> None:
    """Print a summary of the merge operation."""
    print(f"\nMerged {len(env_files)} environment file(s):")
    for env_file in env_files:
        print(f"  - {env_file}")
    print(f"\nTotal variables in merged environment: {len(merged)}")
    
    # Show potential conflicts if multiple files
    if len(env_files) > 1:
        all_keys = set()
        for env_file in env_files:
            env_vars = load_env_file(env_file)
            all_keys.update(env_vars.keys())
        
        conflicts = len(all_keys) - len(merged)
        if conflicts > 0:
            print(f"Variables overwritten during merge: {conflicts}")


def main():
    parser = argparse.ArgumentParser(
        description='Merge multiple environment variable files into one',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge two environment files (last file wins)
  python merge_env.py dev.json prod.json -o merged.json
  
  # Merge with first-wins strategy
  python merge_env.py base.json override.json -o final.json --strategy first
  
  # Merge multiple files
  python merge_env.py base.json dev.json local.json -o combined.json
        """
    )
    
    parser.add_argument(
        'env_files',
        nargs='+',
        type=Path,
        help='Environment JSON files to merge (in order of priority)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        required=True,
        help='Output file path for merged environment'
    )
    
    parser.add_argument(
        '-s', '--strategy',
        choices=['last', 'first'],
        default='last',
        help='Merge strategy: last (default, later files override) or first (earlier files take precedence)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress summary output'
    )
    
    args = parser.parse_args()
    
    # Validate input files exist
    for env_file in args.env_files:
        if not env_file.exists():
            print(f"Error: File does not exist: {env_file}", file=sys.stderr)
            sys.exit(1)
    
    # Merge environments
    merged = merge_environments(args.env_files, args.strategy)
    
    # Save merged environment
    save_merged_env(merged, args.output)
    
    # Print summary
    if not args.quiet:
        print_merge_summary(args.env_files, merged)


if __name__ == '__main__':
    main()
