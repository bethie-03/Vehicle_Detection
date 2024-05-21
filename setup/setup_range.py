import cv2
import numpy as np
from load_config import get_config_yaml, get_absolute_path
import argparse
import os


def get_args():
    parser = argparse.ArgumentParser(description="Train faster-rcnn")
    parser.add_argument("--source", "-src",default= source, type=str, help="path to data")
    parser.add_argument("--warning_range", "-wa", type=str, default='/mnt/d/VietNguyenAI/Vehicle_Detection/setup/warning_range', help="path to warning range file")
    parser.add_argument("--classnames", "-cl", type=str, help="path to classnames file")
    
    # Trả về các tham số đã được phân tích cú pháp
    return parser.parse_args()

def polygons_to_array(polygons):
    # Khởi tạo list để lưu tất cả các điểm trong tất cả các đa giác
    arr = []
    for i, polygon in enumerate(polygons):
        # Thêm tất cả các điểm của đa giác hiện tại vào list
        arr.extend(polygon)
        # Nếu không phải đa giác cuối cùng, thêm một dòng chứa 'np.nan' để phân tách giữa các đa giác
        if i < len(polygons) - 1:
            arr.append([np.nan, np.nan])
    return np.array(arr)

def handle_left_click(event, x, y, flags, param):
    global current_polygon

    # If the left mouse button was clicked, record the starting
    # (x, y) coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        current_polygon.append([x, y])

def draw_polygon(frame, points):
    if len(points) > 0:
        for point in points:
            cv2.circle(frame, (point[0], point[1]), 5, (0,0,255), -1) 
        if len(points) > 1:
            cv2.polylines(frame, [np.array(points)], False, (255, 0, 0), 2)
    return frame 

def open_and_draw_polygon_on_frame(video_path):
    global current_polygon, polygons
    # Initialization
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    cv2.namedWindow("frame")
    cv2.setMouseCallback("frame", handle_left_click)
    while True:
        overlay = frame.copy()

        # For each polygon, draw it on the frame
        for polygon in polygons:
            draw_polygon(overlay, polygon)
        draw_polygon(overlay, current_polygon)  # Also draw the current_polygon
        
        cv2.imshow("frame", overlay)
        key = cv2.waitKey(1) & 0xFF
        
        # When the 'w' key is pressed, finish the polygon
        if key == ord("w"):
            # Only finish if there are more than 2 points (forming a valid polygon)
            if len(current_polygon) > 2:  
                polygons.append(current_polygon.copy())
                current_polygon = []
        
        # Break the loop either when 'q' key or space bar is pressed
        elif key == ord("q") or key == ord(" "):
            break

    cap.release()
    cv2.destroyAllWindows()


    # Save polygons points to the text file
    if not  os.path.exists('warning_range'):
        os.makedirs('warning_range')
    warning_folder =  os.path.abspath('warning_range')
    np.savetxt(f'{warning_folder}/all_polygons.txt', polygons_to_array(polygons), delimiter=' ', fmt='%f')

    return polygons 

if __name__ =="__main__":
    # List of polygons
    polygons = []
    # The current polygon being drawn
    current_polygon = []
    source = get_config_yaml('source')
    print(source)
    args = get_args()
    polygons = open_and_draw_polygon_on_frame(args.source)
    # Print polygon points
    for i, polygon_points in enumerate(polygons):
        print(f"Polygon {i} points:", polygon_points)