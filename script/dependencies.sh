#!/bin/bash

# install dependencies
'/usr/local/bin/python3.9' -m pip install six opencv-python cvlib gtts ultralytics flask prisma flasgger python-dotenv boto3 flask-socketio eventlet


# use this if you want to test using websocket client connection for debugging the websocket app
'/usr/local/bin/python3.9' -m pip install python-socketio