import cv2
import numpy as np
import os
import time
from core.hand_tracker import UltimateHandTracker

tracker = UltimateHandTracker(model_path=os.path.abspath('backend/hand_landmarker.task'))
frame = np.zeros((480, 640, 3), dtype=np.uint8)

for i in range(100):
    try:
        tracker.process_frame(frame)
    except Exception as e:
        print(f"Error on frame {i}: {e}")
        break
print("Finished!")
