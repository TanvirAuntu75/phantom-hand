import cv2
import time

def test_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    start_time = time.time()
    frames = 0
    while frames < 30:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        frames += 1

    elapsed = time.time() - start_time
    print(f"Captured {frames} frames in {elapsed:.2f} seconds. FPS: {frames/elapsed:.2f}")
    cap.release()

test_camera()
