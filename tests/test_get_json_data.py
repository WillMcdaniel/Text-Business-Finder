# tests/test_sms_reply.py
import unittest
from unittest.mock import patch
from main import get_json_data


class TestGetJsonData(unittest.TestCase):
    @patch('main.requests.get')  # Mock the requests.get method
    def test_get_json_data_success(self, mock_get):
        # Set up the mock response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'OK',
                                           'results': [{'geometry': {'location': {'lat': 123, 'lng': 456}}}]}

        # Call the function and assert the expected result
        result = get_json_data('some_address')
        self.assertEqual(result, {'status': 'OK', 'results': [{'geometry': {'location': {'lat': 123, 'lng': 456}}}]})


if __name__ == '__main__':
    unittest.main()
