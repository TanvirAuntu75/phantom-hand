import pytest
from backend.core.command_router import CommandRouter

class MockGestureResult:
    def __init__(self, gesture):
        self.gesture = gesture

class MockVoiceController:
    def __init__(self):
        self.active = False
    def toggle(self):
        self.active = not self.active

def test_gesture_debouncing():
    """Test gesture debouncing logic inside the command router"""
    class MockCanvas:
        def __init__(self):
            self.undo_calls = 0
            self.clear_calls = 0
            self.mode_3d = False
        def undo(self):
            self.undo_calls += 1
        def clear(self):
            self.clear_calls += 1

    canvas = MockCanvas()
    router = CommandRouter(canvas, None)

    for _ in range(30):
        router.route("hand1", MockGestureResult("FIST_UNDO"), [[0,0,0]]*21)

    assert canvas.undo_calls == 1

    for _ in range(30):
        router.route("hand1", MockGestureResult("OPEN_CLEAR"), [[0,0,0]]*21)

    assert canvas.clear_calls == 1

def test_pinky_toggles_voice():
    """Test PINKY_ONLY gesture toggles voice controller via router"""
    class MockCanvas:
        pass

    voice_ctl = MockVoiceController()
    router = CommandRouter(MockCanvas(), None, voice_ctl)

    assert voice_ctl.active is False
    router.route("hand1", MockGestureResult("PINKY_VOICE"), [[0,0,0]]*21)
    assert voice_ctl.active is True
