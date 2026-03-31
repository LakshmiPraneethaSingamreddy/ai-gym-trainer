# AI Gym Trainer

AI Gym Trainer is a full-stack fitness tracking app with live workout feedback, user progress, leaderboard ranking, and workout history.

This setup is optimized for small-scale production usage (around 20 to 100 users) with SQLite persistence.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite
- Frontend: React
- Realtime: WebSocket and WebRTC signaling

## Core Features

- Login or create user by username
- Track XP and level progression
- Store workout history per user
- Show leaderboard based on XP
- Basic validation and clear API error messages

## Local Development

### 1) Start Backend

```powershell
Set-Location "C:\Masters project\ai-gym-trainer"
& ".\.venv\Scripts\Activate.ps1"
python -m pip install -r requirements.txt
$env:USE_BACKEND_CAMERA="0"
$env:SEND_WS_FRAMES="0"
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend URL: `http://127.0.0.1:8000`

For mobile testing on the same Wi-Fi, open frontend using your laptop IP (example: `http://192.168.4.187:3000`).

### 2) Start Frontend

```powershell
Set-Location "C:\Masters project\ai-gym-trainer\ai-gym-frontend"
npm install
npm start
```

Frontend URL: `http://localhost:3000`

## API Quick Check

```powershell
$base='http://127.0.0.1:8000'

# Login/create user
Invoke-RestMethod -Uri "$base/login?name=Alex" -Method Post

# Update XP/level/badges
$body=@{xp=210;level=4;badges=@('starter','bronze')}|ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri "$base/users/Alex" -Method Put -ContentType 'application/json' -Body $body

# Get user history
Invoke-RestMethod -Uri "$base/history?name=Alex" -Method Get

# Leaderboard
Invoke-RestMethod -Uri "$base/leaderboard" -Method Get
```

## Automated Tests

```powershell
Set-Location "C:\Masters project\ai-gym-trainer"
& ".\.venv\Scripts\Activate.ps1"
python -m pytest tests/test_api_regression.py -q
```

## Deployment (Free Service)

This repository includes [render.yaml](render.yaml) to deploy both backend and frontend on Render.

### Render Deployment Steps

1. Push this repository to GitHub.
2. Go to Render and create a Blueprint deployment from the repo.
3. Render will detect [render.yaml](render.yaml) and provision:
- `ai-gym-trainer-api` (FastAPI service)
- `ai-gym-trainer-frontend` (static React site)
4. After backend URL is created, set `REACT_APP_API_BASE_URL` in the frontend service to your backend URL.
5. Redeploy the frontend service.

### Important Notes

- SQLite works for small-scale usage. On free hosting, disk persistence can be limited; use persistent disk add-on if available.
- Username-based flow is intentionally kept simple for this scale.
- For larger scale, move to PostgreSQL and token-based auth.
