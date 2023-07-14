from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# This can be a database or a more complex data structure
pending_requests = {}

def format_places_data(data):
    stores = data.get('results', [])[:5]  # Limit to the top 5 results
    messages = []

    for store in stores:
        name = store.get('name', "No name provided")
        address = store.get('vicinity', "No address provided")
        open_now = store.get('opening_hours', {}).get('open_now', False)
        status = "Open" if open_now else "Closed"
        message = f"{name} at {address} is currently {status}."
        messages.append(message)

    return "\n".join(messages)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Get the phone number the message was sent from
    from_number = request.values.get('From', None)

    API_KEY = 'AIzaSyBiCvlp6HgO8SpEBYUSEYIJRcNqFTw2AyQ'

    # Start our Twilio response
    resp = MessagingResponse()

    if from_number in pending_requests:
        # The user has already made a request and is now providing their address
        address = body
        business_type = pending_requests[from_number]  # Add this line

        # Convert the address to coordinates (using the Google Geocoding API)
        params = {
            'key': API_KEY,
            'address': address
        }

        geo_code_api = 'https://maps.googleapis.com/maps/api/geocode/json?'
        geocode_response = requests.get(geo_code_api, params=params)
        geocode_data = geocode_response.json()
        print(geocode_data)

        if geocode_data['status'] == 'OK':
            location = geocode_data['results'][0]['geometry']['location']
            lat = location['lat']
            lng = location['lng']

            # Then, find businesses of the requested name near these coordinates (using the Google Places API)
            params = {
                'key': API_KEY,
                'location': f'{lat},{lng}',
                'radius': 8047,
                'keyword': business_type
            }

            google_places_api = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
            places_response = requests.get(google_places_api, params=params)
            places_data = places_response.json()
            print(places_data)

            if places_data['status'] == 'OK' and places_data['results']:
                response_message = format_places_data(places_data)
            else:
                response_message = f"No {business_type} found near {address}"

        else:
            response_message = f"Couldn't geocode the provided address: {address}"

        # Remove the pending request
        #del pending_requests[from_number]
    else:
        # This is a new request
        business_name = body.lower()

        # Store the request as pending
        pending_requests[from_number] = business_name

        response_message = "Please reply with your address."

    # Respond with a message
    resp.message(response_message)
    print(str(resp))

    return str(resp)


if __name__=="__main__":
    app.run(debug=True, port=8080)