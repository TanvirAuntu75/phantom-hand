# AGENTS.md — PHANTOM HAND Project Context

## What This Project Is
A zero-keyboard, real-time hand gesture drawing and control system.
The user controls everything through webcam-captured hand gestures.
No mouse. No keyboard. Hands only.

## Codename
PHANTOM HAND

## Aesthetic Requirement
Every file, UI element, variable name, comment, and output must feel
cold, clinical, and machine-made. No generic names. No Bootstrap.
No placeholder UI. The visual language is: dark backgrounds, cyan
accent (#00E5FF), monospace fonts, corner brackets, scan lines.
Think Iron Man's JARVIS HUD, not a tutorial project.

## Existing Core Files (DO NOT REWRITE THESE)
- backend/core/hand_tracker.py     — MediaPipe hand tracking engine
- backend/core/gesture_engine.py   — 20-gesture recognition system
- backend/core/drawing_engine.py   — Canvas with 6 brush modes + layers
- backend/core/shape_recognizer.py — 20+ shape detection
- backend/core/kalman_filter.py    — Kalman + 1-Euro hybrid smoother
- backend/core/ghost_engine.py     — Optical flow fallback tracker

## Tech Stack (NON-NEGOTIABLE — all free)
- Python 3.11+
- FastAPI + Uvicorn (backend server)
- Socket.IO (real-time WebSocket)
- OpenCV + MediaPipe (vision)
- React 18 + Vite (frontend)
- Tailwind CSS (styling only — no component libraries)
- Three.js (3D mode)
- Docker (deployment)

## Code Standards
- Python: fully typed with type hints, docstrings on every class and method
- React: functional components only, hooks only, no class components
- All errors logged to phantom_hand.log with timestamp + context
- Zero hardcoded paths — everything via config.py or environment variables
- Every module must be independently testable (no circular imports)
- Performance target: 30+ FPS on standard laptop CPU

## File Structure
phantom-hand/
├── backend/
│   ├── app.py
│   ├── core/          ← existing files live here
│   ├── ai/
│   ├── utils/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── App.jsx
│   └── package.json
├── tests/
├── docker/
└── AGENTS.md

## What Jules Must Never Do
- Never use any UI component library (no shadcn, no MUI, no Ant Design)
- Never use SQLite or any database — state lives in memory and files only
- Never add authentication — this is a local tool
- Never rename existing core files
- Never add print() statements — use the logger
- Never use synchronous blocking calls in the FastAPI server
