# tests/test_format_places_data.py
import unittest
from main import format_places_data

class TestFormatPlacesData(unittest.TestCase):
    def test_format_places_data(self):
        data = {
            "results": [
                {"name": "Store 1", "vicinity": "Address 1", "opening_hours": {"open_now": True}},
                {"name": "Store 2", "vicinity": "Address 2", "opening_hours": {"open_now": False}}
            ]
        }
        expected_result = "Store 1 at Address 1 is currently Open.\nStore 2 at Address 2 is currently Closed."
        result = format_places_data(data)
        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()