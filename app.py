from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
import os
from flasgger import Swagger
from tools.image_extraction_yolo_function import extract_objects
import uuid
from flask_socketio import SocketIO, emit

from src.service.upload_s3 import upload_single_image
from src.service.request_service import create_request


app = Flask(__name__)
swagger = Swagger(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

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
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    request_id = uuid.uuid4()
    image_file = request.files['image']
    unique_filename = f"image-extractor-service/uploaded_image/{request_id}.png"
    local_filename = f"{request_id}.png"


    image_path = os.path.join('uploads', local_filename)
    os.makedirs('uploads', exist_ok=True)
    image_file.save(image_path)

    s3_url = upload_single_image(image_file, object_name=unique_filename)

    create_request(custom_id=request_id, base_image=s3_url)
    
    # Call the extract_objects function
    extracted_objects = extract_objects(image_path, "cropped_image", request_id)

    if os.path.exists(image_path):
        os.remove(image_path)

    return jsonify(extracted_objects)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port)