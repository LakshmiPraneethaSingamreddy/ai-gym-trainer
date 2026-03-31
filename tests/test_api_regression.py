import tempfile
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import api.main as main_module
from api.db import Base, get_db


def _build_test_client():
    tmp_dir = tempfile.TemporaryDirectory()
    db_path = Path(tmp_dir.name) / "test_ai_gym.db"
    database_url = f"sqlite:///{db_path}"
    test_engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    Base.metadata.create_all(bind=test_engine)

    original_engine = main_module.db_engine
    original_session_local = main_module.SessionLocal
    original_legacy_file = main_module.LEGACY_PLAYER_FILE

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    main_module.db_engine = test_engine
    main_module.SessionLocal = TestSessionLocal
    main_module.LEGACY_PLAYER_FILE = Path(tmp_dir.name) / "players-does-not-exist.json"
    main_module.app.dependency_overrides[get_db] = override_get_db

    client = TestClient(main_module.app)

    return client, tmp_dir, test_engine, original_engine, original_session_local, original_legacy_file


def _cleanup_test_client(tmp_dir, test_engine, original_engine, original_session_local, original_legacy_file):
    main_module.app.dependency_overrides.clear()
    main_module.db_engine = original_engine
    main_module.SessionLocal = original_session_local
    main_module.LEGACY_PLAYER_FILE = original_legacy_file
    test_engine.dispose()
    tmp_dir.cleanup()


def test_login_creates_user_and_returns_defaults():
    client, tmp_dir, test_engine, original_engine, original_session_local, original_legacy_file = _build_test_client()
    try:
        response = client.post("/login", params={"name": "demo-login-user"})
        assert response.status_code == 200

        payload = response.json()
        assert payload["name"] == "demo-login-user"
        assert payload["xp"] == 0
        assert payload["level"] == 1
    finally:
        _cleanup_test_client(tmp_dir, test_engine, original_engine, original_session_local, original_legacy_file)


def test_upsert_updates_xp_and_level():
    client, tmp_dir, test_engine, original_engine, original_session_local, original_legacy_file = _build_test_client()
    try:
        client.post("/login", params={"name": "demo-update-user"})

        response = client.put(
            "/users/demo-update-user",
            json={"xp": 125, "level": 3, "badges": ["starter"]},
        )
        assert response.status_code == 200

        payload = response.json()
        assert payload["name"] == "demo-update-user"
        assert payload["xp"] == 125
        assert payload["level"] == 3
        assert "starter" in payload["badges"]
    finally:
        _cleanup_test_client(tmp_dir, test_engine, original_engine, original_session_local, original_legacy_file)


def test_history_retrieval_returns_inserted_items():
    client, tmp_dir, test_engine, original_engine, original_session_local, original_legacy_file = _build_test_client()
    try:
        response = client.put(
            "/users/demo-history-user",
            json={
                "history": [
                    {"date": "2026-03-30T10:00:00", "reps": 12, "exercise": "Squat"},
                    {"date": "2026-03-30T11:00:00", "reps": 10, "exercise": "Push-Up"},
                ]
            },
        )
        assert response.status_code == 200

        history_response = client.get("/history", params={"name": "demo-history-user"})
        assert history_response.status_code == 200

        history = history_response.json()
        assert len(history) == 2
        assert history[0]["exercise"] == "Squat"
        assert history[1]["exercise"] == "Push-Up"
    finally:
        _cleanup_test_client(tmp_dir, test_engine, original_engine, original_session_local, original_legacy_file)
