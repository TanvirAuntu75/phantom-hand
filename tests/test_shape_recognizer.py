import pytest
import numpy as np

def generate_line(start=(0.1, 0.1), end=(0.9, 0.9), points=30, noise=0.0):
    xs = np.linspace(start[0], end[0], points)
    ys = np.linspace(start[1], end[1], points)
    return [(x + np.random.normal(0, noise), y + np.random.normal(0, noise)) for x, y in zip(xs, ys)]

def generate_rectangle(w=0.4, h=0.2, center=(0.5, 0.5)):
    x1, x2 = center[0] - w/2, center[0] + w/2
    y1, y2 = center[1] - h/2, center[1] + h/2

    top = [(x, y1) for x in np.linspace(x1, x2, 10)]
    right = [(x2, y) for y in np.linspace(y1, y2, 10)]
    bottom = [(x, y2) for x in np.linspace(x2, x1, 10)]
    left = [(x1, y) for y in np.linspace(y2, y1, 10)]
    return top + right + bottom + left

def generate_triangle(base=0.4, height=0.4, center=(0.5, 0.5)):
    p1 = (center[0], center[1] - height/2)
    p2 = (center[0] - base/2, center[1] + height/2)
    p3 = (center[0] + base/2, center[1] + height/2)

    side1 = [(x, y) for x, y in zip(np.linspace(p1[0], p2[0], 10), np.linspace(p1[1], p2[1], 10))]
    side2 = [(x, y) for x, y in zip(np.linspace(p2[0], p3[0], 10), np.linspace(p2[1], p3[1], 10))]
    side3 = [(x, y) for x, y in zip(np.linspace(p3[0], p1[0], 10), np.linspace(p3[1], p1[1], 10))]
    return side1 + side2 + side3

def test_recognize_line(recognizer):
    stroke = generate_line(noise=0.01)
    result = recognizer.recognize_and_snap(stroke)
    assert result["shape"] == "LINE"

def test_recognize_rectangle(recognizer):
    stroke = generate_rectangle()
    result = recognizer.recognize_and_snap(stroke)
    assert result["shape"] == "RECTANGLE"

def test_recognize_triangle(recognizer):
    stroke = generate_triangle()
    result = recognizer.recognize_and_snap(stroke)
    assert result["shape"] == "TRIANGLE"

def test_fallback_freeform(recognizer):
    stroke = [(0.1, 0.1), (0.1, 0.12)]
    result = recognizer.recognize_and_snap(stroke)
    assert result["shape"] == "FREEFORM"
