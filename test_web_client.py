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

def send_frame(image_path):
    image = cv2.imread(image_path)
    _, buffer = cv2.imencode('.jpg', image)
    frame_data = base64.b64encode(buffer).decode('utf-8')
    sio.emit('stream_frame', {'frame': frame_data})

try:
    sio.connect("http://localhost:5000")
    send_frame('/Users/laineljohndelacruz/Desktop/Projects/mvg/tempproject/image-extraction-service/test_assets/image1.png')
    sio.wait()
    sio.disconnect();
except Exception as e:
    print(f"Failed to connect to WebSocket server: {e}")