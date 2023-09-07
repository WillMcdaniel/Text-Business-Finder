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

import logging
from dotenv import load_dotenv
from urllib.parse import urlencode
from flask import Flask, request
import requests
import os
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.DEBUG)

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
radius = os.getenv('RADIUS_METERS')
api_key = 'Your_API_KEY'  # os.environ.get('API_KEY')
geocode_api_url = os.environ.get('GEOCODE_API_URL')
places_url = os.getenv('PLACES_API_URL')

user_state = {}


class UserState:
    waiting_for_address = 'waiting_for_address'
    searching = 'searching'
    SEARCHING_CONTINUE = 'searching_continue'
    SEARCHING_FOR_NEW_BUSINESS = 'searching_for_new_business'
    SEARCHING_NEW_ADDRESS = 'searching_new_address'
    SEARCHING_RESULTS = 'searching_results'


class ResponseError(Exception):
    def __init__(self, message):
        self.message = message


def make_api_request(url):
    try:
        response = requests.get(url)
        if response.status_code not in range(200, 299):
            raise ResponseError("API returned non-200 status code")
        else:
            data = response.json()
        return data
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)
        return error_message


def get_json_data(user_address):
    data_type = 'json'
    endpoint = f'https://maps.googleapis.com/maps/api/geocode/{data_type}'
    params = {'address': user_address, 'key': api_key}
    url_params = urlencode(params)
    url = f'{endpoint}?{url_params}'

    data = make_api_request(url)
    return data


def get_lat_long(data):
    if data['status'] == 'OK':
        results = data['results']
        if results is not None:
            location = results[0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
            return f"{latitude}, {longitude}"
        else:
            print("results == None. Line 86: No results found")
    else:
        print("Error on line 84: Geocoding was not successful for the following reason: ", data['status'])


def nearby_search(location, keyword, max_results=5):
    search_data_type = 'json'
    search_endpoint = f'https://maps.googleapis.com/maps/api/place/nearbysearch/{search_data_type}'
    params = {'location': location, 'radius': 8047, 'keyword': keyword, 'key': api_key}
    url_params = urlencode(params)
    search_url = f'{search_endpoint}?{url_params}'
    formatted_text = "Nearby places:\n"

    search_data = make_api_request(search_url)

    if search_data['status'] == 'OK':
        results = search_data.get('results', [])[:max_results]
        for result in results:
            name = result['name']
            address = result['vicinity']
            opening_hours = result.get('opening_hours', [])
            if opening_hours:
                hours = 'Open' if opening_hours.get('open_now', False) else 'Closed'
            else:
                hours = 'N/A'
            rating = result.get('rating', 'N/A')
            formatted_text += f'Name: {name}\nAddress: {address}\nHours: {hours}\nRating: {rating}\n'
        return formatted_text
    else:
        raise ResponseError("Geocode API returned non-200 status code")


def set_user_state(user_phone_number, state, keyword=None):
    user_state[user_phone_number] = {'state': state}
    if keyword:
        user_state[user_phone_number]['keyword'] = keyword


def get_user_state(user_phone_number):
    return user_state.get(user_phone_number, {})


def generate_welcome_message():
    return 'Welcome, what is your address?'


def generate_continue_search_message():
    return 'Do you want to search for another business? Reply "yes" or "no".'


def generate_goodbye_message():
    return 'Okay, goodbye.'


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    user_phone_number = request.form['From']
    user_input = request.form['Body'].strip().lower()

    user_state_info = get_user_state(user_phone_number)
    user_state_info['address'] = user_input

    if 'state' not in user_state_info:
        set_user_state(user_phone_number, UserState.waiting_for_address, user_input)
        response = generate_welcome_message()
    else:
        state = user_state_info['state']

        if state == UserState.waiting_for_address:
            user_state_info['state'] = UserState.searching
            user_address = user_state_info['address']
            keyword = user_state_info.get('keyword')

            try:
                data = get_json_data(user_address)
                location = get_lat_long(data)
                response = nearby_search(str(location), keyword)
                response += "\n\n" + generate_continue_search_message()
                set_user_state(user_phone_number, UserState.SEARCHING_CONTINUE)
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                logging.error(error_message)
                return error_message
        else:
            if state == UserState.SEARCHING_CONTINUE:
                if user_input == 'yes':
                    user_state_info['state'] = UserState.SEARCHING_FOR_NEW_BUSINESS
                    response = 'Great, what new business would you like to search for?'
                elif user_input == 'no':
                    response = generate_goodbye_message()
                    user_state.pop(user_phone_number)
                else:
                    response = 'Please reply with "yes" or "no".'
            elif state == UserState.SEARCHING_FOR_NEW_BUSINESS:
                user_state_info['new_business'] = user_input
                user_state_info['state'] = UserState.SEARCHING_NEW_ADDRESS
                response = 'What is your new address?'
            elif state == UserState.SEARCHING_NEW_ADDRESS:
                user_state_info['new_address'] = user_input
                user_state_info['state'] = UserState.SEARCHING_RESULTS
                new_business = user_state_info['new_business']
                new_address = user_state_info['new_address']

                try:
                    data = get_json_data(new_address)
                    location = get_lat_long(data)
                    response = nearby_search(str(location), new_business)
                except Exception as e:
                    error_message = f"An error occurred: {str(e)}"
                    logging.error(error_message)
                    response = error_message

                response += "\n\n" + generate_continue_search_message()
                set_user_state(user_phone_number, UserState.SEARCHING_CONTINUE)

    resp = MessagingResponse()
    resp.message(response)
    return str(resp)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
