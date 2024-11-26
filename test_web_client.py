import base64
import json
import cv2
import socketio

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
    image = cv2.imread(image_path)
    _, buffer = cv2.imencode('.jpg', image)
    frame_data = base64.b64encode(buffer).decode('utf-8')
    sio.emit('stream_frame', {'frame': frame_data, 'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDRjOWY1MS1kNjMxLTRlZDYtOTljMy0yNTZhYTRiMDg4YzciLCJ1dWlkIjoiZ29vZ2xlLW9hdXRoMnwxMTI5NzIwNDUwMDEyNjExMzYwNTkiLCJpYXQiOjE3MzI1NzM5NzQsImV4cCI6MTczMjY2MDM3NH0.OAto8zEMj1HQKmvUMYIbjYyDmQwDVw9Be0QjIpvXA6Y'})

try:
    sio.connect("http://localhost:4000")
    send_frame('/Users/laineljohndelacruz/Desktop/Projects/mvg/tempproject/image-extraction-service/test_assets/image2.png')
    sio.wait()
    sio.disconnect();
except Exception as e:
    print(f"Failed to connect to WebSocket server: {e}")