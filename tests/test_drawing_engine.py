import pytest
import numpy as np

def test_draw_basic_stroke(canvas):
    """Test a basic stroke can be drawn and recorded."""
    hand_id = "test_hand"
    canvas.update("DRAW", (0.1, 0.1), hand_id)
    canvas.update("DRAW", (0.2, 0.2), hand_id)

    assert len(canvas.current_strokes[hand_id]) == 2

    # Finish stroke
    canvas.update("HOVER", None, hand_id)

    assert len(canvas._undo_stack) == 1
    assert len(canvas.raw_strokes_2d) == 1

def test_undo_redo_stack(canvas):
    """Test undo stack"""
    hand_id = "test_hand"

    # Draw 5 strokes
    for i in range(5):
        canvas.update("DRAW", (0.1, 0.1), hand_id)
        canvas.update("DRAW", (0.2, 0.2), hand_id)
        canvas.update("HOVER", None, hand_id)

    assert len(canvas._undo_stack) == 5
    assert len(canvas.raw_strokes_2d) == 5

    # Undo 3
    for _ in range(3):
        canvas.undo()

    assert len(canvas._undo_stack) == 2
    # raw_strokes_2d currently accumulates, undo logic is on _undo_stack

    # Engine doesn't natively have redo() implemented in stub, checking if it exists.
    if hasattr(canvas, "redo"):
        canvas.redo()
        assert len(canvas._undo_stack) == 3

def test_teleport_guard(canvas):
    """Test teleport guard prevents massive jumps > MAX_JUMP_PX"""
    hand_id = "test_hand"
    # Normal draw
    canvas.update("DRAW", (0.1, 0.1), hand_id)

    # Massive jump (e.g. tracking swapping hands)
    # MAX_JUMP is 250px on a 1280 canvas, meaning jump > 0.2 normalized
    canvas.update("DRAW", (0.9, 0.9), hand_id)

    # Should have triggered teleport guard, finished the old stroke, and started a new one
    assert len(canvas.current_strokes[hand_id]) == 1 # Only the new point
    assert len(canvas._undo_stack) == 0 # Because the old stroke only had 1 point, it isn't saved

def test_brush_properties(canvas):
    canvas.next_color()
    assert canvas.current_color is not None

    initial_thickness = canvas.thickness
    canvas.increase_size()
    assert canvas.thickness == initial_thickness + 2

    canvas.decrease_size()
    assert canvas.thickness == initial_thickness

def test_layer_switch(canvas):
    initial_layer = getattr(canvas, "active_layer", 1)
    canvas.next_layer()
    new_layer = getattr(canvas, "active_layer", 1)
    assert new_layer != initial_layer
