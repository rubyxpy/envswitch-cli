#!/usr/bin/env python3
"""Backup and restore utility for environment files.

Provides functionality to create timestamped backups of .env files
and restore from previous backups.
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class EnvBackup:
    """Handle backing up and restoring environment files."""

    def __init__(self, backup_dir: str = ".env_backups"):
        """Initialize the backup manager.
        
        Args:
            backup_dir: Directory to store backups (default: .env_backups)
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self, env_file: str = ".env") -> Optional[str]:
        """Create a timestamped backup of an environment file.
        
        Args:
            env_file: Path to the environment file to backup
            
        Returns:
            Path to the backup file, or None if source doesn't exist
        """
        source = Path(env_file)
        if not source.exists():
            print(f"Error: {env_file} does not exist")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source.name}.{timestamp}.backup"
        backup_path = self.backup_dir / backup_name

        try:
            shutil.copy2(source, backup_path)
            print(f"Backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None

    def list_backups(self, env_file: str = ".env") -> List[Path]:
        """List all backups for a given environment file.
        
        Args:
            env_file: Name of the environment file to find backups for
            
        Returns:
            List of backup file paths, sorted by modification time (newest first)
        """
        pattern = f"{env_file}.*.backup"
        backups = sorted(
            self.backup_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return backups

    def restore_backup(self, backup_file: str, target: str = ".env") -> bool:
        """Restore an environment file from a backup.
        
        Args:
            backup_file: Path to the backup file to restore
            target: Path where to restore the file (default: .env)
            
        Returns:
            True if restore was successful, False otherwise
        """
        backup_path = Path(backup_file)
        if not backup_path.exists():
            print(f"Error: Backup file {backup_file} does not exist")
            return False

        target_path = Path(target)
        
        # Create backup of current file before restoring
        if target_path.exists():
            self.create_backup(target)

        try:
            shutil.copy2(backup_path, target_path)
            print(f"Restored {target} from {backup_file}")
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

    def cleanup_old_backups(self, keep_count: int = 10, env_file: str = ".env") -> int:
        """Remove old backups, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent backups to keep
            env_file: Name of the environment file to clean backups for
            
        Returns:
            Number of backups deleted
        """
        backups = self.list_backups(env_file)
        to_delete = backups[keep_count:]
        
        deleted_count = 0
        for backup in to_delete:
            try:
                backup.unlink()
                deleted_count += 1
                print(f"Deleted old backup: {backup.name}")
            except Exception as e:
                print(f"Error deleting {backup.name}: {e}")
        
        return deleted_count


def main():
    """Command-line interface for environment backup utility."""
    if len(sys.argv) < 2:
        print("Usage: python backup_env.py <command> [args]")
        print("Commands:")
        print("  backup [file]           - Create backup of environment file")
        print("  list [file]             - List available backups")
        print("  restore <backup> [file] - Restore from backup")
        print("  cleanup [count] [file]  - Remove old backups (keep N recent)")
        sys.exit(1)

    command = sys.argv[1]
    backup_manager = EnvBackup()

    if command == "backup":
        env_file = sys.argv[2] if len(sys.argv) > 2 else ".env"
        backup_manager.create_backup(env_file)

    elif command == "list":
        env_file = sys.argv[2] if len(sys.argv) > 2 else ".env"
        backups = backup_manager.list_backups(env_file)
        if backups:
            print(f"Available backups for {env_file}:")
            for i, backup in enumerate(backups, 1):
                mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                print(f"  {i}. {backup.name} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")
        else:
            print(f"No backups found for {env_file}")

    elif command == "restore":
        if len(sys.argv) < 3:
            print("Error: Please specify backup file to restore")
            sys.exit(1)
        backup_file = sys.argv[2]
        target = sys.argv[3] if len(sys.argv) > 3 else ".env"
        backup_manager.restore_backup(backup_file, target)

    elif command == "cleanup":
        keep_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        env_file = sys.argv[3] if len(sys.argv) > 3 else ".env"
        deleted = backup_manager.cleanup_old_backups(keep_count, env_file)
        print(f"Cleanup complete: {deleted} backup(s) deleted")

    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
