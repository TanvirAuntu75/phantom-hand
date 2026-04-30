# PHANTOM HAND Start Script (Windows)
Write-Host "Initializing PHANTOM HAND..." -ForegroundColor Cyan

# 1. Check Python version
$pythonCmd = "python"
if (-Not (Get-Command $pythonCmd -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python is not installed or not in PATH." -ForegroundColor Red
    return
}

$pyVerStr = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
[decimal]$pyVer = $pyVerStr
if ($pyVer -lt 3.11) {
    Write-Host "ERROR: Python 3.11+ is required. Found $pyVer." -ForegroundColor Red
    return
}

# 2. Check Node version
if (-Not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js 18+ is not installed or not in PATH." -ForegroundColor Red
    return
}

$nodeVerStr = (node -v).TrimStart('v').Split('.')[0]
[int]$nodeVer = $nodeVerStr
if ($nodeVer -lt 18) {
    Write-Host "ERROR: Node.js 18+ is required. Found $nodeVer." -ForegroundColor Red
    return
}

# 3. Check MediaPipe model
if (-Not (Test-Path "backend\hand_landmarker.task")) {
    Write-Host "Downloading MediaPipe model..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" -OutFile "backend\hand_landmarker.task"
}

# 4. Install dependencies silently
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
Set-Location "backend"
& $pythonCmd -m pip install -r requirements.txt | Out-Null
Set-Location ".."

Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location "frontend"
& npm install | Out-Null
Set-Location ".."

# 5. Start Backend
Write-Host "Starting Backend Engine..." -ForegroundColor Cyan
Set-Location "backend"
$BackendProcess = Start-Process -FilePath $pythonCmd -ArgumentList "app.py" -WindowStyle Hidden -PassThru
Set-Location ".."

Start-Sleep -Seconds 2

# 6. Start Frontend
Write-Host "Starting Frontend Interface..." -ForegroundColor Cyan
Set-Location "frontend"
$FrontendProcess = Start-Process -FilePath "npm" -ArgumentList "run dev" -WindowStyle Hidden -PassThru
Set-Location ".."

Start-Sleep -Seconds 1

# 7. Open Browser
Write-Host "Opening Interface..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"

Write-Host "PHANTOM HAND is running. Close the background terminals to stop." -ForegroundColor Green
