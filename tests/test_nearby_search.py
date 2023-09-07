import unittest
from unittest.mock import patch
from main import nearby_search


class TestNearbySearch(unittest.TestCase):
    @patch('main.requests.get')  # Mock the requests.get method
    def test_nearby_search_success(self, mock_get):
        # Set up the mock response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'OK',
                                           'results': [{'name': 'Store', 'vicinity': '123 Main St', 'rating': 4.5}]}

        # Call the function and assert the expected result
        result = nearby_search('12.34,56.78', 'grocery')
        expected_result = "Nearby places:\nName: Store\nAddress: 123 Main St\nHours: N/A\nRating: 4.5\n"
        self.assertEqual(result, expected_result)

        # Add more test cases for error handling
        # ...


if __name__ == '__main__':
    unittest.main()
