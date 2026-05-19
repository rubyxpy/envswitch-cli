#!/usr/bin/env python3
"""Export environment variables to various formats.

This utility allows exporting current environment variables to different
formats like shell scripts, JSON, or dotenv files for easy sharing and
reproduction of environment configurations.
"""

import os
import json
import argparse
from typing import Dict, List, Optional


class EnvExporter:
    """Export environment variables to various formats."""

    def __init__(self, exclude_keys: Optional[List[str]] = None):
        """Initialize the exporter.
        
        Args:
            exclude_keys: List of environment variable names to exclude from export
        """
        self.exclude_keys = set(exclude_keys or [])
        # Add common sensitive keys to exclude by default
        self.exclude_keys.update([
            'PATH', 'HOME', 'USER', 'SHELL', 'TERM', 'PWD',
            'OLDPWD', 'SHLVL', 'LOGNAME', '_'
        ])

    def get_filtered_env(self) -> Dict[str, str]:
        """Get environment variables filtered by exclude list.
        
        Returns:
            Dictionary of environment variables after filtering
        """
        return {
            key: value for key, value in os.environ.items()
            if key not in self.exclude_keys
        }

    def to_shell(self, env_vars: Optional[Dict[str, str]] = None) -> str:
        """Export environment variables as shell script.
        
        Args:
            env_vars: Dictionary of environment variables to export.
                     If None, uses current filtered environment.
        
        Returns:
            Shell script content with export statements
        """
        if env_vars is None:
            env_vars = self.get_filtered_env()
        
        lines = ['#!/bin/bash', '# Environment variables export', '']
        for key, value in sorted(env_vars.items()):
            # Escape single quotes in values
            escaped_value = value.replace("'", "'\\''")
            lines.append(f"export {key}='{escaped_value}'")
        
        return '\n'.join(lines) + '\n'

    def to_json(self, env_vars: Optional[Dict[str, str]] = None, pretty: bool = True) -> str:
        """Export environment variables as JSON.
        
        Args:
            env_vars: Dictionary of environment variables to export.
                     If None, uses current filtered environment.
            pretty: Whether to format JSON with indentation
        
        Returns:
            JSON string representation of environment variables
        """
        if env_vars is None:
            env_vars = self.get_filtered_env()
        
        if pretty:
            return json.dumps(env_vars, indent=2, sort_keys=True) + '\n'
        return json.dumps(env_vars, sort_keys=True) + '\n'

    def to_dotenv(self, env_vars: Optional[Dict[str, str]] = None) -> str:
        """Export environment variables as .env file format.
        
        Args:
            env_vars: Dictionary of environment variables to export.
                     If None, uses current filtered environment.
        
        Returns:
            Dotenv file content
        """
        if env_vars is None:
            env_vars = self.get_filtered_env()
        
        lines = ['# Environment variables', '']
        for key, value in sorted(env_vars.items()):
            # Quote values that contain spaces or special characters
            if ' ' in value or '"' in value or '\n' in value:
                escaped_value = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                lines.append(f'{key}="{escaped_value}"')
            else:
                lines.append(f'{key}={value}')
        
        return '\n'.join(lines) + '\n'

    def to_yaml(self, env_vars: Optional[Dict[str, str]] = None) -> str:
        """Export environment variables as YAML.
        
        Args:
            env_vars: Dictionary of environment variables to export.
                     If None, uses current filtered environment.
        
        Returns:
            YAML string representation of environment variables
        """
        if env_vars is None:
            env_vars = self.get_filtered_env()
        
        lines = ['# Environment variables', 'environment:']
        for key, value in sorted(env_vars.items()):
            # Properly quote and escape YAML values
            if ':' in value or '#' in value or value.startswith(' ') or value.endswith(' '):
                escaped_value = value.replace('"', '\\"')
                lines.append(f'  {key}: "{escaped_value}"')
            else:
                lines.append(f'  {key}: {value}')
        
        return '\n'.join(lines) + '\n'


def main():
    """Main entry point for the export utility."""
    parser = argparse.ArgumentParser(
        description='Export environment variables to various formats'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['shell', 'json', 'dotenv', 'yaml'],
        default='dotenv',
        help='Output format (default: dotenv)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path (default: stdout)'
    )
    parser.add_argument(
        '-e', '--exclude',
        type=str,
        nargs='+',
        help='Additional environment variables to exclude'
    )
    parser.add_argument(
        '--include-system',
        action='store_true',
        help='Include system variables (PATH, HOME, etc.)'
    )

    args = parser.parse_args()

    # Initialize exporter
    exclude_keys = args.exclude or []
    if args.include_system:
        exclude_keys = exclude_keys  # Don't add system vars to exclude
        exporter = EnvExporter(exclude_keys=exclude_keys if exclude_keys else [])
    else:
        exporter = EnvExporter(exclude_keys=exclude_keys)

    # Generate output based on format
    format_map = {
        'shell': exporter.to_shell,
        'json': exporter.to_json,
        'dotenv': exporter.to_dotenv,
        'yaml': exporter.to_yaml
    }

    output_content = format_map[args.format]()

    # Write to file or stdout
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_content)
        print(f"Environment exported to {args.output} ({args.format} format)")
    else:
        print(output_content, end='')


if __name__ == '__main__':
    main()
