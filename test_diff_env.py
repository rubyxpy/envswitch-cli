#!/usr/bin/env python3
"""Comprehensive test suite for diff_env utility."""

import unittest
import os
import tempfile
import json
from diff_env import diff_environments, load_env_file, main
from io import StringIO
import sys


class TestDiffEnv(unittest.TestCase):
    """Test cases for environment variable diff utility."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.env1_path = os.path.join(self.test_dir, "env1.json")
        self.env2_path = os.path.join(self.test_dir, "env2.json")

    def tearDown(self):
        """Clean up test files."""
        for file in [self.env1_path, self.env2_path]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.test_dir)

    def test_diff_identical_environments(self):
        """Test diff with identical environments."""
        env = {"VAR1": "value1", "VAR2": "value2"}
        diff = diff_environments(env, env)
        self.assertEqual(diff["added"], {})
        self.assertEqual(diff["removed"], {})
        self.assertEqual(diff["changed"], {})
        self.assertEqual(diff["unchanged"], env)

    def test_diff_added_variables(self):
        """Test diff with added variables."""
        env1 = {"VAR1": "value1"}
        env2 = {"VAR1": "value1", "VAR2": "value2", "VAR3": "value3"}
        diff = diff_environments(env1, env2)
        self.assertEqual(diff["added"], {"VAR2": "value2", "VAR3": "value3"})
        self.assertEqual(diff["removed"], {})
        self.assertEqual(diff["changed"], {})
        self.assertEqual(diff["unchanged"], {"VAR1": "value1"})

    def test_diff_removed_variables(self):
        """Test diff with removed variables."""
        env1 = {"VAR1": "value1", "VAR2": "value2", "VAR3": "value3"}
        env2 = {"VAR1": "value1"}
        diff = diff_environments(env1, env2)
        self.assertEqual(diff["added"], {})
        self.assertEqual(diff["removed"], {"VAR2": "value2", "VAR3": "value3"})
        self.assertEqual(diff["changed"], {})
        self.assertEqual(diff["unchanged"], {"VAR1": "value1"})

    def test_diff_changed_variables(self):
        """Test diff with changed variables."""
        env1 = {"VAR1": "old_value", "VAR2": "value2"}
        env2 = {"VAR1": "new_value", "VAR2": "value2"}
        diff = diff_environments(env1, env2)
        self.assertEqual(diff["added"], {})
        self.assertEqual(diff["removed"], {})
        self.assertEqual(diff["changed"], {"VAR1": {"old": "old_value", "new": "new_value"}})
        self.assertEqual(diff["unchanged"], {"VAR2": "value2"})

    def test_diff_complex_scenario(self):
        """Test diff with mixed changes."""
        env1 = {
            "VAR1": "value1",
            "VAR2": "old_value",
            "VAR3": "value3",
            "VAR4": "value4"
        }
        env2 = {
            "VAR1": "value1",
            "VAR2": "new_value",
            "VAR5": "value5"
        }
        diff = diff_environments(env1, env2)
        self.assertEqual(diff["added"], {"VAR5": "value5"})
        self.assertEqual(diff["removed"], {"VAR3": "value3", "VAR4": "value4"})
        self.assertEqual(diff["changed"], {"VAR2": {"old": "old_value", "new": "new_value"}})
        self.assertEqual(diff["unchanged"], {"VAR1": "value1"})

    def test_diff_empty_environments(self):
        """Test diff with empty environments."""
        diff = diff_environments({}, {})
        self.assertEqual(diff["added"], {})
        self.assertEqual(diff["removed"], {})
        self.assertEqual(diff["changed"], {})
        self.assertEqual(diff["unchanged"], {})

    def test_diff_empty_to_populated(self):
        """Test diff from empty to populated environment."""
        env1 = {}
        env2 = {"VAR1": "value1", "VAR2": "value2"}
        diff = diff_environments(env1, env2)
        self.assertEqual(diff["added"], {"VAR1": "value1", "VAR2": "value2"})
        self.assertEqual(diff["removed"], {})
        self.assertEqual(diff["changed"], {})
        self.assertEqual(diff["unchanged"], {})

    def test_diff_populated_to_empty(self):
        """Test diff from populated to empty environment."""
        env1 = {"VAR1": "value1", "VAR2": "value2"}
        env2 = {}
        diff = diff_environments(env1, env2)
        self.assertEqual(diff["added"], {})
        self.assertEqual(diff["removed"], {"VAR1": "value1", "VAR2": "value2"})
        self.assertEqual(diff["changed"], {})
        self.assertEqual(diff["unchanged"], {})

    def test_load_env_file_valid(self):
        """Test loading valid environment file."""
        env_data = {"VAR1": "value1", "VAR2": "value2"}
        with open(self.env1_path, 'w') as f:
            json.dump(env_data, f)
        
        loaded = load_env_file(self.env1_path)
        self.assertEqual(loaded, env_data)

    def test_load_env_file_nonexistent(self):
        """Test loading non-existent file."""
        with self.assertRaises(FileNotFoundError):
            load_env_file("/nonexistent/file.json")

    def test_load_env_file_invalid_json(self):
        """Test loading invalid JSON file."""
        with open(self.env1_path, 'w') as f:
            f.write("invalid json content")
        
        with self.assertRaises(json.JSONDecodeError):
            load_env_file(self.env1_path)

    def test_main_function_with_files(self):
        """Test main function with file arguments."""
        env1 = {"VAR1": "value1", "VAR2": "old"}
        env2 = {"VAR1": "value1", "VAR2": "new", "VAR3": "value3"}
        
        with open(self.env1_path, 'w') as f:
            json.dump(env1, f)
        with open(self.env2_path, 'w') as f:
            json.dump(env2, f)
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            sys.argv = ['diff_env.py', self.env1_path, self.env2_path]
            main()
            output = sys.stdout.getvalue()
            self.assertIn("Environment Diff", output)
            self.assertIn("Added", output)
            self.assertIn("Changed", output)
        finally:
            sys.stdout = old_stdout

    def test_diff_with_special_characters(self):
        """Test diff with special characters in values."""
        env1 = {"PATH": "/usr/bin:/bin", "MSG": "Hello World!"}
        env2 = {"PATH": "/usr/local/bin:/usr/bin:/bin", "MSG": "Hello World!"}
        diff = diff_environments(env1, env2)
        self.assertEqual(len(diff["changed"]), 1)
        self.assertIn("PATH", diff["changed"])
        self.assertEqual(diff["unchanged"], {"MSG": "Hello World!"})

    def test_diff_case_sensitive(self):
        """Test that diff is case-sensitive."""
        env1 = {"VAR": "value"}
        env2 = {"var": "value"}
        diff = diff_environments(env1, env2)
        self.assertEqual(diff["added"], {"var": "value"})
        self.assertEqual(diff["removed"], {"VAR": "value"})
        self.assertEqual(diff["unchanged"], {})


if __name__ == "__main__":
    unittest.main()
