# Dockerfile for Twilio SMS Business Finder
# From official Python image as the base image
FROM python:3.9-alpine

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apk update \
    && apk add --no-cache gcc musl-dev

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /app/

# Run tests, skip todo_* tests
RUN python -m unittest discover -p 'test_*.py' -k 'not todo_'

# Expose the port that the Flask app will run on
EXPOSE 8080

# Run the Flask app
CMD ["python", "main.py"]