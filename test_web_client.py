import base64
import json
import cv2
from websocket import create_connection

def send_frame(ws, image_path):
    image = cv2.imread(image_path)
    _, buffer = cv2.imencode('.jpg', image)
    frame_data = base64.b64encode(buffer).decode('utf-8')
    ws.send(json.dumps({'frame': frame_data}))

try:
    ws = create_connection("ws://localhost:5000/socket.io/")
    print("Connected to WebSocket server")

    # Test the connection
    response = ws.recv()
    print("Server response:", response)

    # Send a test frame
    send_frame(ws, '/Users/laineljohndelacruz/Desktop/Projects/mvg/tempproject/image-extraction-service/test_assets/image1.png')

    # Receive the response
    response = ws.recv()
    print("Server response:", response)

    ws.close()
except Exception as e:
    print(f"Failed to connect to WebSocket server: {e}")