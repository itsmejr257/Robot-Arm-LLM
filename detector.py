import os
import shutil
import time
from pathlib import Path

import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random
import numpy as np
import pyrealsense2 as rs
from imageprocesschatgpt import *


##Hide Warnings
"""
import warnings
import sys
import os
warnings.simplefilter("ignore")
sys.stderr = open(os.devnull, 'w')
"""


from models.experimental import attempt_load
from utils.general import (
    check_img_size, non_max_suppression, scale_coords,
    xyxy2xywh, plot_one_box, set_logging)
from utils.torch_utils import select_device, time_synchronized
from utils.datasets import letterbox


def detect(weights='yolov5m.pt', source='0', img_size=640, conf_thres=0.25, iou_thres=0.45, 
           device='', view_img=True, save_txt=False, save_conf=False, save_dir='inference/output', 
           classes=None, agnostic_nms=False, augment=False):
    out, imgsz = save_dir, img_size
    webcam = source == '0' or source.startswith(('rtsp://', 'rtmp://', 'http://')) or source.endswith('.txt')

    # Initialize
    set_logging(-1)
    device = select_device(device)
    if os.path.exists(out):  # output dir
        shutil.rmtree(out)  # delete dir
    os.makedirs(out)  # make new dir
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    imgsz = check_img_size(imgsz, s=model.stride.max())  # check img_size
    if half:
        model.half()  # to FP16

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]

    # Run inference
    t0 = time.time()
    img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
    _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)

    # Start streaming
    pipeline.start(config)
    align_to_color = rs.align(rs.stream.color)

    # Wait for a coherent pair of frames: depth and color
    frames = pipeline.wait_for_frames()
    frames = align_to_color.process(frames)
    color_frame = frames.get_color_frame()
    color_image = np.asanyarray(color_frame.get_data())

    #Save captured image
    image_dir = os.path.join(os.getcwd(), 'images')
    image_path = os.path.join(image_dir, 'captured_image.jpg')
    cv2.imwrite(image_path, color_image)

    sources = [source]
    imgs = [None]
    path = sources
    imgs[0] = color_image
    im0s = imgs.copy()
    img = [letterbox(x, new_shape=imgsz)[0] for x in im0s]
    img = np.stack(img, 0)
    img = img[:, :, :, ::-1].transpose(0, 3, 1, 2)  # BGR to RGB, to 3x416x416, uint8 to float32
    img = np.ascontiguousarray(img, dtype=np.float16 if half else np.float32)
    img /= 255.0  # 0 - 255 to 0.0 - 1.0

    # Get detections
    img = torch.from_numpy(img).to(device)
    if img.ndimension() == 3:
        img = img.unsqueeze(0)
    t1 = time_synchronized()
    pred = model(img, augment=augment)[0]

    # Apply NMS
    pred = non_max_suppression(pred, conf_thres, iou_thres, classes=classes, agnostic=agnostic_nms)
    t2 = time_synchronized()

    detected_objects = []

    for i, det in enumerate(pred):  # detections per image
        p, s, im0 = path[i], '%g: ' % i, im0s[i].copy()
        s += '%gx%g ' % img.shape[2:]  # print string
        gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
        img_height, img_width = im0.shape[:2]
        center_x_offset = img_width // 2
        center_y_offset = img_height // 2

        # Draw a small dot at the center of the image
        cv2.circle(im0, (center_x_offset, center_y_offset), 5, (0, 0, 255), -1)

        if det is not None and len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

            # Print results
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()  # detections per class
                s += '%g %ss, ' % (n, names[int(c)])  # add to string

            # Write results
            for *xyxy, conf, cls in reversed(det):
                xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                line = (cls, conf, *xywh) if save_conf else (cls, *xywh)  # label format

                label = '%s %.2f' % (names[int(cls)], conf)
                plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3)

                center_x, center_y = int((xyxy[0] + xyxy[2]) / 2) - center_x_offset, int((xyxy[1] + xyxy[3]) / 2) - center_y_offset

                detected_objects.append({
                    'label': names[int(cls)],
                    'confidence': conf.item(),
                    'coordinates': (center_x, center_y),
                })

        # Display results
        if view_img:
            cv2.imshow(p, im0)
            cv2.waitKey(0)  # Wait for a key press to exit
            cv2.destroyAllWindows()

    detected_objects.append({
        'overall_picture_description' : process_image_cgpt('images/captured_image.jpg')
    })
    
    return detected_objects
