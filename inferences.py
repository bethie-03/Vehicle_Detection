import ultralytics
import cv2
import time
from load_config import get_config_yaml
from ultralytics import RTDETR
ultralytics.checks()
import argparse
import os


#setup path 

def get_args():
    parser = argparse.ArgumentParser(description="Train faster-rcnn")
    parser.add_argument("--source", "-src", type=str, default=None, help="path to data")

    args = parser.parse_args()
    return args

def inferences(args):
    if not os.path.exists(args.source):
        return (f"Không tồn tại đường dẫn: {args.source}.")
    else:
        cap = cv2.VideoCapture(args.source)        
        if not cap.isOpened():
            return ("Không đúng định dạng video hoặc hình ảnh.")
        # Kiểm tra số lượng khung hình
        num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) 
        # Nếu chỉ có một khung hình, đó là ảnh
        if num_frames == 1:
            data_type = "image"
        else:
            data_type = "video"
        
    # Loop through the video frames
        model = RTDETR(weight_path)
        begin = time.time()
        while cap.isOpened():
            # Read a frame from the video
            success, frame = cap.read()

            if success:
                # Run YOLOv8 inference on the frame
                results = model(frame)

                # Visualize the results on the frame
                annotated_frame = results[0].plot()

                # Display the annotated frame
                cv2.imshow("RT_DERT Inference", annotated_frame)
                if data_type == 'image':         
                    end = time.time() - begin
                    print(f'total time : {end} second')
                    cv2.waitKey(0)
                    cap.release()
                    cv2.destroyAllWindows()
                    break
                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                # Break the loop if the end of the video is reached
                end = time.time() - begin
                print(f'total time : {end} second')
                cap.release()
                cv2.destroyAllWindows()
                break
  


if __name__ =="__main__":
    weight_path = get_config_yaml('weight_engine')
    args = get_args()
    inferences(args)





