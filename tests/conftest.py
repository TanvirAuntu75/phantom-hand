import pytest
import numpy as np

# Adjust python path to find backend modules
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.drawing_engine import DrawingEngine
from backend.core.shape_recognizer import ShapeRecognizer
from backend.core.kalman_filter import LandmarkSmoother

@pytest.fixture
def canvas():
    return DrawingEngine(1280, 720)

@pytest.fixture
def recognizer():
    return ShapeRecognizer()

@pytest.fixture
def smoother():
    return LandmarkSmoother()

@pytest.fixture
def dummy_landmarks():
    """Returns a realistic-looking array of 21 dummy landmarks (normalized 0-1)"""
    return [(0.5, 0.5, 0.0) for _ in range(21)]
