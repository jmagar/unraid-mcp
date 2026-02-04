import unittest

# unraid_mcp.tools.api is now importable thanks to conftest.py or pip install -e .
from unraid_mcp.tools.api import _strip_comments
from unraid_mcp.tools.system import format_kb


class TestUtils(unittest.TestCase):
    def test_strip_comments(self):
        # Basic comment stripping
        query = """
        query {
            field # This is a comment
            anotherField
        }
        """
        stripped = _strip_comments(query)
        self.assertNotIn("# This is a comment", stripped)
        self.assertIn("field", stripped)

        # String preservation
        query_str = 'field(arg: "some # string")'
        stripped_str = _strip_comments(query_str)
        self.assertIn('""', stripped_str)  # It replaces strings with ""

        # Block string
        query_block = 'field(arg: """block # string""")'
        stripped_block = _strip_comments(query_block)
        self.assertIn('""""""', stripped_block)  # It replaces block strings

    def test_format_kb(self):
        """
        Verify the logic of the real format_kb function directly.
        """
        # Test overflow/special cases
        self.assertEqual(format_kb(float("inf")), "inf")
        self.assertEqual(format_kb("not_a_number"), "not_a_number")
        self.assertEqual(format_kb(None), "N/A")

        # Test formatting
        self.assertEqual(format_kb(1024), "1.00 MB")
        self.assertEqual(format_kb(1024 * 1024), "1.00 GB")
        self.assertEqual(format_kb(512), "512 KB")


if __name__ == "__main__":
    unittest.main()
