"""Exercise the installed wheel used by the trusted source validation."""
import unittest
from splrad_e08_product import greeting


class ProductTest(unittest.TestCase):
    def test_greeting(self):
        self.assertEqual(greeting(), "SPLRAD E08 Python product")


if __name__ == "__main__":
    unittest.main()
