#!/bin/bash

# PHANTOM HAND Start Script (Linux/Mac)
echo "Initializing PHANTOM HAND..."

# 1. Check Python version
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "ERROR: Python 3.11+ is not installed."
    return 1
fi

PY_VER=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$PY_VER < 3.11" | bc -l) )); then
    echo "ERROR: Python 3.11+ is required. Found $PY_VER."
    return 1
fi

# 2. Check Node version
if ! command -v node &>/dev/null; then
    echo "ERROR: Node.js 18+ is not installed."
    return 1
fi

NODE_VER=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
if [ "$NODE_VER" -lt 18 ]; then
    echo "ERROR: Node.js 18+ is required. Found $NODE_VER."
    return 1
fi

# 3. Check MediaPipe model
if [ ! -f "backend/hand_landmarker.task" ]; then
    echo "Downloading MediaPipe model..."
    curl -L "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" -o "backend/hand_landmarker.task"
fi

# 4. Install dependencies silently
echo "Installing backend dependencies..."
cd backend || return 1
$PYTHON_CMD -m pip install -r requirements.txt > /dev/null 2>&1
cd ..

echo "Installing frontend dependencies..."
cd frontend || return 1
npm install > /dev/null 2>&1
cd ..

# 5. Start Backend
echo "Starting Backend Engine..."
cd backend || return 1
$PYTHON_CMD app.py &
BACKEND_PID=$!
cd ..

sleep 2

# 6. Start Frontend
echo "Starting Frontend Interface..."
cd frontend || return 1
npm run dev &
FRONTEND_PID=$!
cd ..

sleep 1

# 7. Open Browser
echo "Opening Interface..."
if command -v xdg-open &>/dev/null; then
    xdg-open "http://localhost:3000"
elif command -v open &>/dev/null; then
    open "http://localhost:3000"
fi

# 8. Wait for user termination
echo "PHANTOM HAND is running. Press Ctrl+C to stop."
trap 'echo "Shutting down..."; kill $BACKEND_PID; kill $FRONTEND_PID; return 0' INT
wait
