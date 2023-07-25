"""
Sample tests
"""

from django.test import SimpleTestCase
from app import calc

class CalcTests(SimpleTestCase):
    """Tests the calc module"""

    def test_add_numbers(self):
        """Test adding numbers together"""
        result = calc.add(5,9)
        self.assertEqual(result, 14)


    def test_subtract_numbers(self):
        """Test substarcting numbers"""

        result = calc.subtract(9,6)
        self.assertEqual(result, 3)
        

        

