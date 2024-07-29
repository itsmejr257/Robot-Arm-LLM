import cv2
import numpy as np
import pyrealsense2 as rs
import torch
import os
from imageprocesschatgpt import *

def detect():
    # Load the YOLOv5 model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

    # Set up the RealSense D455 camera
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline.start(config)

    # Get the latest frame from the camera
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()

    # Convert the frame to a numpy array
    color_image = np.asanyarray(color_frame.get_data())

    # Get image dimensions
    height, width, _ = color_image.shape
    center_x_image = width // 2
    center_y_image = height // 2

    # List to store detected objects
    detected_objects = []

    # Detect objects using YOLOv5
    results = model(color_image)

    #Save captured image
    image_dir = os.path.join(os.getcwd(), 'images')
    image_path = os.path.join(image_dir, 'captured_image.jpg')
    cv2.imwrite(image_path, color_image)

    # Process the results
    for result in results.xyxy[0]:
        x1, y1, x2, y2, confidence, class_id = result

        # Calculate the center coordinates of the bounding box
        center_x_bbox = int((x1 + x2) / 2)
        center_y_bbox = int((y1 + y2) / 2)

        # Adjust coordinates to have the origin at the center of the image
        adjusted_x = center_x_bbox - center_x_image
        adjusted_y = center_y_bbox - center_y_image

        # Store detected object information
        detected_objects.append({
            'label': model.names[int(class_id)],
            'confidence': confidence.item(),
            'coordinates': (adjusted_x, adjusted_y),
        })

        # Draw a rectangle around the object
        cv2.rectangle(color_image, (int(x1), int(y1)), (int(x2), int(y2)), (252, 119, 30), 2)

        # Draw the label with class name, confidence, and coordinates
        label = f"{model.names[int(class_id)]}: {confidence:.2f} ({adjusted_x}, {adjusted_y})"
        cv2.putText(color_image, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (252, 119, 30), 2)

    # Show the image
    cv2.imshow("Color Image", color_image)
    cv2.waitKey(1)

    detected_objects.append({
        'overall_picture_description' : process_image_cgpt('images/captured_image.jpg')
    })

    return detected_objects
