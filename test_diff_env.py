import unittest
import tempfile
import os
from diff_env import diff_environments, format_diff_output


class TestDiffEnv(unittest.TestCase):
    """Comprehensive test suite for diff_env utility."""

    def setUp(self):
        """Set up temporary files for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.env1_path = os.path.join(self.temp_dir, "env1.txt")
        self.env2_path = os.path.join(self.temp_dir, "env2.txt")

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.env1_path):
            os.remove(self.env1_path)
        if os.path.exists(self.env2_path):
            os.remove(self.env2_path)
        os.rmdir(self.temp_dir)

    def test_identical_environments(self):
        """Test diff of identical environment files."""
        content = "VAR1=value1\nVAR2=value2\nVAR3=value3\n"
        with open(self.env1_path, "w") as f:
            f.write(content)
        with open(self.env2_path, "w") as f:
            f.write(content)

        diff = diff_environments(self.env1_path, self.env2_path)
        self.assertEqual(diff["added"], {})
        self.assertEqual(diff["removed"], {})
        self.assertEqual(diff["modified"], {})

    def test_added_variables(self):
        """Test detection of added variables."""
        with open(self.env1_path, "w") as f:
            f.write("VAR1=value1\n")
        with open(self.env2_path, "w") as f:
            f.write("VAR1=value1\nVAR2=value2\n")

        diff = diff_environments(self.env1_path, self.env2_path)
        self.assertEqual(diff["added"], {"VAR2": "value2"})
        self.assertEqual(diff["removed"], {})
        self.assertEqual(diff["modified"], {})

    def test_removed_variables(self):
        """Test detection of removed variables."""
        with open(self.env1_path, "w") as f:
            f.write("VAR1=value1\nVAR2=value2\n")
        with open(self.env2_path, "w") as f:
            f.write("VAR1=value1\n")

        diff = diff_environments(self.env1_path, self.env2_path)
        self.assertEqual(diff["added"], {})
        self.assertEqual(diff["removed"], {"VAR2": "value2"})
        self.assertEqual(diff["modified"], {})

    def test_modified_variables(self):
        """Test detection of modified variables."""
        with open(self.env1_path, "w") as f:
            f.write("VAR1=value1\nVAR2=old_value\n")
        with open(self.env2_path, "w") as f:
            f.write("VAR1=value1\nVAR2=new_value\n")

        diff = diff_environments(self.env1_path, self.env2_path)
        self.assertEqual(diff["added"], {})
        self.assertEqual(diff["removed"], {})
        self.assertEqual(diff["modified"], {"VAR2": {"old": "old_value", "new": "new_value"}})

    def test_complex_diff(self):
        """Test complex diff with added, removed, and modified variables."""
        with open(self.env1_path, "w") as f:
            f.write("VAR1=value1\nVAR2=old_value\nVAR3=value3\n")
        with open(self.env2_path, "w") as f:
            f.write("VAR1=value1\nVAR2=new_value\nVAR4=value4\n")

        diff = diff_environments(self.env1_path, self.env2_path)
        self.assertEqual(diff["added"], {"VAR4": "value4"})
        self.assertEqual(diff["removed"], {"VAR3": "value3"})
        self.assertEqual(diff["modified"], {"VAR2": {"old": "old_value", "new": "new_value"}})

    def test_empty_files(self):
        """Test diff of empty environment files."""
        with open(self.env1_path, "w") as f:
            f.write("")
        with open(self.env2_path, "w") as f:
            f.write("")

        diff = diff_environments(self.env1_path, self.env2_path)
        self.assertEqual(diff["added"], {})
        self.assertEqual(diff["removed"], {})
        self.assertEqual(diff["modified"], {})

    def test_empty_to_populated(self):
        """Test diff from empty to populated file."""
        with open(self.env1_path, "w") as f:
            f.write("")
        with open(self.env2_path, "w") as f:
            f.write("VAR1=value1\nVAR2=value2\n")

        diff = diff_environments(self.env1_path, self.env2_path)
        self.assertEqual(diff["added"], {"VAR1": "value1", "VAR2": "value2"})
        self.assertEqual(diff["removed"], {})
        self.assertEqual(diff["modified"], {})

    def test_variables_with_special_characters(self):
        """Test diff with variables containing special characters."""
        with open(self.env1_path, "w") as f:
            f.write("DB_URL=postgres://user:pass@localhost/db\n")
        with open(self.env2_path, "w") as f:
            f.write("DB_URL=postgres://user:newpass@localhost/db\n")

        diff = diff_environments(self.env1_path, self.env2_path)
        self.assertEqual(diff["added"], {})
        self.assertEqual(diff["removed"], {})
        self.assertEqual(diff["modified"], {
            "DB_URL": {
                "old": "postgres://user:pass@localhost/db",
                "new": "postgres://user:newpass@localhost/db"
            }
        })

    def test_format_diff_output(self):
        """Test formatting of diff output."""
        diff = {
            "added": {"VAR1": "value1"},
            "removed": {"VAR2": "value2"},
            "modified": {"VAR3": {"old": "old", "new": "new"}}
        }
        output = format_diff_output(diff)
        self.assertIn("Added:", output)
        self.assertIn("VAR1", output)
        self.assertIn("Removed:", output)
        self.assertIn("VAR2", output)
        self.assertIn("Modified:", output)
        self.assertIn("VAR3", output)

    def test_format_diff_output_no_changes(self):
        """Test formatting when there are no changes."""
        diff = {
            "added": {},
            "removed": {},
            "modified": {}
        }
        output = format_diff_output(diff)
        self.assertIn("No differences found", output)

    def test_variables_with_quotes(self):
        """Test diff with variables containing quotes."""
        with open(self.env1_path, "w") as f:
            f.write('MESSAGE="Hello World"\n')
        with open(self.env2_path, "w") as f:
            f.write('MESSAGE="Goodbye World"\n')

        diff = diff_environments(self.env1_path, self.env2_path)
        self.assertEqual(diff["modified"], {
            "MESSAGE": {"old": '"Hello World"', "new": '"Goodbye World"'}
        })

    def test_multiline_values(self):
        """Test handling of variables with multiline values."""
        with open(self.env1_path, "w") as f:
            f.write("VAR1=line1\nline2\nVAR2=value2\n")
        with open(self.env2_path, "w") as f:
            f.write("VAR1=line1\nVAR2=value2\n")

        diff = diff_environments(self.env1_path, self.env2_path)
        # Should handle gracefully based on implementation
        self.assertIsInstance(diff, dict)
        self.assertIn("added", diff)
        self.assertIn("removed", diff)
        self.assertIn("modified", diff)


if __name__ == "__main__":
    unittest.main()
