from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os
import asyncio
import base64
import cv2
import numpy as np
from datetime import datetime
from aiortc import RTCPeerConnection, RTCSessionDescription

from api.engine import WorkoutEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = WorkoutEngine()


def env_flag(name: str, default: str = "1") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


SEND_WS_FRAMES = env_flag("SEND_WS_FRAMES", "1")
USE_BACKEND_CAMERA = env_flag("USE_BACKEND_CAMERA", "1")
pcs = set()


class RTCOffer(BaseModel):
    sdp: str
    type: str

PLAYER_FILE = "src/data/players.json"

# Ensure file exists
os.makedirs("src/data", exist_ok=True)
if not os.path.exists(PLAYER_FILE):
    with open(PLAYER_FILE, "w") as f:
        json.dump({}, f)


def load_players():
    try:
        with open(PLAYER_FILE, "r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def save_players(data):
    with open(PLAYER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def default_player():
    return {
        "xp": 0,
        "level": 1,
        "badges": [],
        "history": []
    }


def ensure_player(players, name):
    created = name not in players
    if created:
        players[name] = default_player()
    return players[name], created


@app.get("/")
def root():
    return {"message": "AI Gym Trainer API running"}


@app.post("/start")
def start_workout(exercise: str = "Squat", name: str = "You"):
    selected_exercise = engine.set_exercise(exercise)
    engine.start(use_camera=USE_BACKEND_CAMERA, render_frames=SEND_WS_FRAMES)
    return {"status": "started", "exercise": selected_exercise}


@app.post("/stop")
def stop_workout(name: str = "You"):
    engine.stop()

    players = load_players()
    player, _ = ensure_player(players, name)

    # ✅ Append session history
    player["history"].append({
        "date": datetime.now().isoformat(),
        "reps": engine.state["reps"],
        "exercise": engine.state["exercise"]
    })

    # ✅ Update XP + Level
    player["xp"] = engine.player.xp
    player["level"] = engine.player.level

    # ✅ Merge badges instead of overwrite
    existing = set(player.get("badges", []))
    new = set(engine.unlocked_badges)
    player["badges"] = list(existing.union(new))

    save_players(players)

    # ✅ Keep player_profile.json in sync so XP survives server restarts
    engine.player.save()

    return {"status": "stopped"}


@app.get("/state")
def get_state():
    return engine.get_state()


@app.post("/webrtc/offer")
async def webrtc_offer(offer: RTCOffer):
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        if pc.connectionState in {"failed", "closed", "disconnected"}:
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        if track.kind != "video":
            return

        async def consume_video():
            while True:
                try:
                    frame = await track.recv()
                    # If processing is behind, drop stale frames before expensive conversion.
                    if engine.has_pending_external_frame():
                        continue
                    image = frame.to_ndarray(format="bgr24")
                    engine.ingest_external_frame(image)
                except Exception:
                    break

        asyncio.create_task(consume_video())

    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer.sdp, type=offer.type))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
    }


@app.on_event("shutdown")
async def on_shutdown():
    if pcs:
        await asyncio.gather(*[pc.close() for pc in list(pcs)], return_exceptions=True)
    pcs.clear()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    loop = asyncio.get_running_loop()

    try:
        while True:
            # Wait for a new frame without blocking the async event loop
            await loop.run_in_executor(None, lambda: engine._frame_event.wait(timeout=0.1))
            engine._frame_event.clear()

            raw_frame = engine.raw_frame

            if not engine.running or raw_frame is None:
                frame_b64 = None
                if SEND_WS_FRAMES:
                    blank = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(blank, "Camera Stopped", (150, 240),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    _, buffer = cv2.imencode('.jpg', blank, encode_params)
                    frame_b64 = base64.b64encode(buffer).decode('utf-8')
                await websocket.send_text(json.dumps({
                    "frame": frame_b64,
                    "landmarks": []
                }))
                await asyncio.sleep(0.1)
                continue

            frame_b64 = None
            if SEND_WS_FRAMES:
                _, buffer = cv2.imencode('.jpg', raw_frame, encode_params)
                frame_b64 = base64.b64encode(buffer).decode('utf-8')

            with engine._state_lock:
                state_snapshot = engine.state.copy()
                # Clear badges after reading so they only fire once
                new_badges = list(engine.recent_badges)
                engine.recent_badges = []
                engine.state["badges"] = []

            state_snapshot["badges"] = new_badges

            payload = json.dumps({
                "frame": frame_b64,
                "landmarks": engine.display_landmarks,
                **state_snapshot
            })
            await websocket.send_text(payload)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(
        engine.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/leaderboard")
def get_leaderboard():
    players = load_players()

    leaderboard = sorted(
        [{"name": k, "xp": v["xp"]} for k, v in players.items()],
        key=lambda x: x["xp"],
        reverse=True
    )[:10]

    return leaderboard


@app.get("/history")
def get_history(name: str):
    players = load_players()
    return players.get(name, {}).get("history", [])

@app.post("/login")
def login(name: str):
    players = load_players()

    player, created = ensure_player(players, name)
    if created:
        save_players(players)

    # ✅ Restore player XP/level into engine so state polling reflects correct values
    engine.player.name = name
    engine.player.xp = player["xp"]
    engine.player.level = player["level"]
    with engine._state_lock:
        engine.state["xp"] = engine.player.xp
        engine.state["level"] = engine.player.level
        engine.state["xp_required"] = engine.level_system.xp_needed(engine.player.level)

    return {
        "name": name,
        "xp": player["xp"],
        "level": player["level"]
    }