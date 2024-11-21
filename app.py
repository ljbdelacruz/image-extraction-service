from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flasgger import Swagger
import os
import uuid
import asyncio
from tools.image_extraction_yolo_function import extract_objects
from src.service.upload_s3 import upload_single_image
from src.service.request_service import create_request
import base64
import cv2
import numpy as np
from io import BytesIO
from ultralytics import YOLO

app = Flask(__name__)
swagger = Swagger(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/extract_objects', methods=['POST'])
async def extract_objects_endpoint():
    """
    Extract objects from an image using a YOLO model.
    ---
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: The image file to upload.
    responses:
      200:
        description: A list of extracted objects.
    """
    try:
        # Get the image from the request
        image_file = request.files['image']
        image_data = image_file.read()
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({'error': 'Failed to decode image'}), 400

        # Generate a unique filename for the image
        request_id = uuid.uuid4()
        unique_filename = f"{UPLOAD_FOLDER}/{request_id}.png"

        # Save the image to the uploads directory
        cv2.imwrite(unique_filename, image)

        # Call the extract_objects function with the image path
        model = YOLO(os.getenv('MODEL_PATH'))
        extracted_objects = await extract_objects(unique_filename, model, "cropped_image")

        return jsonify({'extracted_objects': extracted_objects})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('response', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('stream_frame')
async def handle_stream_frame(data):
    try:
        # Decode the base64 image data
        image_data = base64.b64decode(data['frame'])
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Failed to decode image")

        # Generate a unique filename for the image
        request_id = uuid.uuid4()
        unique_filename = f"{UPLOAD_FOLDER}/{request_id}.png"

        # Save the image to the uploads directory
        cv2.imwrite(unique_filename, image)

        # Call the extract_objects function with the image path
        model = YOLO(os.getenv('MODEL_PATH'))
        extracted_objects = await extract_objects(unique_filename, model, "cropped_image")

        # Send the extracted objects back to the client
        emit('response', {'extracted_objects': extracted_objects})
    except Exception as e:
        emit('response', {'error': str(e)})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    import eventlet
    eventlet.monkey_patch()
    socketio.run(app, host='0.0.0.0', port=port, debug=True)