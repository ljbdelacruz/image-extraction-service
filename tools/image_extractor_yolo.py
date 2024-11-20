import numpy as np
import cv2
from ultralytics import YOLO
import os

# Load a pre-trained YOLOv8n model
model = YOLO('/Users/laineljohndelacruz/Desktop/Projects/mvg/tempproject/object-detection-streaming-project/yolo/yolov8n.pt')

# Create a directory to save the cropped images
output_dir = 'cropped_images'
os.makedirs(output_dir, exist_ok=True)

# Path to the input image
image_path = '/Users/laineljohndelacruz/Desktop/Projects/mvg/tempproject/object-detection-streaming-project/dataset/bus.png'

# Read the image
image = cv2.imread(image_path)

# Perform object detection
results = model(image)

# Iterate over the results and draw bounding boxes
for result in results:
    boxes = result.boxes.xyxy.cpu().numpy()  # Bounding box coordinates
    confidences = result.boxes.conf.cpu().numpy()  # Confidence scores
    class_ids = result.boxes.cls.cpu().numpy().astype(int)  # Class IDs

    for i, (box, confidence, class_id) in enumerate(zip(boxes, confidences, class_ids)):
        x1, y1, x2, y2 = box
        label = f"{model.names[class_id]}: {confidence * 100:.2f}%"
        # cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        # cv2.putText(image, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Extract the cropped image
        cropped_image = image[int(y1):int(y2), int(x1):int(x2)]

        # Save the cropped image
        cropped_image_path = os.path.join(output_dir, f"{i}_{model.names[class_id]}.jpg")
        cv2.imwrite(cropped_image_path, cropped_image)

# Display the image with bounding boxes
cv2.imshow('YOLOv8 Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()