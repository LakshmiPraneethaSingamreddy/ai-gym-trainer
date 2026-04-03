# AI Gym Trainer

AI Gym Trainer is a **full-stack AI fitness trainer** that delivers **real-time fitness coaching** with **live posture feedback**, **rep counting**, and **gamified progress tracking** using **computer vision**.

It turns a standard browser camera into an interactive workout assistant: the frontend streams video to the backend, and the app returns live state updates such as reps, feedback, **XP system** progress, levels, and badges.

## Demo

Project links:

- Live Demo: `https://...`
- Demo Video: `https://...`
- Screenshots/GIFs: 

## Features

- **Real-time workout tracking** directly from browser webcam input
- **Exercise form analysis** with exercise-specific movement-state detection
- **Rep counting** powered by state transitions instead of timer-based heuristics
- Live landmarks and **real-time posture correction** feedback cues
- **Gamification** with **XP system**, levels, badges, and a competitive **leaderboard**
- Persistent user history and profile progression across sessions

## Tech Stack

### Frontend
- **React** (Create React App)
- JavaScript
- **WebRTC** and **WebSocket**

### Backend
- **FastAPI**
- Uvicorn
- aiortc

### Computer Vision
- **OpenCV**
- **MediaPipe**
- NumPy

### Storage
- SQLite (via SQLAlchemy)
- Legacy JSON files for compatibility/migration

### Tooling
- pytest
- black
- flake8

## Architecture Overview

1. Browser captures video.
2. Video is streamed to the backend via WebRTC.
3. Backend runs **pose estimation** and exercise logic.
4. Backend sends live state updates through WebSocket.
5. Frontend updates workout UI in near real-time.

This separates capture, processing, and rendering, which keeps the system modular and easier to optimize.

## API Overview

### Session and streaming

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/start` | POST | Start workout session |
| `/stop` | POST | Stop workout and persist session progress |
| `/state` | GET | Get current workout state |
| `/webrtc/offer` | POST | WebRTC SDP offer/answer negotiation |
| `/ws` | WS | Real-time state stream (and optional frames) |
| `/video_feed` | GET | MJPEG stream for backend camera mode |

### User and leaderboard

| Endpoint | Method | Description |
|---|---|---|
| `/leaderboard` | GET | Top users by XP |
| `/history?name=<user>` | GET | Workout history for a user |
| `/signup` `/signin` `/login` | POST | Create or fetch user |
| `/signout` `/logout` | POST | Sign out user (persists active session if running) |
| `/users` | GET | List users |
| `/users/{name}` | GET | Get user details |
| `/users/{name}` | POST | Create user with optional payload |
| `/users/{name}` | PUT | Upsert user fields |
| `/users/{name}` | DELETE | Delete user |

## Project Structure

- `api/`: FastAPI app, database integration, workout API
- `src/`: Core exercise logic, CV helpers, gamification systems
- `ai-gym-frontend/`: React client app
- `tests/`: Backend and integration tests
- `data/`: Recorded landmark CSV files for analysis/training data

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

Default local URLs:

- Frontend: http://localhost:3000
- Backend: http://127.0.0.1:8000

## Environment Variables

### Frontend

- `REACT_APP_API_BASE_URL`: Backend base URL (default: `http://127.0.0.1:8000`)

### Backend

- `USE_BACKEND_CAMERA`: Use server-side camera capture (`0` or `1`, default `0`)
- `SEND_WS_FRAMES`: Include JPEG frames in WebSocket payload (`0` or `1`, default `1`)

Recommended production values:

- `USE_BACKEND_CAMERA=0`
- `SEND_WS_FRAMES=0`

## Docker (Backend)

```bash
docker build -t ai-gym-backend .
docker run --rm -p 8000:8000 -e USE_BACKEND_CAMERA=0 -e SEND_WS_FRAMES=0 ai-gym-backend
```

## Future Enhancements

- Advanced form scoring with richer movement quality metrics
- Personalized coaching plans and adaptive difficulty progression
- Expanded exercise library with guided multi-exercise workout flows
- Social features such as challenges, streaks, and friend leaderboards
- Stronger production readiness with CI/CD and enhanced observability

