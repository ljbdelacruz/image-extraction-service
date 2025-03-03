#!/bin/bash

PYTHON_PATH=$(which python3)

# install dependencies
PYTHON_PATH -m pip install six opencv-python cvlib gtts ultralytics flask prisma flasgger python-dotenv boto3 flask-socketio eventlet


# use this if you want to test using websocket client connection for debugging the websocket app
PYTHON_PATH -m pip install python-socketio

PYTHON_PATH app_websocket.py

PYTHON_PATH test_web_client.py

# running flask app
export FLASK_APP=app.py
set FLASK_APP=app.py
flask run
