import cv2
import mediapipe as mp
import numpy as np
import time
import logging
from threading import Thread, Lock
from typing import Dict, List, Optional, Tuple, Set

# --- Mediapipe Components ---
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- Local Engine Components ---
from core.kalman_filter import LandmarkSmoother
from core.ghost_engine import GhostHand

# --- Configuration & Logger ---
logger = logging.getLogger("phantom_hand")

class HandIdentity:
    """
    NEURAL_IDENTITY_CONTAINER
    Maintains persistent state for a specific hand (Left/Right).
    """
    def __init__(self, label: str):
        self.label: str = label
        self.smoother: LandmarkSmoother = LandmarkSmoother()
        self.ghost: GhostHand = GhostHand(max_ghost_frames=15)
        self.last_normalized_tip: Optional[np.ndarray] = None
        self.signal_loss_frames: int = 0
        self.is_active: bool = False

    def reset(self) -> None:
        """System reset for specific identity."""
        self.smoother.reset()
        self.last_normalized_tip = None
        self.signal_loss_frames = 0
        self.is_active = False

class UltimateHandTracker:
    """
    VISION_PROCESSING_KERNEL
    The core engine for zero-latency hand landmarker detection and tracking.
    Integrates MediaPipe Tasks with custom Optical Flow fallbacks and Kalman filters.
    """
    
    def __init__(self, model_path: str = 'hand_landmarker.task'):
        # --- MediaPipe Initialisation ---
        try:
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.LIVE_STREAM,
                num_hands=2,
                min_hand_detection_confidence=0.75,
                min_hand_presence_confidence=0.75,
                min_tracking_confidence=0.75,
                result_callback=self._neural_callback
            )
            self.detector = vision.HandLandmarker.create_from_options(options)
            logger.info("NEURAL_ENGINE_READY: MediaPipe HandLandmarker initialised.")
        except Exception as e:
            logger.critical(f"NEURAL_ENGINE_FAILURE: Could not load model at {model_path}. Error: {e}")
            raise

        # --- State Management ---
        self._raw_neural_data: List[Dict] = []
        self._data_lock: Lock = Lock()
        
        # Identity Persistence
        self.identities: Dict[str, HandIdentity] = {
            "Left": HandIdentity("Left"),
            "Right": HandIdentity("Right")
        }
        
        # Constants for Identity Verification
        self._MAX_JUMP_THRESHOLD: float = 0.35  # Max normalised Euclidean distance per frame
        self._SIGNAL_LOSS_LIMIT: int = 15        # Frames to wait before identity purge
        
        # Telemetry
        self._fps_buffer: List[float] = []
        self._last_perf_check: float = time.time()

    def _neural_callback(self, result: vision.HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int) -> None:
        """
        NEURAL_INTERRUPT_HANDLER
        Executed by the MediaPipe worker thread upon landmark computation.
        """
        parsed_batch = []
        if result.hand_landmarks:
            for i, landmarks in enumerate(result.hand_landmarks):
                # MediaPipe handedness is relative to the camera
                label = result.handedness[i][0].category_name
                
                # Convert landmarks to NumPy for efficient downstream processing
                coords = np.array([(lm.x, lm.y, lm.z) for lm in landmarks], dtype=np.float32)
                
                parsed_batch.append({
                    "label": label,
                    "landmarks": coords,
                    "confidence": result.handedness[i][0].score
                })
        
        with self._data_lock:
            self._raw_neural_data = parsed_batch

    def process_frame(self, frame: np.ndarray) -> Dict[str, Tuple[List[Tuple[float, float, float]], bool]]:
        """
        PIPELINE_EXECUTION_LOOP
        Main entry point for tracking. Processes a single BGR frame.
        
        Returns:
            Dict mapping "Left"/"Right" to (smoothed_landmarks, is_ghost_flag).
        """
        h, w = frame.shape[:2]
        timestamp = int(time.time() * 1000)
        
        # 1. Dispatch to Neural Engine
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        self.detector.detect_async(mp_image, timestamp)
        
        # 2. Acquire thread-safe AI data
        with self._data_lock:
            current_neural_signals = self._raw_neural_data.copy()
            
        results: Dict[str, Tuple[List[Tuple[float, float, float]], bool]] = {}
        detected_this_frame: Set[str] = set()
        
        # 3. Synchronize Identities with Neural Signals
        for signal in current_neural_signals:
            label = signal["label"]
            lms = signal["landmarks"]
            tip = lms[8][:2] # Index finger tip
            
            identity = self.identities[label]
            
            # Spatial Identity Check (Jump Guard)
            if identity.last_normalized_tip is not None:
                dist = np.linalg.norm(tip - identity.last_normalized_tip)
                if dist > self._MAX_JUMP_THRESHOLD:
                    # Potential tracking swap artefact; ignore this signal
                    continue
            
            # Update Identity State
            identity.last_normalized_tip = tip
            identity.signal_loss_frames = 0
            identity.is_active = True
            detected_this_frame.add(label)
            
            # Feed Ghost Engine for future fallbacks
            pixel_lms = [(pt[0] * w, pt[1] * h) for pt in lms]
            identity.ghost.update_real_data(frame, pixel_lms)
            
            # Smooth and Record
            smoothed = identity.smoother.smooth(lms.tolist())
            results[label] = (smoothed, False)

        # 4. Handle Missing Signals via Ghost Engine Fallback
        for label, identity in self.identities.items():
            if label not in detected_this_frame:
                identity.signal_loss_frames += 1
                
                if identity.signal_loss_frames < self._SIGNAL_LOSS_LIMIT:
                    ghost_pixel_coords = identity.ghost.predict(frame)
                    if ghost_pixel_coords is not None:
                        # Normalise back for consistent output format
                        norm_ghost = [(pt[0]/w, pt[1]/h, 0.0) for pt in ghost_pixel_coords]
                        smoothed = identity.smoother.smooth(norm_ghost)
                        results[label] = (smoothed, True)
                else:
                    # Signal lost beyond recovery limit
                    if identity.is_active:
                        logger.info(f"SIGNAL_TERMINATED: {label} hand identity purged.")
                        identity.reset()
                        
        return results

    def get_fps(self) -> float:
        """
        Calculates moving average FPS for the vision pipeline.
        """
        now = time.time()
        delta = now - self._last_perf_check
        self._last_perf_check = now
        
        if delta > 0:
            self._fps_buffer.append(1.0 / delta)
        
        if len(self._fps_buffer) > 30:
            self._fps_buffer.pop(0)
            
        return sum(self._fps_buffer) / len(self._fps_buffer) if self._fps_buffer else 0.0

if __name__ == "__main__":
    # Self-test block
    logging.basicConfig(level=logging.INFO)
    cap = cv2.VideoCapture(0)
    tracker = UltimateHandTracker()
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        
        tracks = tracker.process_frame(frame)
        
        for label, (lms, ghost) in tracks.items():
            color = (0, 255, 255) if label == "Right" else (255, 0, 255)
            if ghost: color = (100, 100, 100)
            
            for pt in lms:
                cv2.circle(frame, (int(pt[0]*w), int(pt[1]*h)), 3, color, -1)
                
        cv2.putText(frame, f"FPS: {int(tracker.get_fps())}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("TEST_KERNEL", frame)
        
        if cv2.waitKey(1) == 27: break
        
    cap.release()
    cv2.destroyAllWindows()
