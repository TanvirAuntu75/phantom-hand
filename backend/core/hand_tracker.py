import cv2
import mediapipe as mp
import numpy as np
import time
from threading import Thread
from queue import Queue
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- Local Modules ---
from backend.core.kalman_filter import LandmarkSmoother
from backend.core.ghost_engine import GhostHand

class UltimateHandTracker:
    def __init__(self, model_path='hand_landmarker.task'):
        # ── Mediapipe Setup ───────────────────────────────────────────────────
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=2,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7,
            result_callback=self._ai_callback
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # ── State Management ──────────────────────────────────────────────────
        self._hand_data = []         # Most recent AI output
        self._fps_history = []
        self._last_time = time.time()
        
        # Identity Lock for Single-Hand Mode
        self._locked_label = None          # "Left" or "Right" — the chosen hand
        self._last_known_tip = None        # Normalised (x, y) of index tip [8]
        self._identity_lost_frames = 0    # Consecutive frames without our label
        self._MAX_IDENTITY_LOST = 15       # Increased to 0.25s to survive fast motion
        
        # Max normalised distance a tip is allowed to jump in ONE frame.
        self._MAX_JUMP = 0.35              # Increased for fast writing
        # ──────────────────────────────────────────────────────────────────────
        
        # Engines
        self.smoother = LandmarkSmoother()
        self.ghost = GhostHand(max_ghost_frames=12)

        self._last_timestamp_ms = -1 # to ensure monotonically increasing timestamps

    def _ai_callback(self, result: vision.HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        """ The pure AI thread. Executes only when the neural network spits out a result. """
        parsed_data = []
        if result.hand_landmarks:
            for hand_idx in range(len(result.hand_landmarks)):
                landmarks = result.hand_landmarks[hand_idx]
                parsed_lm = [(lm.x, lm.y, lm.z) for lm in landmarks]

                # We trust MediaPipe's internal classification.
                # If it's consistently swapped, we will handle it in the HUD,
                # but manual flipping in the logic often causes more confusion.
                label = result.handedness[hand_idx][0].category_name

                parsed_data.append({
                    "landmarks": parsed_lm,
                    "handedness": label
                })
        
        self._hand_data = parsed_data

    def _pick_locked_hand(self):
        """
        If multiple hands exist, we must stick to ONE to prevent drawing jitter.
        """
        if not self._hand_data:
            return None

        # 1. If we have a lock, look for that specific label
        if self._locked_label:
            for h in self._hand_data:
                if h["handedness"] == self._locked_label:
                    # Identity verification: don't jump to a hand across the screen
                    if self._last_known_tip is not None:
                        current_tip = h["landmarks"][8][:2]
                        dist = np.linalg.norm(np.array(current_tip) - np.array(self._last_known_tip))
                        if dist < self._MAX_JUMP:
                            self._identity_lost_frames = 0
                            self._last_known_tip = current_tip
                            return h
            
            # If we reached here, our locked hand is missing or jumped too far
            self._identity_lost_frames += 1
            if self._identity_lost_frames < self._MAX_IDENTITY_LOST:
                return "LOST" # Signal ghost fallback
            else:
                self._locked_label = None # Release lock
                self._last_known_tip = None

        # 2. No lock or lock lost -> Pick the highest confidence hand
        # For simplicity, we just pick the first one available
        best_hand = self._hand_data[0]
        self._locked_label = best_hand["handedness"]
        self._last_known_tip = best_hand["landmarks"][8][:2]
        self._identity_lost_frames = 0
        return best_hand

    def process_frame(self, frame, w, h):
        """
        The main pipeline loop.
        """
        timestamp_ms = int(time.time() * 1000)
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        self.detector.detect_async(mp_image, timestamp_ms)

        hand = self._pick_locked_hand()
        
        if hand == "LOST" or hand is None:
            # AI missed it or locked hand is gone -> Fallback to Ghost Engine (Optical Flow)
            ghost_lms = self.ghost.predict(frame)
            if ghost_lms:
                # Ghost data is in pixels, convert back to normalized for the smoother
                norm_ghost = [(p[0]/w, p[1]/h, 0.0) for p in ghost_lms]
                smoothed = self.smoother.smooth(norm_ghost)
                return smoothed, True
            return None, False

        # Fresh AI Data available
        lms = hand["landmarks"]
        
        # Update Ghost with fresh pixel-space data for the next frame
        pixel_lms = [(lm[0]*w, lm[1]*h) for lm in lms]
        self.ghost.update_real_data(frame, pixel_lms)

        # Apply Kalman Smoothing
        smoothed = self.smoother.smooth(lms)
        return smoothed, False

    def get_fps(self):
        curr = time.time()
        dt = curr - self._last_time
        self._last_time = curr
        self._fps_history.append(1.0 / dt if dt > 0 else 0)
        if len(self._fps_history) > 30: self._fps_history.pop(0)
        return sum(self._fps_history) / len(self._fps_history)

    # ── DUAL-HAND API ─────────────────────────────────────────────────────────
    def get_all_hands(self, frame, w, h):
        """
        Track EVERY hand the AI sees (up to 2) independently.
        Returns a dict:  { "Left": (smoothed_lms, is_ghost),
                           "Right": (smoothed_lms, is_ghost) }
        Each hand has its own Kalman smoother, ghost engine, and jump guard
        stored in self._per_hand[label].
        """
        if not hasattr(self, '_per_hand'):
            self._per_hand = {}   # id -> {smoother, ghost, last_tip, label}

        results = {}
        seen_ids = set()

        timestamp_ms = int(time.time() * 1000)
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        self.detector.detect_async(mp_image, timestamp_ms)


        # ── Update from live AI data ──────────────────────────────────────────
        # MediaPipe handedness labels flip rapidly. We need spatial tracking to maintain hand identity.

        # 1. Match current detections to existing tracked hands based on distance
        unmatched_detections = self._hand_data.copy()

        for tracked_id, state in self._per_hand.items():
            if not unmatched_detections:
                 break

            best_match_idx = -1
            min_dist = float('inf')

            for i, det in enumerate(unmatched_detections):
                tip = np.array(det["landmarks"][8][:2])
                if state["last_tip"] is not None:
                     dist = np.linalg.norm(tip - state["last_tip"])
                     if dist < min_dist and dist < self._MAX_JUMP:
                         min_dist = dist
                         best_match_idx = i

            if best_match_idx != -1:
                # Match found!
                det = unmatched_detections.pop(best_match_idx)
                lms = det["landmarks"]
                tip = np.array(lms[8][:2])

                seen_ids.add(tracked_id)
                state["last_tip"] = tip
                state["lost"] = 0
                state["label"] = det["handedness"] # update label just for UI

                pixel_lm = [(lm[0] * w, lm[1] * h) for lm in lms]
                state["ghost"].update_real_data(frame, pixel_lm)

                smoothed = state["smoother"].smooth(lms)
                results[tracked_id] = (smoothed, False)

        # 2. Add new hands for any unmatched detections
        for det in unmatched_detections:
            # generate a new ID, e.g., "Hand_1", "Hand_2"
            new_id = f"Hand_{int(time.time()*1000)}_{len(self._per_hand)}"
            lms = det["landmarks"]
            tip = np.array(lms[8][:2])

            self._per_hand[new_id] = {
                "smoother": LandmarkSmoother(),
                "ghost": GhostHand(max_ghost_frames=20),
                "last_tip": tip,
                "lost": 0,
                "label": det["handedness"]
            }
            seen_ids.add(new_id)

            state = self._per_hand[new_id]
            pixel_lm = [(lm[0] * w, lm[1] * h) for lm in lms]
            state["ghost"].update_real_data(frame, pixel_lm)

            smoothed = state["smoother"].smooth(lms)
            results[new_id] = (smoothed, False)

        # ── Ghost fallback for hands that disappeared this frame ──────────────
        # We need a list to allow deletion from dictionary during iteration
        ids_to_remove = []
        for tracked_id, state in self._per_hand.items():
            if tracked_id not in seen_ids:
                state["lost"] += 1
                if state["lost"] < self._MAX_IDENTITY_LOST:
                    ghost_lms = state["ghost"].predict(frame)
                    if ghost_lms is not None:
                        # Convert pixels -> normalized
                        norm_ghost = [(p[0]/w, p[1]/h, 0.0) for p in ghost_lms]
                        smoothed = state["smoother"].smooth(norm_ghost)
                        results[tracked_id] = (smoothed, True)
                    else:
                        ids_to_remove.append(tracked_id)
                else:
                    ids_to_remove.append(tracked_id)

        for tracked_id in ids_to_remove:
            del self._per_hand[tracked_id]

        return results

if __name__ == "__main__":
    import cv2
    from backend.core.drawing_engine import DrawingEngine
    from backend.core.gesture_state import GestureState
    import urllib.request
    import os

    # Download model if not exists
    if not os.path.exists("hand_landmarker.task"):
        print("Downloading MediaPipe hand landmarker model...")
        urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", "hand_landmarker.task")
        print("Downloaded!")

    # --- Setup ---
    cap = cv2.VideoCapture(0)
    tracker = UltimateHandTracker(model_path="hand_landmarker.task")
    canvas = DrawingEngine(1280, 720)
    gesture_states = {} # tracked_id -> GestureState

    print("Initializing Ultimate Vision Engine...")

    # ── Visual identity per hand ──────────────────────────────────────────────
    # We now assign colours dynamically as the IDs are auto-generated
    import random
    hand_colors = {}

    # 1. Zero-latency camera
    class CameraStream:
        def __init__(self):
            self.stream = cv2.VideoCapture(0)
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.frame = None
            self.stopped = False
        def start(self):
            Thread(target=self.update, args=()).start()
            return self
        def update(self):
            while not self.stopped:
                _, self.frame = self.stream.read()
        def read(self):
            if self.frame is not None:
                return cv2.flip(self.frame, 1)
            return self.frame
        def stop(self):
            self.stopped = True

    cam = CameraStream().start()

    while True:
        frame = cam.read()
        if frame is None: continue
        
        h, w = frame.shape[:2]
        
        # Get data for ALL hands
        all_hands = tracker.get_all_hands(frame, w, h)
        
        # Process each hand for gestures and drawing
        for tracked_id, (landmarks, is_ghost) in all_hands.items():
            if tracked_id not in gesture_states:
                gesture_states[tracked_id] = GestureState()
            
            if tracked_id not in hand_colors:
                 hand_colors[tracked_id] = (random.randint(50,255), random.randint(50,255), random.randint(50,255))

            # 1. Get State
            state = gesture_states[tracked_id].get_state(landmarks)
            
            # 2. Update Canvas
            # We use pinch midpoint for drawing: midpoint of Thumb (4) and Index (8)
            thumb_tip = np.array(landmarks[4][:2])
            index_tip = np.array(landmarks[8][:2])
            midpoint = (thumb_tip + index_tip) / 2.0

            canvas.update(state, tuple(midpoint), hand_id=tracked_id)

            # 3. HUD Overlay (Dots)
            color = hand_colors[tracked_id]
            for i, lm in enumerate(landmarks):
                px = int(lm[0] * w)
                py = int(lm[1] * h)
                
                # Ghost hands are drawn with transparency
                alpha = 0.4 if is_ghost else 1.0
                cv2.circle(frame, (px, py), 4, color, -1)
                
            # Add Label
            tx = int(landmarks[0][0] * w)
            ty = int(landmarks[0][1] * h) - 20
            ui_label = tracker._per_hand[tracked_id]["label"] if tracked_id in tracker._per_hand else "Unknown"
            cv2.putText(frame, f"{ui_label} ({tracked_id[:8]}) {'(GHOST)' if is_ghost else ''}", (tx, ty),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Composite Canvas
        final_frame = canvas.render(frame)
        
        # System HUD
        cv2.putText(final_frame, f"ENGINE FPS: {int(tracker.get_fps())}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Phantom Hand - Vision Engine v2.1", final_frame)
        
        key = cv2.waitKey(1)
        if key == ord('q'): break
        if key == ord('c'): canvas.clear()
        if key == ord('z'): canvas.undo()

    cam.stop()
    cv2.destroyAllWindows()
