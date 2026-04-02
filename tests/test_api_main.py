import json
import threading

from fastapi.testclient import TestClient

import api.main as main


class DummyPlayer:
    def __init__(self):
        self.name = "Player1"
        self.xp = 0
        self.level = 1

    def save(self):
        return None


class DummyLevelSystem:
    def xp_needed(self, level):
        return 500 * level


class DummyEngine:
    def __init__(self):
        self.running = False
        self.player = DummyPlayer()
        self.level_system = DummyLevelSystem()
        self._state_lock = threading.Lock()
        self.state = {
            "reps": 0,
            "xp": 0,
            "xp_required": 500,
            "level": 1,
            "feedback": "",
            "exercise": "Squat",
            "badges": [],
        }
        self.unlocked_badges = set()

    def set_exercise(self, exercise):
        self.state["exercise"] = exercise
        return exercise

    def start(self, use_camera=False, render_frames=False):
        return None

    def stop(self):
        return None

    def get_state(self):
        return self.state


class TestApiMainUnit:
    def test_ensure_player_creates_default_player(self):
        players = {}

        player, created = main.ensure_player(players, "Alice")

        assert created is True
        assert player["xp"] == 0
        assert player["level"] == 1
        assert "Alice" in players

    def test_env_flag_parses_truthy_and_falsy(self, monkeypatch):
        monkeypatch.setenv("FEATURE_X", "true")
        assert main.env_flag("FEATURE_X", "0") is True

        monkeypatch.setenv("FEATURE_X", "0")
        assert main.env_flag("FEATURE_X", "1") is False


class TestApiMainIntegration:
    def setup_method(self):
        self.client = TestClient(main.app)

    def _set_temp_player_file(self, tmp_path, monkeypatch):
        player_file = tmp_path / "players.json"
        player_file.write_text("{}", encoding="utf-8")
        monkeypatch.setattr(main, "PLAYER_FILE", str(player_file))
        monkeypatch.setattr(main, "engine", DummyEngine())
        return player_file

    def test_signin_creates_player_and_updates_engine_state(self, tmp_path, monkeypatch):
        player_file = self._set_temp_player_file(tmp_path, monkeypatch)

        response = self.client.post("/signin", params={"name": "Alice"})

        assert response.status_code == 200
        payload = response.json()
        assert payload == {"name": "Alice", "xp": 0, "level": 1}

        saved = json.loads(player_file.read_text(encoding="utf-8"))
        assert "Alice" in saved

    def test_leaderboard_returns_sorted_by_xp(self, tmp_path, monkeypatch):
        player_file = self._set_temp_player_file(tmp_path, monkeypatch)
        players = {
            "A": {"xp": 5, "level": 1, "badges": [], "history": []},
            "B": {"xp": 50, "level": 1, "badges": [], "history": []},
            "C": {"xp": 20, "level": 1, "badges": [], "history": []},
        }
        player_file.write_text(json.dumps(players), encoding="utf-8")

        response = self.client.get("/leaderboard")

        assert response.status_code == 200
        assert response.json() == [
            {"name": "B", "xp": 50},
            {"name": "C", "xp": 20},
            {"name": "A", "xp": 5},
        ]

    def test_stop_persists_history_and_progress(self, tmp_path, monkeypatch):
        player_file = self._set_temp_player_file(tmp_path, monkeypatch)
        engine = main.engine
        engine.state["reps"] = 12
        engine.state["exercise"] = "Low Plank"
        engine.player.xp = 77
        engine.player.level = 2
        engine.unlocked_badges = {"first_workout"}

        response = self.client.post("/stop", params={"name": "Nina"})

        assert response.status_code == 200
        assert response.json() == {"status": "stopped"}

        saved = json.loads(player_file.read_text(encoding="utf-8"))
        assert saved["Nina"]["xp"] == 77
        assert saved["Nina"]["level"] == 2
        assert "first_workout" in saved["Nina"]["badges"]
        assert len(saved["Nina"]["history"]) == 1
        assert saved["Nina"]["history"][0]["reps"] == 12
        assert saved["Nina"]["history"][0]["exercise"] == "Low Plank"

    def test_signout_returns_signed_out_without_active_workout(self, tmp_path, monkeypatch):
        self._set_temp_player_file(tmp_path, monkeypatch)

        response = self.client.post("/signout", params={"name": "Maya"})

        assert response.status_code == 200
        assert response.json() == {"status": "signed_out"}

    def test_signout_stops_active_workout_and_persists_progress(self, tmp_path, monkeypatch):
        player_file = self._set_temp_player_file(tmp_path, monkeypatch)
        engine = main.engine
        engine.running = True
        engine.state["reps"] = 9
        engine.state["exercise"] = "Squat"
        engine.player.xp = 42
        engine.player.level = 2

        response = self.client.post("/signout", params={"name": "Maya"})

        assert response.status_code == 200
        assert response.json() == {"status": "signed_out"}

        saved = json.loads(player_file.read_text(encoding="utf-8"))
        assert saved["Maya"]["xp"] == 42
        assert saved["Maya"]["level"] == 2
        assert len(saved["Maya"]["history"]) == 1
        assert saved["Maya"]["history"][0]["reps"] == 9
        assert saved["Maya"]["history"][0]["exercise"] == "Squat"
