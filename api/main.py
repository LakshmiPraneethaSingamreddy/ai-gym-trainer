from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json
import os
import asyncio
import base64
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from aiortc import RTCPeerConnection, RTCSessionDescription

from api.db import Base, SessionLocal, get_db
from api.db import engine as db_engine
from api.db_models import User
from api.engine import WorkoutEngine
from api.user_store import (
    add_badges,
    add_history_item,
    create_user_if_missing,
    get_leaderboard_payload,
    get_user_by_name,
    get_user_history_payload,
    import_legacy_json_if_empty,
    list_users_payload,
    normalize_name,
    set_user_badges,
    update_user,
    user_to_dict,
)

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
USE_BACKEND_CAMERA = env_flag("USE_BACKEND_CAMERA", "0")
pcs = set()


class RTCOffer(BaseModel):
    sdp: str
    type: str

LEGACY_PLAYER_FILE = Path(__file__).resolve().parent.parent / "src" / "data" / "players.json"
PLAYER_FILE = LEGACY_PLAYER_FILE


class SessionHistoryItem(BaseModel):
    date: str
    reps: int
    exercise: str


class UserData(BaseModel):
    xp: int = 0
    level: int = 1
    badges: list[str] = Field(default_factory=list)
    history: list[SessionHistoryItem] = Field(default_factory=list)


class UserPatch(BaseModel):
    xp: Optional[int] = None
    level: Optional[int] = None
    badges: Optional[list[str]] = None
    history: Optional[list[SessionHistoryItem]] = None


def validate_user_numbers(xp: Optional[int] = None, level: Optional[int] = None) -> None:
    if xp is not None and xp < 0:
        raise HTTPException(status_code=400, detail="XP must be 0 or greater")
    if level is not None and level < 1:
        raise HTTPException(status_code=400, detail="Level must be 1 or greater")


def parse_history_date(raw_date: str) -> datetime | None:
    if not raw_date:
        return None
    try:
        return datetime.fromisoformat(raw_date)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid history date format: {raw_date}. Use ISO format.",
        ) from exc


def sync_engine_player(user: User) -> None:
    engine.player.name = user.name
    engine.player.xp = int(user.xp or 0)
    engine.player.level = int(user.level or 1)
    engine.player.badges = sorted([badge.badge_name for badge in user.badges])

    with engine._state_lock:
        engine.state["xp"] = engine.player.xp
        engine.state["level"] = engine.player.level
        engine.state["xp_required"] = engine.level_system.xp_needed(engine.player.level)


def default_player():
    return {"xp": 0, "level": 1, "badges": [], "history": []}


def load_players() -> dict:
    player_file = Path(PLAYER_FILE)
    if not player_file.exists():
        return {}

    try:
        with open(player_file, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}

    return raw if isinstance(raw, dict) else {}


def save_players(players: dict) -> None:
    player_file = Path(PLAYER_FILE)
    player_file.parent.mkdir(parents=True, exist_ok=True)
    with open(player_file, "w", encoding="utf-8") as handle:
        json.dump(players, handle, indent=2)


def ensure_player(players: dict, name: str):
    clean_name = str(name).strip()
    if clean_name not in players:
        players[clean_name] = default_player()
        return players[clean_name], True
    return players[clean_name], False


@app.on_event("startup")
def startup_database() -> None:
    Base.metadata.create_all(bind=db_engine)
    with SessionLocal() as db:
        imported = import_legacy_json_if_empty(db, LEGACY_PLAYER_FILE)
        if imported:
            db.commit()


@app.get("/")
def root():
    return {"message": "AI Gym Trainer API running"}


@app.post("/start")
def start_workout(exercise: str = "Squat", name: str = "You", use_backend_camera: Optional[bool] = None):
    selected_exercise = engine.set_exercise(exercise)
    camera_mode = USE_BACKEND_CAMERA if use_backend_camera is None else use_backend_camera
    engine.start(use_camera=camera_mode, render_frames=SEND_WS_FRAMES)
    return {"status": "started", "exercise": selected_exercise}


@app.post("/stop")
def stop_workout(name: str = "You", db: Session = Depends(get_db)):
    engine.stop()

    try:
        clean_name = normalize_name(name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user = create_user_if_missing(db, clean_name)

    add_history_item(
        db,
        user,
        reps=engine.state["reps"],
        exercise=engine.state["exercise"],
        when=datetime.utcnow(),
    )

    update_user(db, user, xp=engine.player.xp, level=engine.player.level)
    add_badges(db, user, list(engine.unlocked_badges))
    db.commit()
    db.refresh(user)
    sync_engine_player(user)

    players = load_players()
    player, _ = ensure_player(players, user.name)
    player["xp"] = int(user.xp or 0)
    player["level"] = int(user.level or 1)
    player.setdefault("badges", [])
    player["badges"] = sorted(set(player["badges"]) | set(engine.unlocked_badges))
    player.setdefault("history", [])
    player["history"].append(
        {
            "date": datetime.utcnow().isoformat(),
            "reps": engine.state["reps"],
            "exercise": engine.state["exercise"],
        }
    )
    save_players(players)

    # Keep runtime badge cache aligned with persisted badge rows.
    engine.unlocked_badges = {badge.badge_name for badge in user.badges}

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
                    # Drop stale frames when processing falls behind.
                    has_pending_frame = engine.has_pending_external_frame()
                    if has_pending_frame:
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
            await loop.run_in_executor(
                None, lambda: engine._frame_event.wait(timeout=0.1)
            )
            engine._frame_event.clear()

            raw_frame = engine.raw_frame

            if not engine.running or raw_frame is None:
                frame_b64 = None
                if SEND_WS_FRAMES:
                    blank = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(
                        blank,
                        "Camera Stopped",
                        (150, 240),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2,
                    )
                    _, buffer = cv2.imencode(".jpg", blank, encode_params)
                    frame_b64 = base64.b64encode(buffer).decode("utf-8")
                await websocket.send_text(
                    json.dumps({"frame": frame_b64, "landmarks": []})
                )
                await asyncio.sleep(0.1)
                continue

            frame_b64 = None
            if SEND_WS_FRAMES:
                _, buffer = cv2.imencode(".jpg", raw_frame, encode_params)
                frame_b64 = base64.b64encode(buffer).decode("utf-8")

            with engine._state_lock:
                state_snapshot = engine.state.copy()
                # Clear badges after reading so they only fire once
                new_badges = list(engine.recent_badges)
                engine.recent_badges = []
                engine.state["badges"] = []

            state_snapshot["badges"] = new_badges

            payload = json.dumps(
                {
                    "frame": frame_b64,
                    "landmarks": engine.display_landmarks,
                    **state_snapshot,
                }
            )
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
        },
    )


@app.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    if Path(PLAYER_FILE) != LEGACY_PLAYER_FILE:
        players = load_players()
        if players:
            return sorted(
                [{"name": name, "xp": int(record.get("xp", 0) or 0)} for name, record in players.items()],
                key=lambda item: item["xp"],
                reverse=True,
            )[:10]

    leaderboard = get_leaderboard_payload(db, top_n=10)
    if leaderboard:
        return leaderboard

    players = load_players()
    return sorted(
        [{"name": name, "xp": int(record.get("xp", 0) or 0)} for name, record in players.items()],
        key=lambda item: item["xp"],
        reverse=True,
    )[:10]


@app.get("/history")
def get_history(name: str, db: Session = Depends(get_db)):
    try:
        return get_user_history_payload(db, name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/login")
def login(name: str, db: Session = Depends(get_db)):
    try:
        clean_name = normalize_name(name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user = create_user_if_missing(db, clean_name)
    db.commit()
    db.refresh(user)
    sync_engine_player(user)

    players = load_players()
    player, _ = ensure_player(players, user.name)
    player["xp"] = int(user.xp or 0)
    player["level"] = int(user.level or 1)
    player.setdefault("badges", [])
    player.setdefault("history", [])
    save_players(players)

    return {
        "name": user.name,
        "xp": int(user.xp or 0),
        "level": int(user.level or 1)
    }


@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return list_users_payload(db)


@app.get("/users/{name}")
def get_user(name: str, db: Session = Depends(get_db)):
    try:
        user = get_user_by_name(db, name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"name": user.name, **user_to_dict(user, include_history=True)}


@app.post("/users/{name}")
def create_user(name: str, data: Optional[UserData] = None, db: Session = Depends(get_db)):
    try:
        clean_name = normalize_name(name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    existing = get_user_by_name(db, clean_name)
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    user = create_user_if_missing(db, clean_name)
    if data is not None:
        validate_user_numbers(xp=data.xp, level=data.level)
        update_user(db, user, xp=data.xp, level=data.level)
        set_user_badges(db, user, data.badges)
        try:
            for item in data.history:
                parsed_date = parse_history_date(item.date)
                add_history_item(db, user, reps=item.reps, exercise=item.exercise, when=parsed_date)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.commit()
    db.refresh(user)
    return {"name": user.name, **user_to_dict(user, include_history=True)}


@app.put("/users/{name}")
def upsert_user(name: str, patch: UserPatch, db: Session = Depends(get_db)):
    try:
        clean_name = normalize_name(name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user = create_user_if_missing(db, clean_name)

    if patch.xp is not None or patch.level is not None:
        validate_user_numbers(xp=patch.xp, level=patch.level)
        update_user(db, user, xp=patch.xp, level=patch.level)

    if patch.badges is not None:
        set_user_badges(db, user, patch.badges)

    if patch.history is not None:
        for row in list(user.history):
            db.delete(row)

        try:
            for item in patch.history:
                parsed_date = parse_history_date(item.date)
                add_history_item(db, user, reps=item.reps, exercise=item.exercise, when=parsed_date)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.commit()
    db.refresh(user)
    return {"name": user.name, **user_to_dict(user, include_history=True)}


@app.delete("/users/{name}")
def delete_user(name: str, db: Session = Depends(get_db)):
    try:
        user = get_user_by_name(db, name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    deleted_name = user.name
    deleted_xp = int(user.xp or 0)
    db.delete(user)
    db.commit()

    return {
        "deleted": deleted_name,
        "xp": deleted_xp,
    }
