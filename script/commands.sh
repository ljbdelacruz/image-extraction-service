#!/bin/bash


# install dependencies
'/usr/local/bin/python3.9' -m pip install six opencv-python cvlib gtts ultralytics flask prisma flasgger python-dotenv boto3 flask-socketio eventlet


# use this if you want to test using websocket client connection for debugging the websocket app
'/usr/local/bin/python3.9' -m pip install python-socketio

/usr/local/bin/python3.9 app_websocket.py

/usr/local/bin/python3.9 test_web_client.py

# running flask app
export FLASK_APP=app.py
set FLASK_APP=app.py
flask run
