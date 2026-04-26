# Phantom Hand - Architecture & File Registry

This document serves as the master registry for all files in the Phantom Hand project, ensuring the AI agent and the developer know exactly where everything resides and what its purpose is.

## 📁 `backend/` - Python FastAPI Server
The core of Phantom Hand, handling computer vision, gesture recognition, AI integration, and the websocket server.

### 📂 `backend/core/` - Vision & Logic
- `hand_tracker.py`: Captures webcam feed (1280x720@30fps), uses MediaPipe to extract 21 3D landmarks for up to 2 hands. Outputs clean data.
- `kalman_filter.py`: Smooths the MediaPipe landmark coordinates using independent Kalman filters (x,y,z,vx,vy,vz) to remove camera jitter.
- `gesture_engine.py`: Takes smoothed landmarks and runs rule-based logic (and ML fallback) to classify exactly which of the 30 gestures is currently active. Manages gesture state machine.
- `drawing_engine.py`: The canvas. Manages layers (4K numpy arrays), processes strokes, handles undo/redo stacks, and composites the final frame with alpha blending over the camera feed.
- `brush_system.py`: Implements the 12 brush rendering modes (Pencil, Airbrush, Laser, etc.) using OpenCV and custom particle/bloom logic.
- `motion_smoother.py`: Smooths the raw path of the fingertip *before* sending to the drawing engine using Gaussian/Bezier interpolation. Changes smoothing based on movement velocity.
- `shape_recognizer.py`: Takes a completed stroke and tries to fit it to one of 25 geometric primitives using algorithms (Douglas-Peucker, convex hull).
- `letter_recognizer.py`: Evaluates a single continuous stroke drawn in air-write mode against a custom trained EMNIST CNN to predict the character.
- `command_router.py`: Central hub mapping detected gestures and voice commands to actual system state changes (changing modes, undoing, exporting).
- `layer_manager.py`: Controls layer stack, blend modes (Multiply, Screen, etc.), opacity, and reordering.

### 📂 `backend/ai/` - AI Capabilities
- `gemini_client.py`: The wrapper for the Gemini 3.1 Pro API. Sends images for drawing completion or text for autocorrect.
- `drawing_completer.py`: Uses Gemini Vision to analyze partial drawings and suggest completions or colors.
- `style_transfer.py`: Applies TensorFlow Hub Magenta models to drawings to apply artistic styles like watercolor or neon.
- `gesture_trainer.py`: A CLI utility that prompts the user to record gesture samples and trains a new TensorFlow Lite model.
- `token_manager.py`: (Currently simplified to 1 account as requested) Manages API keys and handles rate-limit backoff.

### 📂 `backend/utils/` - Helpers
- `voice_controller.py`: Listens via microphone using SpeechRecognition for voice fallback commands.
- `exporter.py`: Handles saving the canvas to PNG, SVG, PDF, MP4, WebP, JSON, and OBJ formats.
- `performance_monitor.py`: Tracks FPS, RAM, and latency, feeding data to the HUD.
- `camera_manager.py`: Manages webcam device selection and resolution config.
- `collaboration.py`: Room-based state management for multiplayer drawing over Socket.IO.

### 📂 `backend/models/` - Trained AI Models
- `gesture_classifier.tflite`: Local ML model for the 30 system gestures.
- `letter_recognition.h5 / .tflite`: EMNIST character recognition model.
- `shape_templates.pkl`: Stored templates for shape recognition matching.

### 📄 `backend/app.py`
The main FastAPI and Socket.IO server. Starts camera threads, processes the main pipeline frame-by-frame, and communicates with the frontend via websockets.

---

## 📁 `frontend/` - React User Interface (HUD)
The interface layer, built using React + TypeScript + Vite. It is a strictly "HUD" aesthetic—dark theme, cyan highlights, no rounded corners, monospace fonts.

### 📂 `frontend/src/components/` - UI Elements
- `HUDOverlay.jsx`: The main wrapper for all UI elements.
- `VideoFeed.jsx`: The background element showing the webcam + composited canvas.
- `DrawingCanvas.jsx`: For any browser-side rendering or interaction overlays.
- `GestureIndicator.jsx`: Live feedback showing what gesture is detected.
- `LayerPanel.jsx`: Visual control of the layer stack.
- `ColorOrb.jsx`: Gesture-controlled color wheel.
- `BrushSelector.jsx`: UI for the 12 brush modes.
- `AIPanel.jsx`: Shows text and drawing suggestions from Gemini.
- `VoiceWave.jsx`: Audio visualizer for voice commands.
- `ExportMenu.jsx`: File export controls.
- `CollaborationPanel.jsx`: Shows connected users and remote cursors.
- `PerformanceHUD.jsx`: Shows FPS, resolution, and latency.
- `HandSkeleton.jsx`: Visualizes the 21 MediaPipe points on screen.
- `ShapePreview.jsx`: Shows a faint "ghost" of the detected autocomplete shape.

### 📂 `frontend/src/hooks/` - Logic integration
- `useSocket.js`: Manages the Socket.IO connection to the backend.
- `useGesture.js`: Processes raw gesture events.
- `useDrawing.js`: State management for local drawing feedback.
- `useVoice.js`: Ties into browser audio or backend voice events.

### 📂 `frontend/src/three/` - 3D Engine
- `Scene3D.js`: Initializes a Three.js scene for the 3D drawing mode.
- `StrokeRenderer3D.js`: Converts stroke paths into volumetric ribbon meshes.
- `HandVisualizer3D.js`: Maps the 2D camera hand into a 3D avatar/point cloud.

---

## 📁 `tests/` - QA and Validation
- `tests/unit/`: Pytest tests for individual python functions.
- `tests/integration/`: Tests for websocket messaging and API endpoints.
- `tests/visual/`: Selenium tests for the HUD component rendering.

## 📁 `docker/` - Deployment
- `Dockerfile`: Multi-stage build for python + node.
- `docker-compose.yml`: For easy one-click local deployment.

## 📁 `docs/` - Project Documentation
- `GESTURE_REFERENCE.md`: The 30 gestures and how to do them.
- `API_DOCS.md`: Backend endpoints and socket events.
- `USER_GUIDE.md`: How to actually use Phantom Hand.
