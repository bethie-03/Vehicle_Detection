import ultralytics
import cv2
import time
from ultralytics import RTDETR
from load_config import get_config_yaml
ultralytics.checks()
weight_pt = get_config_yaml('weight_pt')
model = RTDETR(weight_pt)
model.export(format='TensorRT', half=True, device = 0)
