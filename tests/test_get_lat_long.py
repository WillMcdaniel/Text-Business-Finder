# tests/test_format_places_data.py
import unittest
from main import get_lat_long


class TestGetLatLong(unittest.TestCase):
    def test_get_lat_long_success(self):
        # Mocked data with a successful response
        data = {'status': 'OK', 'results': [{'geometry': {'location': {'lat': 123, 'lng': 456}}}]}
        result = get_lat_long(data)
        self.assertEqual(result, '123, 456')

    def test_get_lat_long_error(self):
        # Test when 'status' is not 'OK'
        data = {'status': 'ZERO_RESULTS'}  # Simulate an error response
        result = get_lat_long(data)
        self.assertIsNone(result)  # You might want to handle this differently in your code


if __name__ == '__main__':
    unittest.main()
