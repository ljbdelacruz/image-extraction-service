from PIL import Image
from rembg import remove
import uuid
import io
import os
import cv2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def image_background_remover(file, path, output_dir):
    try:
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output = remove(file)
        # Create a green background
        green_bg = Image.new("RGBA", output.size, (0, 255, 0, 255))
        # Composite the image with the green background
        final_img = Image.alpha_composite(green_bg, output)
        # Convert the final image to bytes
        img_byte_arr = io.BytesIO()
        final_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        image_id = uuid.uuid4()
        output_path = os.path.join(output_dir, f"{image_id}.png")
        final_img.save(output_path, format='PNG')
        unique_filename = f"{path}/{image_id}.png"

        image = cv2.imread(output_path)
        _, buffer = cv2.imencode('.png', image)
        file_obj = io.BytesIO(buffer)

        return file_obj, unique_filename, output_path
    except Exception as e:
        logger.error(f"Error in image_background_remover: {e}")
        raise