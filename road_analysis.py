import cv2
from ultralytics import YOLO
import cv2
import numpy as np

class RoadAnalysis:
    def __init__(self, model_path, image_path):
        self.model = YOLO(model_path)
        self.image = cv2.imread(image_path)
        self.mask = None
        self.mask_image = None
        self.drawing = False
        self.total_bounding_box_pixels = 0
        self.start_x = -1
        self.start_y = -1
        self.points=[] #top_left, top_right, bottom_right, bottom_left
    
    def convert_array_list(self):
        points_array_list = np.array(self.points, np.int32)
        points_array_list = points_array_list.reshape((-1, 1, 2))
        return points_array_list
        
    def draw(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_x, self.start_y = x, y
            img_copy = self.image.copy()
            cv2.circle(img_copy, (self.start_x, self.start_y), 5, (0, 0, 255), -1)
            cv2.imshow("Detection result", img_copy)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            if cv2.waitKey(0) & 0xFF == ord('d'):
                cv2.imshow("Detection result", self.image)
            else:
                self.points.append([self.start_x, self.start_y])
                if len(self.points) >= 4:
                    points_array_list = self.convert_array_list()
                    cv2.circle(self.image, (self.start_x, self.start_y), 5, (0, 0, 255), -1)
                    cv2.polylines(self.image, [points_array_list], isClosed=False, color=(0, 0, 255), thickness=2)
                elif len(self.points) > 1 and len(self.points) < 4:
                    points_copy = self.points[-2:]
                    cv2.circle(self.image, (self.start_x, self.start_y), 5, (0, 0, 255), -1)
                    cv2.line(self.image, points_copy[0], points_copy[1], (0, 0, 255), 2)
                else:
                    cv2.circle(self.image, (self.start_x, self.start_y), 5, (0, 0, 255), -1) 
                cv2.imshow("Detection result", self.image)
    
    def create_mask_image(self) -> int:
        height, width, _ = self.image.shape
        points_array_list = self.convert_array_list()
        self.mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(self.mask, [points_array_list], color=255)
        self.mask_image = cv2.bitwise_and(self.image,self.image, mask=self.mask)
    
    def calculate_total_zone_pixels(self) -> int:
        height, width, _ = self.image.shape
        total_zone_pixels = 0
        for y in range(height):
            for x in range(width):
                pixel_value = self.mask[y,x]
                if pixel_value==255:
                    total_zone_pixels+=1
        return total_zone_pixels
    
    def count_black_pixels_in_bounding_boxes(self, x1, y1, x2, y2):
        black_pixel = 0
        for x in range(x1,x2):
            for y in range(y1, y2):
                self.total_bounding_box_pixels += 1
                pixel_value = self.mask_image[y,x]
                if np.all(pixel_value==0):
                    black_pixel+=1 
        self.total_bounding_box_pixels -= black_pixel
        
    def calculate_ratio(self):
        cv2.imshow("Detection result", self.image)
        cv2.setMouseCallback("Detection result", self.draw)
        
        if cv2.waitKey(0) == ord('x') or cv2.waitKey(0) == ord('X'):  
            points_array_list = self.convert_array_list() 
            cv2.polylines(self.image, [points_array_list], isClosed=True, color=(0, 0, 255), thickness=2)
            cv2.imshow('Detection result', self.image) 
            
            self.create_mask_image()
            results = self.model(self.mask_image)[0]
            
            if results is not None:
                for result in results.boxes.data:
                    x1, y1, x2, y2 = list(map(int, result[:4])) 
                    class_id = int(result[5])
                    self.count_black_pixels_in_bounding_boxes(x1, y1, x2, y2)
                    cv2.putText(self.image, f'{self.model.names[class_id]}', (x1,y1), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.rectangle(self.image, (x1,y1), (x2,y2), (0,255,0), 2)
                        
                total_zone_pixels = self.calculate_total_zone_pixels()
                ratio = self.total_bounding_box_pixels/total_zone_pixels
            else:
                ratio = 0
                
            print(self.total_bounding_box_pixels, total_zone_pixels)
            cv2.putText(self.image, f'Ratio: {ratio}', (100,100), cv2.FONT_HERSHEY_DUPLEX, 1, color=(0,0,0), thickness=3)               
            cv2.imshow('Detection result', self.image) 
        if cv2.waitKey(0) == ord('b') or cv2.waitKey(0) == ord('B'): 
            cv2.destroyAllWindows()
                
calculate = RoadAnalysis(r'C:\Users\phuon\Documents\FPT\CN7\DAT301m\Vehicle Detection\weights\epoch40.pt', r"C:\Users\phuon\Documents\FPT\CN7\DAT301m\Vehicle Detection\Dataset\train\images\000000393_jpg.rf.300e40d07c0e36ed59d62df94d22d051.jpg")
calculate.calculate_ratio()