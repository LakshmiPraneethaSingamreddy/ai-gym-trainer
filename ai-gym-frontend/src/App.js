import React, { useEffect, useRef, useState } from "react";
import "./App.css";
import Login from "./Login";

// MediaPipe skeleton connections (pairs of landmark indices)
const POSE_CONNECTIONS = [
  [0,1],[1,2],[2,3],[3,7],
  [0,4],[4,5],[5,6],[6,8],
  [9,10],[11,12],
  [11,13],[13,15],[15,17],[15,19],[15,21],[17,19],
  [12,14],[14,16],[16,18],[16,20],[16,22],[18,20],
  [11,23],[12,24],[23,24],
  [23,25],[25,27],[27,29],[27,31],[29,31],
  [24,26],[26,28],[28,30],[28,32],[30,32]
];

function App() {
  const [state, setState] = useState({
    reps: 0,
    xp: 0,
    xp_required: 100,
    level: 1,
    feedback: "",
    exercise: "",
    badges: []
  });

  const [username, setUsername] = useState(
    localStorage.getItem("username") || ""
  );

  const [showBadge, setShowBadge] = useState(null);
  const [badgeQueue, setBadgeQueue] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [history, setHistory] = useState([]); // ✅ NEW
  const [selectedExercise, setSelectedExercise] = useState("Squat");
  const [landmarks, setLandmarks] = useState([]);
  const [isWebRTCActive, setIsWebRTCActive] = useState(false);
  const [isWorkoutActive, setIsWorkoutActive] = useState(false);

  const canvasRef = useRef(null);
  const overlayCanvasRef = useRef(null);
  const localVideoRef = useRef(null);
  const localStreamRef = useRef(null);
  const pcRef = useRef(null);

  function drawSkeleton(ctx, landmarks, w, h) {
    if (!landmarks || landmarks.length === 0) return;
    ctx.strokeStyle = "#00ff88";
    ctx.lineWidth = 2;
    POSE_CONNECTIONS.forEach(([i, j]) => {
      const a = landmarks[i];
      const b = landmarks[j];
      if (a && b && a.visibility > 0.35 && b.visibility > 0.35) {
        ctx.beginPath();
        ctx.moveTo(a.x * w, a.y * h);
        ctx.lineTo(b.x * w, b.y * h);
        ctx.stroke();
      }
    });
    ctx.fillStyle = "#ff4444";
    landmarks.forEach(lm => {
      if (lm.visibility > 0.35) {
        ctx.beginPath();
        ctx.arc(lm.x * w, lm.y * h, 4, 0, 2 * Math.PI);
        ctx.fill();
      }
    });
  }

  // ✅ Save username
  useEffect(() => {
    if (username) {
      localStorage.setItem("username", username);
    }
  }, [username]);

  // ✅ Fetch leaderboard (every 5s)
  useEffect(() => {
    if (!username) return;

    const fetchLeaderboard = () => {
      fetch("http://127.0.0.1:8000/leaderboard")
        .then(res => res.json())
        .then(data => setLeaderboard(data))
        .catch(err => console.error("Leaderboard error:", err));
    };

    fetchLeaderboard();
    const interval = setInterval(fetchLeaderboard, 5000);

    return () => clearInterval(interval);
  }, [username]);

  // ✅ Fetch history (NEW)
  useEffect(() => {
    if (!username) return;

    fetch(`http://127.0.0.1:8000/history?name=${username}`)
      .then(res => res.json())
      .then(data => setHistory(data))
      .catch(err => console.error("History error:", err));
  }, [username]);

  const stopWebRTC = () => {
    setIsWebRTCActive(false);

    if (pcRef.current) {
      pcRef.current.close();
      pcRef.current = null;
    }

    const stream = localStreamRef.current;
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      localStreamRef.current = null;
    }

    if (localVideoRef.current) {
      localVideoRef.current.srcObject = null;
    }
  };

  const startWebRTC = async () => {
    stopWebRTC();

    const localStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480 },
      audio: false,
    });
    localStreamRef.current = localStream;

    const pc = new RTCPeerConnection();
    pcRef.current = pc;
    localStream.getTracks().forEach((track) => pc.addTrack(track, localStream));

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    const response = await fetch("http://127.0.0.1:8000/webrtc/offer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sdp: offer.sdp,
        type: offer.type,
      }),
    });

    if (!response.ok) {
      stopWebRTC();
      throw new Error("WebRTC signaling failed");
    }

    const answer = await response.json();
    await pc.setRemoteDescription(answer);
    setIsWebRTCActive(true);
  };

  useEffect(() => {
    return () => {
      stopWebRTC();
    };
  }, []);

  // WebSocket — replaces the 250ms polling interval
  // Receives video frame + landmarks + state in one message at ~30fps
  useEffect(() => {
    if (!username) return;

    const ws = new WebSocket("ws://127.0.0.1:8000/ws");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLandmarks(data.landmarks || []);

      // Update workout state
      if (data.reps !== undefined) {
        setState({
          reps: data.reps,
          xp: data.xp,
          xp_required: data.xp_required,
          level: data.level,
          feedback: data.feedback,
          exercise: data.exercise,
          badges: data.badges || []
        });

        if (data.badges?.length > 0) {
          setBadgeQueue(prev => {
            const newBadges = data.badges.filter(b => !prev.includes(b));
            return [...prev, ...newBadges];
          });
        }
      }

      // Draw frame + skeleton on canvas
      const canvas = canvasRef.current;
      if (!canvas || !data.frame || isWebRTCActive) return;
      const ctx = canvas.getContext("2d");
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        drawSkeleton(ctx, data.landmarks, canvas.width, canvas.height);
      };
      img.src = "data:image/jpeg;base64," + data.frame;
    };

    ws.onerror = (err) => console.error("WebSocket error:", err);

    return () => ws.close();
  }, [username, isWebRTCActive]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!isWebRTCActive) return;

    const video = localVideoRef.current;
    const stream = localStreamRef.current;
    if (!video || !stream) return;

    video.srcObject = stream;
  }, [isWebRTCActive]);

  useEffect(() => {
    if (!isWebRTCActive) return;

    const canvas = overlayCanvasRef.current;
    const video = localVideoRef.current;
    if (!canvas || !video) return;

    const ctx = canvas.getContext("2d");
    let rafId;

    const drawOverlay = () => {
      const w = video.videoWidth || 640;
      const h = video.videoHeight || 480;

      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawSkeleton(ctx, landmarks, canvas.width, canvas.height);
      rafId = requestAnimationFrame(drawOverlay);
    };

    drawOverlay();
    return () => cancelAnimationFrame(rafId);
  }, [isWebRTCActive, landmarks]);

  // ✅ Badge queue system
  useEffect(() => {
    if (showBadge || badgeQueue.length === 0) return;

    setShowBadge(badgeQueue[0]);

    const timer = setTimeout(() => {
      setShowBadge(null);
      setBadgeQueue(prev => prev.slice(1));
    }, 3000);

    return () => clearTimeout(timer);
  }, [badgeQueue, showBadge]);

  const xpPercent = state.xp_required
    ? (state.xp / state.xp_required) * 100
    : 0;

  const exercises = ["Squat", "Pushup", "Lunge", "Plank", "JumpingJack"];

  const startWorkout = async () => {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/start?exercise=${selectedExercise}&name=${username}`,
        { method: "POST" }
      );
      if (!res.ok) {
        throw new Error("Failed to start workout");
      }

      await startWebRTC();
      setIsWorkoutActive(true);
    } catch (error) {
      console.error("Start workout error:", error);
      stopWebRTC();
    }
  };

  const stopWorkout = async () => {
    stopWebRTC();
    setIsWorkoutActive(false);
    try {
      const res = await fetch(`http://127.0.0.1:8000/stop?name=${username}`, {
        method: "POST"
      });
      if (!res.ok) {
        throw new Error("Failed to stop workout");
      }

      const historyRes = await fetch(`http://127.0.0.1:8000/history?name=${username}`);
      const data = await historyRes.json();
      setHistory(data);
    } catch (error) {
      console.error("Stop workout error:", error);
    }
  };

  if (!username) {
    return <Login setUsername={setUsername} />;
  }

  return (
    <div>
      <h1 className="title">🏋️ AI Gym Trainer</h1>

      <h2>Select Exercise</h2>
      <div className="exercise-grid">
        {exercises.map((ex) => (
          <div
            key={ex}
            className={`exercise-card ${selectedExercise === ex ? "active" : ""}`}
            onClick={() => setSelectedExercise(ex)}
          >
            {ex}
          </div>
        ))}
      </div>

      <div className="controls">
        <button
          className="button"
          onClick={startWorkout}
          disabled={isWorkoutActive}
        >
          ▶ Start Workout
        </button>

        <button
          className="button button-stop"
          onClick={stopWorkout}
          disabled={!isWorkoutActive}
        >
          ⏹ Stop Workout
        </button>
      </div>

      <div className="main">
        {/* CAMERA */}
        <div className="camera-container">
          {isWebRTCActive ? (
            <div className="camera-stack">
              <video
                ref={localVideoRef}
                className="camera"
                autoPlay
                playsInline
                muted
              />
              <canvas
                ref={overlayCanvasRef}
                width={640}
                height={480}
                className="camera camera-overlay"
              />
            </div>
          ) : (
            <canvas
              ref={canvasRef}
              width={640}
              height={480}
              className="camera"
            />
          )}
        </div>

        {/* RIGHT PANEL */}
        <div className="panel">
          <h2>🏃 {state.exercise}</h2>

          <div className="card">
            <h3>Reps</h3>
            <p className="big-text">{state.reps}</p>
          </div>

          <div className="card">
            <h3>Level {state.level}</h3>
            <div className="xp-bar">
              <div
                className="xp-fill"
                style={{ width: `${xpPercent}%` }}
              />
            </div>
            <p>{state.xp} / {state.xp_required} XP</p>
          </div>

          <div className="card">
            <h3>Feedback</h3>
            <p>{state.feedback || "Good form 👍"}</p>
          </div>

          <div className="card leaderboard">
            <h3>🏆 Leaderboard</h3>
            {leaderboard.map((user, i) => (
              <div key={i} className="leaderboard-item">
                <span>{i + 1}. {user.name}</span>
                <span>{user.xp} XP</span>
              </div>
            ))}
          </div>

          {/* ✅ HISTORY UI (NEW) */}
          <div className="card">
            <h3>📜 Workout History</h3>

            {history.length === 0 ? (
              <p>No workouts yet</p>
            ) : (
              history.slice().reverse().map((h, i) => (
                <div key={i} className="history-item">
                  <span>{h.exercise}</span>
                  <span>{h.reps} reps</span>
                  <span>{new Date(h.date).toLocaleDateString()}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {showBadge && (
        <div className="badge-popup">
          🏆 {showBadge} Unlocked!
        </div>
      )}
    </div>
  );
}

export default App;