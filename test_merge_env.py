import unittest
import tempfile
import os
from merge_env import merge_env_files


class TestMergeEnv(unittest.TestCase):
    """Test suite for merge_env utility."""

    def setUp(self):
        """Set up temporary files for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_file = os.path.join(self.temp_dir, "base.env")
        self.override_file = os.path.join(self.temp_dir, "override.env")
        self.output_file = os.path.join(self.temp_dir, "output.env")

    def tearDown(self):
        """Clean up temporary files."""
        for file in [self.base_file, self.override_file, self.output_file]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.temp_dir)

    def test_merge_basic(self):
        """Test basic merge of two env files."""
        with open(self.base_file, "w") as f:
            f.write("KEY1=value1\n")
            f.write("KEY2=value2\n")

        with open(self.override_file, "w") as f:
            f.write("KEY2=override2\n")
            f.write("KEY3=value3\n")

        merge_env_files(self.base_file, self.override_file, self.output_file)

        with open(self.output_file, "r") as f:
            content = f.read()

        self.assertIn("KEY1=value1", content)
        self.assertIn("KEY2=override2", content)
        self.assertIn("KEY3=value3", content)
        self.assertNotIn("KEY2=value2", content)

    def test_merge_empty_override(self):
        """Test merge with empty override file."""
        with open(self.base_file, "w") as f:
            f.write("KEY1=value1\n")
            f.write("KEY2=value2\n")

        with open(self.override_file, "w") as f:
            f.write("")

        merge_env_files(self.base_file, self.override_file, self.output_file)

        with open(self.output_file, "r") as f:
            content = f.read()

        self.assertIn("KEY1=value1", content)
        self.assertIn("KEY2=value2", content)

    def test_merge_empty_base(self):
        """Test merge with empty base file."""
        with open(self.base_file, "w") as f:
            f.write("")

        with open(self.override_file, "w") as f:
            f.write("KEY1=value1\n")

        merge_env_files(self.base_file, self.override_file, self.output_file)

        with open(self.output_file, "r") as f:
            content = f.read()

        self.assertIn("KEY1=value1", content)

    def test_merge_with_comments(self):
        """Test merge preserves comments from base file."""
        with open(self.base_file, "w") as f:
            f.write("# Comment line\n")
            f.write("KEY1=value1\n")

        with open(self.override_file, "w") as f:
            f.write("KEY2=value2\n")

        merge_env_files(self.base_file, self.override_file, self.output_file)

        with open(self.output_file, "r") as f:
            content = f.read()

        self.assertIn("# Comment line", content)
        self.assertIn("KEY1=value1", content)
        self.assertIn("KEY2=value2", content)

    def test_merge_with_equals_in_value(self):
        """Test merge handles equals signs in values."""
        with open(self.base_file, "w") as f:
            f.write("KEY1=value=with=equals\n")

        with open(self.override_file, "w") as f:
            f.write("KEY2=another=value=test\n")

        merge_env_files(self.base_file, self.override_file, self.output_file)

        with open(self.output_file, "r") as f:
            content = f.read()

        self.assertIn("KEY1=value=with=equals", content)
        self.assertIn("KEY2=another=value=test", content)

    def test_merge_multiple_overrides(self):
        """Test merge with multiple keys being overridden."""
        with open(self.base_file, "w") as f:
            f.write("KEY1=base1\n")
            f.write("KEY2=base2\n")
            f.write("KEY3=base3\n")

        with open(self.override_file, "w") as f:
            f.write("KEY1=override1\n")
            f.write("KEY3=override3\n")

        merge_env_files(self.base_file, self.override_file, self.output_file)

        with open(self.output_file, "r") as f:
            content = f.read()

        self.assertIn("KEY1=override1", content)
        self.assertIn("KEY2=base2", content)
        self.assertIn("KEY3=override3", content)

    def test_merge_preserves_order(self):
        """Test merge preserves base file order."""
        with open(self.base_file, "w") as f:
            f.write("ZEBRA=z\n")
            f.write("ALPHA=a\n")
            f.write("MIDDLE=m\n")

        with open(self.override_file, "w") as f:
            f.write("ALPHA=override\n")

        merge_env_files(self.base_file, self.override_file, self.output_file)

        with open(self.output_file, "r") as f:
            lines = f.readlines()

        keys = [line.split("=")[0] for line in lines if "=" in line]
        self.assertEqual(keys, ["ZEBRA", "ALPHA", "MIDDLE"])

    def test_merge_nonexistent_base(self):
        """Test merge handles nonexistent base file."""
        with open(self.override_file, "w") as f:
            f.write("KEY1=value1\n")

        with self.assertRaises(FileNotFoundError):
            merge_env_files(
                os.path.join(self.temp_dir, "nonexistent.env"),
                self.override_file,
                self.output_file
            )

    def test_merge_nonexistent_override(self):
        """Test merge handles nonexistent override file."""
        with open(self.base_file, "w") as f:
            f.write("KEY1=value1\n")

        with self.assertRaises(FileNotFoundError):
            merge_env_files(
                self.base_file,
                os.path.join(self.temp_dir, "nonexistent.env"),
                self.output_file
            )


if __name__ == "__main__":
    unittest.main()
