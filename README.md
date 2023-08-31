# Twilio SMS Business Finder

The Twilio SMS Business Finder is a Python application that allows users to send SMS messages with business types and addresses. The application utilizes the Twilio API to receive SMS messages, the Google Geocoding API to convert addresses to coordinates, and the Google Places API to find businesses of the requested type near the provided address.

## Prerequisites

Before running the application, make sure you have the following:

- Python 3.9 or higher installed
- Twilio account and API credentials
- Google Maps API key
- ngrok for local testing
- Docker (optional, for containerization)

## Directory Layout

The unit tests are structured as follows:
```
twilio-sms-business-finder/
├── Dockerfile
├── LICENSE
├── README.md
├── main.py
├── requirements.txt
└── tests
    ├── test_format_places_data.py
    └── test_sms_reply.py
```

## Setup

1. Clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/twilio-sms-business-finder.git
cd twilio-sms-business-finder
```

3. Rename the .env.example file to .env and fill in your Twilio API credentials and Google Maps API key:
```bash
API_KEY=your_google_maps_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

## Unit Tests

The Twilio SMS Business Finder project includes unit tests to ensure the correctness of its core functionality. The tests are organized in the `tests` directory and use the built-in `unittest` framework.

### Directory Layout

The unit tests are structured as follows:
```
twilio-sms-business-finder/
├── ...
└── tests
    ├── test_format_places_data.py
    └── todo_test_sms_reply.py (Tests w/the prefix 'todo_' will be ingored by the specified pattern, once they are complete, you must remove the prefix to enable them.)
    └── ...
```

### Prerequisites

Before running the unit tests, ensure you have the following prerequisites:

- Python 3.9 or higher installed.
- Required Python packages from `requirements.txt` installed.

### Running Tests

To run the unit tests, use the following commands:

```bash
pip install -r requirements.txt
python -m unittest discover -p 'test_*.py' -k 'not todo_'
```

This command discovers and runs all the test cases in the tests directory. You'll see output indicating whether the tests have passed or failed.

*NOTE: The Dockerfile runs all tests automatically as part of the image build.*

### Adding Tests
To add new tests or expand existing ones, follow these steps:

1. Create test files in the tests directory. For example, test_format_places_data.py and test_sms_reply.py.
2. Implement test cases using the unittest assertions to check expected behavior.
3. Run the tests using the python -m unittest discover tests command.

## Running the Application

### Using Python
Run the Flask application using the following commands:
```bash
pip install -r requirements.txt
python main.py
```

### Using Docker
If you prefer to run the application in a Docker container, follow these steps:

1. Build the Docker image:
```bash
docker build -t twilio-sms-business-finder .
```

2. Run a Docker container based on the image:
```bash
docker run -p 8080:8080 -d twilio-sms-business-finder
```

## Usage
1. Send an SMS to your Twilio phone number with the desired business type.
2. When prompted, reply with the address where you want to find businesses.
3. Receive SMS responses with information about businesses of the requested type near the provided address.

## Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please create an issue or submit a pull request.
