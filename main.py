"""
Twilio SMS Business Finder

This script uses the Twilio API to receive SMS messages with business types
and user addresses, then uses the Google Geocoding and Places APIs to find
businesses of the requested type near the provided address.

Before running this script, ensure the following environment variables are set:
- API_KEY: Your Google Maps API key for accessing the Geocoding and Places APIs.
- FLASK_PORT (optional): Port number for running the Flask app (default: 8080).

Author: William McDaniel
Date: 8/12/2023
Version: 1.0.0
"""

import os
import threading
from queue import Queue
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from dotenv import load_dotenv

# Import constants from the separate file
from constants import GEOCODE_API_URL, PLACES_API_URL, RADIUS_METERS, NUM_RESULTS, FLASK_PORT

load_dotenv()

app = Flask(__name__)

# Using a Queue to process incoming requests
pending_requests = Queue()

# Load API key from environment variables
API_KEY = os.environ.get('API_KEY')

def handle_requests():
    """
    Threaded function to process pending requests from the queue.
    Placeholder for actual processing logic.
    """
    try:
        while True:
            number, business_type = pending_requests.get()
            # TODO: Process pending requests here (geocode address, search businesses, respond to user)
            # I think core logic is missing here, but it is hard for me to tell because I do not know exactly how to
            # test the Flask server once it comes up. 
    except Exception as e:
        # Handle exceptions and provide an informative error message
        error_message = f"An error occurred in handle_requests: {str(e)}"
        # You might want to log the error here
        print(error_message)

# Start the threaded request handler
threading.Thread(target=handle_requests).start()

def format_places_data(data):
    """
    Formats Google Places API response data into human-readable messages.
    """
    try:
        stores = data.get('results', [])[:NUM_RESULTS]
        messages = []

        for store in stores:
            name = store.get('name', "No name provided")
            address = store.get('vicinity', "No address provided")
            open_now = store.get('opening_hours', {}).get('open_now', False)
            status = "Open" if open_now else "Closed"
            message = f"{name} at {address} is currently {status}."
            messages.append(message)

        return "\n".join(messages)
    except Exception as e:
        # Handle exceptions and provide an informative error message
        error_message = f"An error occurred while formatting places data: {str(e)}"
        # You might want to log the error here
        print(error_message)

@app.route("/sms", methods=['POST'])
def sms_reply():
    # Get the message the user sent to the Twilio number
    body = request.values.get('Body', None)

    # Get the phone number the message was sent from
    from_number = request.values.get('From', None)

    # Create a Twilio response
    resp = MessagingResponse()

    try:
        if pending_requests.get(from_number, None):
            # The user has already made a request and is now providing their address
            address = body
            business_type = pending_requests.get(from_number)

            # Convert the address to coordinates using the Google Geocoding API
            params = {
                'key': API_KEY,
                'address': address
            }

            geocode_response = requests.get(GEOCODE_API_URL, params=params)
            geocode_data = geocode_response.json()

            if geocode_data['status'] == 'OK':
                location = geocode_data['results'][0]['geometry']['location']
                lat = location['lat']
                lng = location['lng']

                # Search for businesses using the Google Places API
                params = {
                    'key': API_KEY,
                    'location': f'{lat},{lng}',
                    'radius': RADIUS_METERS,
                    'keyword': business_type
                }
                places_response = requests.get(PLACES_API_URL, params=params)
                places_data = places_response.json()

                if places_data['status'] == 'OK' and places_data['results']:
                    response_message = format_places_data(places_data)
                else:
                    response_message = f"No {business_type} found near {address}"
            else:
                response_message = f"Couldn't geocode the provided address: {address}"
        else:
            # This is a new request
            business_name = body.lower()

            # Store the request as pending
            pending_requests.put((from_number, business_name))

            response_message = "Please reply with your address."
    except Exception as e:
        # Handle exceptions and provide an informative error message
        response_message = f"An error occurred: {str(e)}"
        # You might want to log the error here
        print(response_message)

    # Respond with a message
    resp.message(response_message)
    return str(resp)

if __name__ == "__main__":
    # Start the Flask app
    app.run(debug=True, port=FLASK_PORT)