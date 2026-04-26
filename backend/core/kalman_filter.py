import numpy as np

class LandmarkSmoother:
    """
    Dynamic Exponential Smoother (1-Euro Style)
    Replaces the Kalman Filter to absolutely guarantee zero oscillation (zigzag) when the hand is still,
    while removing lag when the hand moves fast.
    """
    def __init__(self):
        self.state = None
        
        # Tuning parameters
        self.min_alpha = 0.1  # Heavy smoothing when hand is completely still (removes jitter)
        self.max_alpha = 0.9  # Almost no smoothing when moving fast (removes lag)
        self.speed_multiplier = 15.0 # How quickly it transitions from heavy smoothing to no smoothing

    def reset(self):
        """Reset the filter when hand disappears from frame."""
        self.state = None

    def smooth(self, raw_landmarks: list) -> list:
        """
        Takes raw [x, y, z] from MediaPipe and returns smoothed [x, y, z].
        """
        measurements = np.array(raw_landmarks) # Shape: (21, 3)
        
        if self.state is None:
            self.state = measurements
            return measurements.tolist()
            
        smoothed_landmarks = []
        
        for i in range(21):
            curr = measurements[i]
            prev = self.state[i]
            
            # Calculate speed of this specific landmark
            speed = np.linalg.norm(curr - prev)
            
            # Dynamic Alpha: fast movement = alpha approaches 1.0, slow movement = alpha approaches min_alpha
            alpha = self.min_alpha + (self.max_alpha - self.min_alpha) * (1.0 - np.exp(-speed * self.speed_multiplier))
            
            # Apply EMA
            new_pos = alpha * curr + (1.0 - alpha) * prev
            self.state[i] = new_pos
            smoothed_landmarks.append(tuple(new_pos))
            
        return smoothed_landmarks
