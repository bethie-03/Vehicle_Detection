import cv2
from ultralytics import YOLO
import numpy as np
from configs import *

class RoadAnalysis:
    def __init__(self, model_path, image_path, road_length: float):
        self.model = YOLO(model_path)
        self.image = cv2.imread(image_path)
        self.mask = None
        self.mask_image = None
        self.drawing = False
        self.total_bounding_box_area = 0
        self.start_x = -1
        self.start_y = -1
        self.road_length = road_length
        self.bboxes = []
        self.points=[] #top_left, top_right, bottom_right, bottom_left
        self.points_array_list = None

        self.motorcycle_speed_min = 10 #km/h
        self.motorcycle_speed_average = 30 
        self.motorcycle_speed_max = 60 

        self.car_speed_min = 7
        self.car_speed_average = 25
        self.car_speed_max = 40
        
    def convert_array_list(self):
        self.points_array_list = np.array(self.points, np.int32)
        self.points_array_list = self.points_array_list.reshape((-1, 1, 2))
        
    def draw_call_back(self, event, x, y, flags, param):
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
                    self.convert_array_list()
                    cv2.circle(self.image, (self.start_x, self.start_y), 5, (0, 0, 255), -1)
                    cv2.polylines(self.image, [self.points_array_list], isClosed=False, color=(0, 0, 255), thickness=2)
                elif len(self.points) > 1 and len(self.points) < 4:
                    points_copy = self.points[-2:]
                    cv2.circle(self.image, (self.start_x, self.start_y), 5, (0, 0, 255), -1)
                    cv2.line(self.image, points_copy[0], points_copy[1], (0, 0, 255), 2)
                else:
                    cv2.circle(self.image, (self.start_x, self.start_y), 5, (0, 0, 255), -1) 
                cv2.imshow("Detection result", self.image)
    
    def empty_call_back(self, event, x, y, flags, param):
        pass
    
    def create_mask_image(self) -> int:
        height, width, _ = self.image.shape
        self.convert_array_list()
        self.mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(self.mask, [self.points_array_list], color=255)
        self.mask_image = cv2.bitwise_and(self.image,self.image, mask=self.mask)
    
    def calculate_total_zone_pixels(self) -> int:
        total_zone_area = cv2.countNonZero(self.mask)
        return total_zone_area
    
    def count_black_pixels_in_bounding_boxes(self, x1, y1, x2, y2):
        black_pixel = 0
        bounding_box_area = (x2 - x1 + 1) * (y2 - y1 + 1)
        
        for x in range(x1,x2):
            for y in range(y1, y2):
                pixel_value = self.mask_image[y,x]
                if np.all(pixel_value==0):
                    black_pixel+=1 
                    
        self.total_bounding_box_area += bounding_box_area - black_pixel
        
    def calculate_intersection_area(self, box1, box2):
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        intersection_area = max(0, x2_i - x1_i + 1) * max(0, y2_i - y1_i + 1)
        return intersection_area
    
    def count_total_overlap_area(self):
        total_overlap_area = 0
        bboxes = self.bboxes.copy()
        while len(bboxes) > 1:
            for i in range(1, len(bboxes)):
                intersection_area = self.calculate_intersection_area(bboxes[0][:4], bboxes[i][:4])
                total_overlap_area += intersection_area
            bboxes.pop(0)
            
        self.total_bounding_box_area -= total_overlap_area

    def calculate_ratio(self):
        self.count_total_overlap_area() 
        total_zone_area = self.calculate_total_zone_pixels()
        ratio = self.total_bounding_box_area/total_zone_area
        return ratio
        
    def find_indices_of_min_value(self, distances: list):
        min_value = min(distances)
        return [index for index, value in enumerate(distances) if value == min_value]
    
    def find_indices_of_max_value(self, distances: list):
        max_value = max(distances)
        return [index for index, value in enumerate(distances) if value == max_value]

    def find_furthest_vehicle_position(self):
        top_left, top_right, bottom_right, bottom_left = self.points
        road_height = max(bottom_right[1], bottom_left[1]) - max(top_left[1], top_right[1]) + 1
        
        nearest_to_the_top_distances = []
        furthest_to_the_bottom_distances = []
        
        for box in self.bboxes:
            distance = max(0, box[1] - max(top_left[1], top_right[1]) + 1)
            nearest_to_the_top_distances.append(distance)
            
        indices_of_min_value = self.find_indices_of_min_value(nearest_to_the_top_distances)
                
        if len(indices_of_min_value) > 1:
            for index in indices_of_min_value:
                distance = max(bottom_right[1], bottom_left[1]) - self.bboxes[index][3] + 1
                furthest_to_the_bottom_distances.append(distance)
            indices_of_max_value = self.find_indices_of_max_value(furthest_to_the_bottom_distances)
            return furthest_to_the_bottom_distances[indices_of_max_value[0]], indices_of_min_value[indices_of_max_value[0]]
        else:
            furthest_to_the_bottom_distance = max(bottom_right[1], bottom_left[1]) - self.bboxes[indices_of_min_value[0]][3] + 1
            return road_height, furthest_to_the_bottom_distance , indices_of_min_value[0]
    
    def create_front_vehicle_zone(self):
        _, _, bottom_right, bottom_left = self.points
        _, _ , furthest_index = self.find_furthest_vehicle_position()
        x1, y1, x2, _, _ = self.bboxes[furthest_index]
        front_zone_box = (x1 - (x2 - x1), y1, x2 + (x2 - x1), max(bottom_right[1], bottom_left[1]))
        front_zone_height = front_zone_box[3] - front_zone_box[1]
        cv2.rectangle(self.image, (front_zone_box[0], front_zone_box[1]), (front_zone_box[2], front_zone_box[3]), (255,0,0), 2)
        return front_zone_box, front_zone_height
    
    def check_front_vehicle_appearance(self, furthest_vehicle_y2):
        front_zone_box, front_zone_height = self.create_front_vehicle_zone()
        for box in self.bboxes:
            intersection_area = self.calculate_intersection_area(box[:4], front_zone_box)
            if intersection_area != 0:
                distance_between_vehicles = box[3] - furthest_vehicle_y2
                ratio_of_distance_to_road_height = distance_between_vehicles / front_zone_height
                print(ratio_of_distance_to_road_height)
                if ratio_of_distance_to_road_height >= 0.5:
                    continue
                else:
                    cv2.rectangle(self.image, (box[0], box[1]), (box[2], box[3]), (255,0,0), 2)
                    return True
        return False 

    def calculate_actual_speed(self, v_min, v_average, v_max, ratio):
        ratio_deviation = 0.5 - ratio
        if ratio_deviation < 0:
            ratio_deviation_percentage = (abs(ratio_deviation) / (0.8 - 0.5)) 
            actual_speed = v_average - ((v_average - v_min) * ratio_deviation_percentage)
        elif ratio_deviation > 0:
            ratio_deviation_percentage = (abs(ratio_deviation) / 0.5) 
            actual_speed = v_average + ((v_max - v_average) * ratio_deviation_percentage)
        else:
            return v_average
        return actual_speed

    def calculate_time_for_furthest_vehicle_to_light(self, ratio):
        road_height, furthest_vehicle_to_light_height , index = self.find_furthest_vehicle_position()
        furthest_vehicle_to_light_distance = (furthest_vehicle_to_light_height / road_height) * self.road_length
        if self.check_front_vehicle_appearance(self.bboxes[index][3]) == True:
            print('yes')
            if self.bboxes[index][4] == 5:
                vehicle_speed = self.calculate_actual_speed(self.motorcycle_speed_min, 
                                                            self.motorcycle_speed_average, 
                                                            self.motorcycle_speed_max, 
                                                            ratio)
            else:
                vehicle_speed = self.calculate_actual_speed(self.car_speed_min, 
                                                            self.car_speed_average, 
                                                            self.car_speed_max, 
                                                            ratio)
        else:
            print('no')
            if self.bboxes[index][4] == 5:
                vehicle_speed = self.motorcycle_speed_max
            else:
                vehicle_speed = self.car_speed_max
        time = furthest_vehicle_to_light_distance/vehicle_speed
        cv2.rectangle(self.image, (self.bboxes[index][0], self.bboxes[index][1]), (self.bboxes[index][2], self.bboxes[index][3]), (255,0,0), 2)
        cv2.putText(self.image, f'Time: {int(time*3600)}s', (10,100), cv2.FONT_HERSHEY_DUPLEX, 1, color=(255,255,255), thickness=3)
    
    def road_analyse(self):
        cv2.imshow("Detection result", self.image)
        cv2.setMouseCallback("Detection result", self.draw_call_back)
        
        if cv2.waitKey(0) == ord('x') or cv2.waitKey(0) == ord('X'):  
            cv2.setMouseCallback("Detection result", self.empty_call_back)
            self.convert_array_list() 
            cv2.polylines(self.image, [self.points_array_list], isClosed=True, color=(0, 0, 255), thickness=2)
            cv2.imshow('Detection result', self.image) 
            
            self.create_mask_image()
            results = self.model(self.mask_image)[0]
            
            if len(results.boxes.data) > 0:
                for result in results.boxes.data:
                    x1, y1, x2, y2 = list(map(int, result[:4])) 
                    class_id = int(result[5])
                    self.bboxes.append([x1,y1,x2,y2, class_id])
                    self.count_black_pixels_in_bounding_boxes(x1, y1, x2, y2)
                    
                    cv2.putText(self.image, f'{self.model.names[class_id]}', (x1,y1), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.rectangle(self.image, (x1,y1), (x2,y2), (0,255,0), 2)
                    
                ratio = self.calculate_ratio()
                if ratio <= 0.8:
                    self.calculate_time_for_furthest_vehicle_to_light(ratio)
                cv2.putText(self.image, f'Ratio: {ratio}', (10,50), cv2.FONT_HERSHEY_DUPLEX, 1, color=(255,255,255), thickness=3)\
                    
            else:
                cv2.putText(self.image, f'NO DETECTION', (10,50), cv2.FONT_HERSHEY_DUPLEX, 1, color=(255,255,255), thickness=3)               
            cv2.imshow('Detection result', self.image) 
            cv2.waitKey(0)
            cv2.destroyAllWindows()

if __name__ == '__main__':       
    calculate = RoadAnalysis(MODEL_PATH, IMAGE_PATH, ROAD_LENGTH)
    calculate.road_analyse()