import logging
from dotenv import load_dotenv
from flask import Flask, request
import requests
import os
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
radius = os.environ.get('RADIUS_METERS')
api_key = os.environ.get('API_KEY')

user_state = {}


# GEOCODING API ->GOOGLE PLACES API->TWILIO RESPONSE TO USER
def get_json_data(user_address):
    try:
        params = {
            'address': user_address,
            'key': api_key,
        }
        geocode_api_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
        response = requests.get(geocode_api_url, params=params)
        print("line 29", response)
        data = response.json()  # Puts the json as a python list object
        print("line 31", data)
        return data
    except Exception as e:
        error_message = f"An error occured getting a response from the geocode api: {str(e)}"
        logging.error(error_message)
        return error_message


def get_lat_long(data):
    if data['status'] == 'OK':  # if status is okay, continue with operation
        results = data['results']  # Accessing the results key in the json list
        if results:  # if the results it recieves is not none
            location = results[0]['geometry'][
                'location']  # This accesses location dict from the first result in the list
            latitude = location['lat']
            longitude = location['lng']

            return latitude, longitude

        else:
            print("No results found")
    else:
        print("Geocoding was not successful for the following reason: ", data['status'])


def nearby_search(location, max_results=5):
    params = {
        'location': location,
        'radius': radius,
        'key': api_key
    }
    places_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
    try:
        search_data = requests.get(places_url, params=params)
        if search_data.status_code != 200:
            raise Exception

        response = search_data.json()
        print("line 62", response)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)

    if response['status'] != 'OK':
        print("line 69", response)
    else:
        search_data = response.json()
        results = search_data.get('results', [])[:max_results]
        print("line 73", results)
        formatted_text = "Nearby places:\n"

    for result in results:
        name = result['name']
        address = result['vicinity']
        opening_hours = result.get('opening_hours', [])
        if opening_hours:
            if opening_hours.get('open_now', False):
                hours = 'Open'
            else:
                hours = 'Closed'
        else:
            hours = 'N/A'
        rating = result.get('rating', 'N/A')
        formatted_text += f'Name: {name}\nAddress: {address}\nRating: {rating}\n'
        print("Line 90", formatted_text)
    return formatted_text


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    # Get the message the user sent our Twilio number
    user_phone_number = request.form['From']  # Users phone number
    user_input = request.form['Body']  # Users address

    if user_phone_number not in user_state:
        user_state[user_phone_number] = 'waiting for address'  # Add user to state
        response = 'Welcome, what is your address?'

    elif user_state[user_phone_number] == 'waiting for address':
        user_address = user_input
        data = get_json_data(user_address)
        location = get_lat_long(data)
        response = nearby_search(location)
        print(response)

        resp = MessagingResponse()
        resp.message(response)
        print("line 122", resp)

        return str(resp)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
