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

from src.service.upload_s3 import upload_single_image
from src.service.request_service import create_request

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
    responses:
      200:
        description: The image with the background removed and replaced with green.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    img = Image.open(file.stream)
    img = img.convert("RGBA")  # Ensure image is in RGBA format
    output = remove(img)

    # Create a green background
    green_bg = Image.new("RGBA", output.size, (0, 255, 0, 255))

    # Composite the image with the green background
    final_img = Image.alpha_composite(green_bg, output)

    # Convert the final image to bytes
    img_byte_arr = io.BytesIO()
    final_img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    image_id = uuid.uuid4()
    output_path = os.path.join('cropped_image', f"{image_id}.png")
    final_img.save(output_path, format='PNG')
    unique_filename = f"image-extractor-service/background_removed/{image_id}.png"

    image = cv2.imread(output_path)
    _, buffer = cv2.imencode('.png', image)
    file_obj = io.BytesIO(buffer)

    s3_url = upload_single_image(file_obj, object_name=unique_filename)

    if os.path.exists(output_path):
      os.remove(output_path)

    return jsonify({'message': 'Image processed and saved successfully', 'path': s3_url}), 200

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
    app.run(debug=True, port=port, host='0.0.0.0')