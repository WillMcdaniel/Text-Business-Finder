import logging

from dotenv import load_dotenv
from urllib.parse import urlencode
from flask import Flask, request
import requests
import os
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
load_dotenv()
logging.basicConfig(level=logging.DEBUG)

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
radius = os.getenv('RADIUS_METERS')
api_key = 'YOUR_API_KEY'  # os.environ.get('API_KEY')
geocode_api_url = os.environ.get('GEOCODE_API_URL')
places_url = os.getenv('PLACES_API_URL')

user_state = {}


def get_json_data(user_address):
    """
    Retrieves JSON data from the geocode API using the provided user address.

    Args:
        user_address (str): The address of the user.

    Returns:
        dict: The JSON data retrieved from the geocode API.

    Raises:
        Exception: If the geocode API returns a non-200 status code.

    """
    # params = {
    #    'address': user_address,
    #      'key': api_key,
    # }
    data_type = 'json'
    endpoint = f'https://maps.googleapis.com/maps/api/geocode/{data_type}'
    params = {'address': user_address, 'key': api_key
              }
    url_params = urlencode(params)
    url = f'{endpoint}?{url_params}'

    # sample = 'https: // maps.googleapis.com / maps / api / geocode / json?address = 1600 + Amphitheatre + Parkway,
    # +Mountain + View, +CA & key = YOUR_API_KEY'

    try:
        response = requests.get(url)
        if response.status_code not in range(200, 299):
            raise Exception("Geocode API returned non-200 status code")
        else:
            data: dict = response.json()  # Converts the json as a python dict object
        return data
    except Exception as e:
        error_message = f"An error occurred getting a response from the geocode api on code block 54: {str(e)}"
        logging.error(error_message)
        return error_message


def get_lat_long(data):
    if data['status'] == 'OK':  # if status is okay, continue with operation
        results = data['results']  # Accessing the results key in the json list
        if results is not None:  # if the results it receives is not none
            location = results[0]['geometry']['location']  # This accesses location dict from the first result in list
            latitude = location['lat']
            longitude = location['lng']

            return f"{latitude}, {longitude}"  # returns latitude, longitude

        else:
            print("results == None. Line 86: No results found")
    else:
        print("Error on line 84:  Geocoding was not successful for the following reason: ", data['status'])


def nearby_search(location, max_results=5):
    search_data_type = 'json'
    search_endpoint = f'https://maps.googleapis.com/maps/api/place/nearbysearch/{search_data_type}'
    params = {'location': location, 'radius': 8047, 'key': api_key,
              }
    url_params = urlencode(params)
    search_url = f'{search_endpoint}?{url_params}'
    formatted_text = "Nearby places:\n"

    try:
        search_data = requests.get(search_url)
        response = search_data.json()
        print("line 62", response)

        if response['status'] == 'OK':
            print(f'line 99: {response["status"]}')

            results = response.get('results', [])[:max_results]
            print(f'line 100: {results}')
            for result in results:
                name = result['name']
                print(name)
                address = result['vicinity']
                print(address)
                opening_hours = result.get('opening_hours', [])
                print(opening_hours)
                if opening_hours:
                    if opening_hours.get('open_now', False):
                        hours = 'Open'
                    else:
                        hours = 'Closed'

                else:
                    hours = 'N/A'

                rating = result.get('rating', 'N/A')
                print(rating)
                formatted_text += f'Name: {name}\nAddress: {address}\nHours: {hours}\nRating: {rating}\n'
                print(formatted_text)
                print("Line 90", formatted_text)
            return formatted_text

        else:
            raise Exception
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    user_phone_number = request.form['From']  # Users phone number
    user_input = request.form['Body']  # Users address

    if user_phone_number not in user_state:
        user_state[user_phone_number] = 'waiting for address'  # Add user to state
        response = 'Welcome, what is your address?'
        resp = MessagingResponse()
        resp.message(response)
        return str(resp)

    elif user_state[user_phone_number] == 'waiting for address':
        try:
            user_address = f'{user_input}'  # user_input
            print(user_address)
            data = get_json_data(user_address)
            print(f'user_state response data: {data}')
            location = get_lat_long(data)
            print(f'user_state response location lat and lon: {location}')
            response: str = nearby_search(str(location))  # This function is expecting a string
            print(response)

            resp = MessagingResponse()
            print(resp)
            resp.message(response)
            print("line 122", resp)

            return str(resp)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            logging.error(error_message)
            return error_message


if __name__ == '__main__':
    app.run(debug=True, port=5000)
