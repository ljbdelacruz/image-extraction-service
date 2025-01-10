import os
from dotenv import load_dotenv
load_dotenv()
import base64
import json
import cv2
import socketio
from src.service.gatherer_service import login

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to WebSocket server")

@sio.event
def disconnect():
    print("Disconnected from WebSocket server")

@sio.event
def response(data):
    print("Server response:", data)

@sio.event
def scan_result(data):
    print("Server response:", data)
    sio.disconnect()

def send_frame(image_path):
    client_id = os.getenv("AUTH_CLIENT_ID")
    secret = os.getenv('AUTH_CLIENT_SECRET')

    field = "destination"
    uuid = "google-oauth2|112972045001261136059"

    login_response = login(client_id, secret, field, uuid)
    access_token = login_response.get('access_token')
    if not access_token:
        raise ValueError("Failed to retrieve access token")

    image = cv2.imread(image_path)
    _, buffer = cv2.imencode('.jpg', image)
    frame_data = base64.b64encode(buffer).decode('utf-8')
    sio.emit('stream_frame', {'frame': frame_data, 'access_token': access_token})

try:
    sio.connect("http://localhost:4000")
    send_frame('/Users/laineljohndelacruz/Desktop/Projects/mvg/tempproject/image-extraction-service/test_assets/image2.png')
    sio.wait()
    sio.disconnect();
except Exception as e:
    print(f"Failed to connect to WebSocket server: {e}")