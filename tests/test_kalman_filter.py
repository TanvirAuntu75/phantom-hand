import pytest
import numpy as np

def test_smoother_reduces_variance(smoother, dummy_landmarks):
    """Test that smoother reduces jitter: output variance < input variance"""
    num_frames = 50
    base_pos = np.array(dummy_landmarks)

    noisy_inputs = []
    smoothed_outputs = []

    # Inject 5% random noise
    for _ in range(num_frames):
        noise = np.random.normal(0, 0.01, size=(21, 3))
        frame_in = base_pos + noise
        noisy_inputs.append(frame_in)
        smoothed_outputs.append(smoother.smooth(frame_in.tolist()))

    in_var = np.var(np.array(noisy_inputs), axis=0).mean()
    out_var = np.var(np.array(smoothed_outputs), axis=0).mean()

    # Variance of smoothed output should be significantly lower than noisy input
    assert out_var < in_var
    assert out_var < (in_var * 0.5)

def test_smoother_reset(smoother, dummy_landmarks):
    """Test reset() properly initializes fresh state"""
    smoother.smooth(dummy_landmarks)
    assert smoother.state is not None

    smoother.reset()
    assert smoother.state is None

def test_smoother_convergence(smoother):
    """Test convergence: after 30 frames of stable input, output must match input within 2%"""
    stable_input = [(0.7, 0.3, 0.1) for _ in range(21)]

    # Start with wildly different state to force convergence test
    smoother.smooth([(0.1, 0.9, 0.5) for _ in range(21)])

    for _ in range(30):
        out = smoother.smooth(stable_input)

    diff = np.abs(np.array(out) - np.array(stable_input)).max()
    assert diff < 0.02 # Less than 2% deviation
