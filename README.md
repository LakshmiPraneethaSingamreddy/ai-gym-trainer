# AI Gym Trainer

AI Gym Trainer is a **full-stack**, **real-time** fitness coaching application that delivers **live posture feedback**, **rep counting**, and **gamified progress tracking** using computer vision.

The app captures the user webcam stream in the browser, analyzes pose and movement in the backend, and continuously returns workout insights including **rep count**, **exercise state**, **form feedback**, **XP progression**, and **leaderboard updates**.

## Demo

Add your links here:
1. Live demo URL
2. Demo video URL
3. Screenshots or GIFs

## Product Story

AI Gym Trainer was built to make solo workouts feel guided and measurable. Instead of following static content, users interact with a **live coaching interface** that reacts to their movement in real time. The experience is designed around a continuous loop of **action**, **feedback**, and **progression** so users can improve technique while staying motivated through **levels**, **badges**, and **ranking**.

## How It Works

1. The browser captures video with user permission.
2. Video streaming is handled through **WebRTC** to the backend for low-latency ingestion.
3. The backend runs **pose estimation** and exercise state logic.
4. Workout state updates are returned over **WebSocket** for real-time UI updates.
5. The frontend renders **feedback**, **rep count**, **XP**, **level**, and **leaderboard** data.

## Key Functionalities

1. **Real-time** workout tracking through browser webcam input.
2. Exercise workflows for **Squat**, **Pushup**, **Lunge**, and **Plank**.
3. **Rep counting** using state-based exercise logic.
4. **Form feedback** and landmark visualization for posture correction.
5. **XP progression**, **level advancement**, **badge unlocks**, and **leaderboard ranking**.
6. Workout history and profile continuity across sessions.

## Technology Stack

### Frontend
**React (Create React App)**, **JavaScript**, **WebRTC**, **WebSocket**

### Backend

**FastAPI**, **Uvicorn**, **aiortc**

### Computer Vision

**OpenCV**, **MediaPipe**, **NumPy**

### Data Layer

**JSON persistence** for player and history state

### Quality and Tooling

**pytest**, **black**, **flake8**

## Project Structure

**api** contains FastAPI application and engine entrypoints. **src** contains core CV, exercise logic, session logic, and gamification modules. **ai-gym-frontend** contains the React client.

## Local Development

### Backend

```powershell
python -m venv .venv
& ".\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```powershell
Set-Location ai-gym-frontend
npm install
npm start
```

Default URLs:
1. Frontend: http://localhost:3000
2. Backend: http://localhost:8000

## Environment Variables

### Frontend

**REACT_APP_API_BASE_URL** defines the backend base URL. Default local value is **http://127.0.0.1:8000**.

### Backend

**USE_BACKEND_CAMERA** controls server-side webcam usage (0 off, 1 on). **SEND_WS_FRAMES** controls whether image frames are included in websocket payloads.

Recommended for production:
1. USE_BACKEND_CAMERA=0
2. SEND_WS_FRAMES=0

## Deployment Notes

The frontend uses the **end user browser camera**, not the server camera. Set **REACT_APP_API_BASE_URL** before frontend build. Persist **src/data/players.json** with a mounted volume or migrate to a managed database for reliable storage.

## Docker (Backend)

```powershell
docker build -t ai-gym-backend .
docker run --rm -p 8000:8000 -e USE_BACKEND_CAMERA=0 ai-gym-backend
```

## Known Limitations

1. Persistence currently relies on **JSON files** and is not ideal for multi-instance production.
2. **Authentication** and **authorization** are not yet implemented.
3. **CORS** is still broad and should be restricted by environment before public deployment.

## Roadmap

### Near-Term Priorities

1. Move persistence from JSON to SQLite or PostgreSQL.
2. Add environment-based CORS restrictions.
3. Add health and readiness endpoints.
4. Expand API and integration test coverage.
5. Add CI pipeline for lint, test, and build checks.

### Future Vision

1. Multi-exercise session plans.
2. Improved form scoring models.
3. Personalized coaching and adaptive plans.
4. Social features such as challenges and friend leaderboards.
