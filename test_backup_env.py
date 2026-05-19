import unittest
import os
import tempfile
import shutil
from datetime import datetime
from backup_env import backup_environment, restore_environment, list_backups


class TestBackupEnv(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory for test backups."""
        self.test_dir = tempfile.mkdtemp()
        self.original_backup_dir = os.environ.get('ENVSWITCH_BACKUP_DIR')
        os.environ['ENVSWITCH_BACKUP_DIR'] = self.test_dir

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        if self.original_backup_dir:
            os.environ['ENVSWITCH_BACKUP_DIR'] = self.original_backup_dir
        elif 'ENVSWITCH_BACKUP_DIR' in os.environ:
            del os.environ['ENVSWITCH_BACKUP_DIR']

    def test_backup_environment(self):
        """Test backing up environment variables."""
        # Set some test environment variables
        os.environ['TEST_VAR_1'] = 'value1'
        os.environ['TEST_VAR_2'] = 'value2'
        
        backup_name = backup_environment('test_backup')
        self.assertIsNotNone(backup_name)
        
        # Verify backup file exists
        backup_files = os.listdir(self.test_dir)
        self.assertEqual(len(backup_files), 1)
        self.assertTrue(backup_files[0].startswith('test_backup'))
        self.assertTrue(backup_files[0].endswith('.env'))

    def test_backup_with_filter(self):
        """Test backing up filtered environment variables."""
        os.environ['FILTER_VAR'] = 'include_me'
        os.environ['OTHER_VAR'] = 'exclude_me'
        
        backup_name = backup_environment('filtered', filter_prefix='FILTER_')
        self.assertIsNotNone(backup_name)
        
        # Read backup file and verify only filtered vars are included
        backup_file = os.path.join(self.test_dir, os.listdir(self.test_dir)[0])
        with open(backup_file, 'r') as f:
            content = f.read()
        
        self.assertIn('FILTER_VAR', content)
        self.assertNotIn('OTHER_VAR', content)

    def test_restore_environment(self):
        """Test restoring environment variables from backup."""
        # Create a backup first
        os.environ['RESTORE_TEST'] = 'original_value'
        backup_name = backup_environment('restore_test')
        
        # Modify the variable
        os.environ['RESTORE_TEST'] = 'modified_value'
        
        # Restore from backup
        backup_file = os.path.join(self.test_dir, os.listdir(self.test_dir)[0])
        success = restore_environment(backup_file)
        self.assertTrue(success)
        
        # Verify restoration
        self.assertEqual(os.environ.get('RESTORE_TEST'), 'original_value')

    def test_list_backups(self):
        """Test listing available backups."""
        # Create multiple backups
        backup_environment('backup1')
        backup_environment('backup2')
        backup_environment('backup3')
        
        backups = list_backups()
        self.assertEqual(len(backups), 3)
        
        # Verify backups are sorted by timestamp (newest first)
        self.assertTrue(all(backups[i] >= backups[i+1] for i in range(len(backups)-1)))

    def test_backup_with_special_characters(self):
        """Test backing up environment variables with special characters."""
        os.environ['SPECIAL_VAR'] = 'value with spaces and "quotes"'
        os.environ['MULTILINE_VAR'] = 'line1\nline2\nline3'
        
        backup_name = backup_environment('special_chars')
        backup_file = os.path.join(self.test_dir, os.listdir(self.test_dir)[0])
        
        # Clear and restore
        del os.environ['SPECIAL_VAR']
        del os.environ['MULTILINE_VAR']
        
        success = restore_environment(backup_file)
        self.assertTrue(success)
        
        # Verify special characters are preserved
        self.assertEqual(os.environ.get('SPECIAL_VAR'), 'value with spaces and "quotes"')
        self.assertEqual(os.environ.get('MULTILINE_VAR'), 'line1\nline2\nline3')

    def test_backup_empty_environment(self):
        """Test backing up with no matching environment variables."""
        backup_name = backup_environment('empty', filter_prefix='NONEXISTENT_')
        self.assertIsNotNone(backup_name)
        
        # Backup file should still be created
        backup_files = os.listdir(self.test_dir)
        self.assertEqual(len(backup_files), 1)

    def test_restore_nonexistent_backup(self):
        """Test restoring from a non-existent backup file."""
        success = restore_environment('/nonexistent/path/backup.env')
        self.assertFalse(success)

    def test_backup_overwrite_protection(self):
        """Test that backups with same name get unique timestamps."""
        backup1 = backup_environment('same_name')
        backup2 = backup_environment('same_name')
        
        self.assertNotEqual(backup1, backup2)
        backup_files = os.listdir(self.test_dir)
        self.assertEqual(len(backup_files), 2)


if __name__ == '__main__':
    unittest.main()
