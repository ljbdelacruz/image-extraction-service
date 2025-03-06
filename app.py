from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
import os
from flasgger import Swagger
from tools.image_extraction_yolo_function import extract_objects
import uuid
from PIL import Image, ImageOps
import io
from rembg import remove
from io import BytesIO
import cv2
import logging
import threading
from kafka.kafka_producer import produce_message
from kafka.kafka_consumer import consume_messages

from src.service.upload_s3 import upload_single_image
from src.service.request_service import create_request
from src.service.image_service import image_background_remover

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a dummy image to trigger the model download
dummy_image = Image.new("RGBA", (1, 1), (255, 255, 255, 255))
output = remove(dummy_image)

app = Flask(__name__)
swagger = Swagger(app, config={
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/api/swagger.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/"
})

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/extract_frames_and_remove_bg', methods=['POST'])
def extract_frames_and_remove_bg():
    """
    Extract frames from video every 2 seconds, remove background from each frame, and save as images.
    ---
    parameters:
      - name: video
        in: formData
        type: file
        required: true
        description: The video file to upload.
      - name: s3_directory
        in: formData
        type: string
        required: true
        description: The s3_directory prefix for the processed frames.
    responses:
      200:
        description: The frames with the background removed and saved as images.
    """
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400

        if 's3_directory' not in request.form:
            return jsonify({'error': 'No unique filename provided'}), 400

        file = request.files['video']
        s3_directory = request.form['s3_directory']
        image_id = uuid.uuid4()
        file_extension = os.path.splitext(file.filename)[1]
        input_path = os.path.join('processed_video', f"{image_id}.{file_extension}")

        # Ensure the directory exists
        if not os.path.exists('processed_video'):
            os.makedirs('processed_video')

        file.save(input_path)

        # Open the video file
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * 2)  # Capture one frame every 2 seconds
        frame_count = 0
        processed_frame_count = 0
        s3_urls = []
        file_keys = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process every nth frame
            if frame_count % frame_interval == 0:
                # Convert frame to PIL image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)

                file_obj, unique_filename, output_path = image_background_remover(
                    pil_img, 
                    s3_directory,
                    "processed_video")

                s3_url, file_key = upload_single_image(file_obj, object_name=unique_filename)

                # Append the output path to the list
                s3_urls.append(s3_url)
                file_keys.append(file_key)

                if os.path.exists(output_path):
                    os.remove(output_path)

                processed_frame_count += 1

            frame_count += 1

        cap.release()

        if os.path.exists(input_path):
            os.remove(input_path)

        return jsonify({'message': 'Frames processed and saved successfully', 'frame_count': processed_frame_count, 's3': s3_urls, 'file_keys': file_keys}), 200
    except Exception as e:
        logger.error(f"Error in extract_frames_and_remove_bg: {e}")
        return jsonify({'error': 'An error occurred while processing the video'}), 500

@app.route('/remove_image_bg', methods=['POST'])
def remove_image_bg():
    """
    Remove Background from detected image and replace it with green background.
    ---
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: The image file to upload.
      - name: s3_directory
        in: formData
        type: string
        required: true
        description: The s3_directory prefix for the processed image.
    responses:
      200:
        description: The image with the background removed and replaced with green.
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        if 's3_directory' not in request.form:
            return jsonify({'error': 'No unique filename provided'}), 400

        file = request.files['image']
        s3_directory = request.form['s3_directory']
        img = Image.open(file.stream)
        img = img.convert("RGBA")  # Ensure image is in RGBA format

        file_obj, unique_filename, output_path = image_background_remover(img, s3_directory, "cropped_image")
        s3_url, fileKey = upload_single_image(file_obj, object_name=unique_filename)
        if os.path.exists(output_path):
            os.remove(output_path)

        # Produce a message to Kafka
        message = {'key': str(uuid.uuid4()), 'value': s3_url}
        produce_message('image_processed', message)

        return jsonify({'message': 'Image processed and saved successfully', 'path': fileKey, 's3': s3_url}), 200
    except Exception as e:
        logger.error(f"Error in remove_image_bg: {e}")
        return jsonify({'error': 'An error occurred while processing the image'}), 500

@app.route('/extract_objects', methods=['POST'])
def extract_objects_endpoint():
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
        schema:
          type: array
          items:
            type: object
            properties:
              label:
                type: string
              cropped_image_path:
                type: string
      400:
        description: No image file provided.
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        request_id = uuid.uuid4()
        image_file = request.files['image']
        unique_filename = f"image-extractor-service/uploaded_image/{request_id}.png"
        local_filename = f"{request_id}.png"

        image_path = os.path.join('uploads', local_filename)

        # Ensure the directory exists
        if not os.path.exists('uploads'):
            os.makedirs('uploads')

        image_file.save(image_path)
        s3_url, file_key = upload_single_image(image_file, object_name=unique_filename)
        create_request(custom_id=request_id, base_image=s3_url)
        
        # Call the extract_objects function
        extracted_objects = extract_objects(image_path, "cropped_image", request_id)

        if os.path.exists(image_path):
            os.remove(image_path)

        return jsonify(extracted_objects)
    except Exception as e:
        logger.error(f"Error in extract_objects_endpoint: {e}")
        return jsonify({'error': 'An error occurred while extracting objects from the image'}), 500

if __name__ == '__main__':
    # Start Kafka consumer in a separate thread
    consumer_thread = threading.Thread(target=consume_messages, args=('image_processed',))
    consumer_thread.start()

    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port, host='0.0.0.0')