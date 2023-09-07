# tests/test_sms_reply.py
import unittest
from main import app


class TestSMSReplyRoute(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_sms_reply_initial_state(self):
        # Simulate the first message from a new user
        response = self.app.post('/sms', data={'From': '1234567890', 'Body': '123 Main St'})

        # Assert the expected response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome, what is your address?', response.data)

    def test_sms_reply_searching_state(self):
        # Simulate a message from a user who has already provided an address
        response = self.app.post('/sms', data={'From': '1234567890', 'Body': 'grocery'})

        # Assert the expected response based on the searching state logic
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Nearby places:', response.data)


if __name__ == '__main__':
    unittest.main()
