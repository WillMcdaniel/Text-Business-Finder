# constants.py
import os

GEOCODE_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
PLACES_API_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
RADIUS_METERS = 8047
NUM_RESULTS = 5
FLASK_PORT = int(os.environ.get('FLASK_PORT', 8080))  # Get port from env variable, default to 8080