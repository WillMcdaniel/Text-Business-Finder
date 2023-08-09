Text Business Finder
Overview
This is a Python Flask web application that allows users to text a business name to a Twilio number and receive a response with the 5 closest matching businesses and their current open/closed status.
It uses the Twilio API for SMS, Google Maps Geocoding API, and Google Places API.
How it works:
User texts a business name (e.g. "coffee") to the Twilio number
Twilio webhook sends the request to the /sms endpoint
The app stores the phone number and business name in a pending_requests Queue
The app responds asking the user to send their location
User replies with their address
The app geocodes the address to latitude and longitude using the Google Maps Geocoding API
The app searches for nearby businesses of that type using the latitude, longitude, and business name with the Google Places API
The app formats the Places API results into a message with the 5 closest businesses, their addresses, and open/closed status
The message is sent back to the user via Twilio API
Code structure:
main.py
Sets up the Flask app and routes
Configures the Twilio webhook route
Handles the business lookup workflow
Uses background threads and queues for asynchronous processing
requirements.txt
Specifies the app's Python dependencies
.env
Stores API keys and other environment variables
Running locally:
Clone the repo
Create a virtualenv and install requirements
Get API keys for Twilio, Google Maps, Google Places
Add the keys to a .env file
Run python main.py
Text a business name to your Twilio number
Deployment:
This app can be deployed to any host that supports Python/Flask apps.
Some options:
Heroku
AWS Elastic Beanstalk
Azure App Service
Google App Engine
The Twilio webhook URL will need to be configured to point to the deployed app.
