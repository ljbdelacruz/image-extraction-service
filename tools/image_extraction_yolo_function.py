import os
import cv2
from ultralytics import YOLO
from io import BytesIO
from dotenv import load_dotenv
import uuid
from src.service.upload_s3 import upload_single_image
from src.service.request_service import create_image
from src.service.gatherer_service import scanner_service

load_dotenv()

model = YOLO(os.getenv('MODEL_PATH'))
s3_base_url=os.getenv('S3_BASE_URL')

def extract_objects(image_path, output_dir='cropped_images', request_id = '', access_token=''):
    """
    Extract objects from an image and save the cropped images.

    Parameters:
    - image_path: str, path to the input image
    - output_dir: str, directory to save the cropped images

    Returns:
    - List of dictionaries containing bounding box coordinates, confidence scores, and class IDs
    """

    os.makedirs(output_dir, exist_ok=True)

    # Read the image
    image = cv2.imread(image_path)

    # Perform object detection
    results = model(image)

    extracted_objects = []

    # Iterate over the results and draw bounding boxes
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()  # Bounding box coordinates
        confidences = result.boxes.conf.cpu().numpy()  # Confidence scores
        class_ids = result.boxes.cls.cpu().numpy().astype(int)  # Class IDs

        for i, (box, confidence, class_id) in enumerate(zip(boxes, confidences, class_ids)):
            x1, y1, x2, y2 = box

            # Extract the cropped image
            cropped_image = image[int(y1):int(y2), int(x1):int(x2)]
            unique_filename = f"{uuid.uuid4()}.png"
            cropped_image_path = os.path.join(output_dir, unique_filename)
            _, buffer = cv2.imencode('.jpg', cropped_image)
            file_obj = BytesIO(buffer)

            object_name = f"image-extractor-service/cropped_images/{unique_filename}"

            s3_url = upload_single_image(file_obj, object_name=object_name)

            create_image(s3_url, request_id)
            s3_url_key = s3_url.replace(s3_base_url, "")
            extracted_objects.append({
                'confidence': f'{confidence * 100:.2f}',
                'label': model.names[class_id],
                's3_uri': s3_url_key
            })

            if os.path.exists(cropped_image_path):
                os.remove(cropped_image_path)

    return extracted_objects