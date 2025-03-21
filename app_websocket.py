from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from flask_socketio import SocketIO, emit
import os
import uuid
from tools.image_extraction_yolo_function import extract_objects
from src.service.upload_s3 import upload_single_image
from src.service.request_service import create_request
import base64
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(
    app, cors_allowed_origins="*",
    max_http_buffer_size=50 * 1024 * 1024
)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('response', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('stream_frame')
def handle_stream_frame(data):
    try:
        # Decode the base64 image data
        access_token = data["access_token"]
        image_data = base64.b64decode(data['frame'])
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Failed to decode image")

        # Generate a unique filename for the image
        request_id = uuid.uuid4()
        unique_filename = f"image-extractor-service/uploaded_image/{request_id}.png"
        local_filename = f"uploads/{request_id}.png"

        # Save the image to the uploads directory
        cv2.imwrite(local_filename, image)
        # s3_url = upload_single_image(image_data, object_name=unique_filename)
        create_request(custom_id=request_id, base_image="")

        # Call the extract_objects function with the image path
        extracted_objects = extract_objects(local_filename, "cropped_image", request_id, access_token=access_token)

        if os.path.exists(local_filename):
            os.remove(local_filename)
        
        if(extracted_objects):
            print(extracted_objects[0]);
            emit('response', extracted_objects[0])
        else:
            print('no object found')
            emit('error', 'no object detected')
        # # Send the extracted objects back to the client
        # emit('response', extracted_objects[0])
    except Exception as e:
        emit('response', {'error': str(e)})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, debug=True, port=port, host='0.0.0.0')