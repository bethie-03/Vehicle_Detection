import cv2
import numpy as np
import math
import torch
import os
import ultralytics
from ultralytics import RTDETR
import matplotlib.pyplot as plt
import threading
from threading import Timer
import time
import cvzone
from matplotlib.path import Path
import argparse
from setup.load_config import get_config_yaml, string_to_list
from collections import defaultdict
from shapely.geometry import Point, Polygon
from scipy.spatial import distance
from datetime import datetime, timedelta




def get_args():
    parser = argparse.ArgumentParser(description="Train faster-rcnn")
    parser.add_argument("--source", "-src", type=str, default=source, help="path to data")
    parser.add_argument("--model", "-w", type=str, default=weight_path, help="")
    parser.add_argument("--warning_range", "-wa", type=str, default= warning_range, help="")
    parser.add_argument("--classnames", "-cl", type=str, default=classnames, help="")


    args = parser.parse_args()
    return args

def load_polygons(filepath):
    # Load polygons points from text file
    polygons_points = np.loadtxt(filepath, delimiter=' ').reshape(-1, 2)
    polygons = []
    current_polygon = []
    for point in polygons_points:
        if np.isnan(point).any():
            # If encounter a row with nan value, means start of new polygon, add current polygon to polygons
            polygons.append(current_polygon)
            current_polygon = []
        else:
            current_polygon.append(list(map(int, point)))
    # Add the last polygon
    if current_polygon:
        polygons.append(current_polygon)
    return polygons


def draw_polygons(image, polygons):
    overlay = image.copy()
    overlay_alpha = 0.2
    overlay_color=  (0, 255, 255)
    # Loop through each polygon
    for polygon in polygons:
        if len(polygon) > 0:
            for point in polygon:
                cv2.circle(image, (int(point[0]), int(point[1])), 5, (0,0,255), -1) 
            if len(polygon) > 1:
                cv2.polylines(image, [np.array(polygon, dtype=int)], False, (255, 0, 0), 2)
                cv2.fillPoly(overlay, [np.array(polygon, dtype=int)], overlay_color)
    cv2.addWeighted(overlay, overlay_alpha, image, 1 - overlay_alpha, 0, image)
    return image

def apply_mask(image, polygons):
    mask = np.zeros_like(image[:, :, 0], dtype=np.uint8)
    # Vẽ tất cả các polygon lên mask
    for polygon in polygons:
        cv2.fillPoly(mask, [np.array(polygon, dtype=int)], 255)
    # Che phần không muốn hiển thị bằng cách áp dụng mask
    masked_img = cv2.bitwise_and(image, image, mask=mask)
    return masked_img




def non_max_suppression(boxes, scores, threshold):
    # Khởi tạo list chứa các index được chọn
    pick = []

    # Tính toán diện tích của các boxs
    area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])

    # Sắp xếp các boxes theo điểm số của chúng
    idxs = np.argsort(scores)

    while len(idxs) > 0:
        # Thêm index của bounding box có điểm số lớn nhất vào list chọn lựa
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # Tìm cặp IoU lớn nhất với box hiện tại và tất cả các box khác
        xx1 = np.maximum(boxes[i, 0], boxes[idxs[:last], 0])
        yy1 = np.maximum(boxes[i, 1], boxes[idxs[:last], 1])
        xx2 = np.minimum(boxes[i, 2], boxes[idxs[:last], 2])
        yy2 = np.minimum(boxes[i, 3], boxes[idxs[:last], 3])

        # Tính toán width và height của hình chữ nhật có diện tích giao nhau
        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)

        # Tính toán diện tích giao nhau
        overlap = w * h

        # Xóa hiện tại và tất cả các bounding box có IoU lớn hơn ngưỡng từ list các index
        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > threshold)[0])))

    return pick

def track_vehicle_in_polygon(boxes, track_ids, polygons, frame_tracks, disappeared_vehicles, track_history, frame_counter, last_detected_time):
    current_time = datetime.now()
    for idx, box in enumerate(boxes):
        track_id = track_ids[idx]
        x1, y1, x2, y2 = box
        centroid = [(x1 + x2) / 2, (y1 + y2) / 2]

        track_history[track_id].append(centroid)
        if len(track_history[track_id]) > frame_tracks:
            track_history[track_id].pop(0)

        point = Point(centroid)
        for polygon in polygons:
            if Polygon(polygon).contains(point):
                frame_counter[track_id] += 1
            
        last_detected_time[track_id] = current_time
    disappeared_ids = list(set(disappeared_vehicles.keys()) - set(track_ids))
    for track_id in disappeared_ids:
        if current_time - last_detected_time[track_id] > timedelta(seconds=2):
            del disappeared_vehicles[track_id]

    for track_id in track_ids:
        if track_id in disappeared_vehicles:
            if distance.euclidean(centroid, disappeared_vehicles[track_id]) < 50:
                print(f"Vehicle ID {track_id} has been re-identified.")
                disappeared_vehicles[track_id] = centroid
        else:
            disappeared_vehicles[track_id] = centroid

    return track_history, frame_counter

def predict_image(model,classnames, image_input, warming_range, disappeared_vehicles, track_history, frame_counter, last_detected_time):
    img = image_input
    img_input_model = img.copy()
    img_input_model = apply_mask(img_input_model, warming_range)
    img = draw_polygons(img, warming_range)

    results = model.track(img_input_model, persist=True)
    try:
        track_ids = results[0].boxes.id.int().cpu().tolist()
    except AttributeError:
        track_ids = []
    boxes = []
    classes = []
    scores = []

    for info in results:
        for box in info.boxes:
            confidence = box.conf[0]
            if confidence.item() > 0.20:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                boxes.append([x1, y1, x2, y2])
                class_id = int(box.cls.item())
                classes.append(class_id)
                scores.append(confidence.item())
                

    boxes = np.array(boxes)
    scores = np.array(scores)
    final_confidence = 0
    if len(boxes) > 0:
        idxs = non_max_suppression(boxes, scores, threshold=0.5)
        for idx in idxs:
            x1, y1, x2, y2 = boxes[idx]
            confidence = scores[idx]
            track_id = track_ids[idx]
            final_confidence = confidence
            w, h = x2 - x1, y2 - y1
            text = f'{classnames[classes[idx]]} ID: {track_id}'
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            thickness = 2
            color = (255, 255, 255)
            x, y = max(0, x1), max(35, y1)
            (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            text_height += baseline
            top_left = (x, y - text_height)
            bottom_right = (x + text_width, y + baseline)
            cv2.rectangle(img, top_left, bottom_right, (0, 0, 0), -1)
            cv2.putText(img, text, (x, y), font, font_scale, color, thickness)
            cvzone.cornerRect(img, (x1, y1, w, h), l=10)

    frame_tracks = 10
    track_history, frame_counter = track_vehicle_in_polygon(boxes, track_ids, warming_range, frame_tracks, disappeared_vehicles, track_history, frame_counter, last_detected_time)
    try:
        max_id = max(track_ids)
        if max_id > 100:
            model.predictor.trackers[0].reset()
    except:
        max_id = 0


    return img



def vision(args, classnames):
    if not os.path.exists(args.source):
        return f"Không tồn tại đường dẫn: {args.source}."
    else:
        cap = cv2.VideoCapture(args.source)
        if not cap.isOpened():
            return "Không đúng định dạng video hoặc hình ảnh."
        
        num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        data_type = "image" if num_frames == 1 else "video"
        
        model = RTDETR(args.model)
        begin = time.time()
        warming_range = load_polygons(args.warning_range)
        
        disappeared_vehicles = defaultdict(list)
        track_history = defaultdict(list)
        frame_counter = defaultdict(int)
        last_detected_time = defaultdict(lambda: datetime.now())

        while cap.isOpened():
            success, frame = cap.read()
            if success:
                results = predict_image(model,classnames, frame, warming_range, disappeared_vehicles, track_history, frame_counter, last_detected_time)
                cv2.imshow("RT_DETR Inference", results)
                if data_type == 'image':
                    end = time.time() - begin
                    print(f'total time : {end} second')
                    cv2.waitKey(0)
                    cap.release()
                    cv2.destroyAllWindows()
                    break
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                end = time.time() - begin
                print(f'total time : {end} second')
                cap.release()
                cv2.destroyAllWindows()
                break

if __name__ == "__main__":
    classnames = (get_config_yaml('classnames'))
    warning_range = get_config_yaml('warning_range')
    weight_path = get_config_yaml('weight_engine')
    source = get_config_yaml('source')
    args = get_args()
    vision(args, classnames)