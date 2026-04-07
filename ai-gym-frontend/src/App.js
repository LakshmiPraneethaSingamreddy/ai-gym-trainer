import React, { useEffect, useRef, useState } from "react";
import "./App.css";
import Login from "./Login";
import { apiUrl, wsUrl } from "./apiConfig";

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

const INITIAL_STATE = {
  reps: 0,
  xp: 0,
  xp_required: 100,
  level: 1,
  feedback: "",
  exercise: "",
  badges: []
};

function App() {
  const formatDuration = (secondsValue) => {
    const totalSeconds = Math.max(0, Math.floor(Number(secondsValue) || 0));
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  };

  const [state, setState] = useState(INITIAL_STATE);

  const [username, setUsername] = useState(
    localStorage.getItem("username") || ""
  );

  const [showBadge, setShowBadge] = useState(null);
  const [badgeQueue, setBadgeQueue] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [history, setHistory] = useState([]); // ✅ NEW
  const [cameraError, setCameraError] = useState("");
  const [selectedExercise, setSelectedExercise] = useState("Squat");
  const [landmarks, setLandmarks] = useState([]);
  const [isWebRTCActive, setIsWebRTCActive] = useState(false);
  const [isWorkoutActive, setIsWorkoutActive] = useState(false);

  const canvasRef = useRef(null);
  const overlayCanvasRef = useRef(null);
  const localVideoRef = useRef(null);
  const localStreamRef = useRef(null);
  const pcRef = useRef(null);
  const mediaTrackRegistryRef = useRef(new Set());
  const startSequenceRef = useRef(0);

  const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const ensureApiAwake = async () => {
    // Render free services can sleep; wake API before starting workout flow.
    await fetch(apiUrl("/"), { method: "GET" });
  };

  const startSessionWithRetry = async (maxAttempts = 3) => {
    let lastError;

    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      try {
        await ensureApiAwake();
        const res = await fetch(
          apiUrl(`/start?exercise=${selectedExercise}&name=${username}`),
          { method: "POST" }
        );

        if (!res.ok) {
          let errorDetail = "Failed to start workout";
          try {
            const errorPayload = await res.json();
            if (errorPayload?.detail) {
              errorDetail = errorPayload.detail;
            }
          } catch (_parseError) {
            // Keep default message when response body is not JSON.
          }

          throw new Error(errorDetail);
        }

        return;
      } catch (error) {
        lastError = error;

        if (attempt < maxAttempts) {
          await delay(1400 * attempt);
        }
      }
    }

    throw lastError || new Error("Failed to start workout");
  };

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
      fetch(apiUrl("/leaderboard"))
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

    fetch(apiUrl(`/history?name=${username}`))
      .then(res => res.json())
      .then(data => setHistory(data))
      .catch(err => console.error("History error:", err));
  }, [username]);

  const stopWebRTC = () => {
    setIsWebRTCActive(false);

    if (pcRef.current) {
      try {
        pcRef.current.getSenders().forEach((sender) => {
          if (sender.track) {
            sender.track.stop();
          }
        });
      } catch (error) {
        console.error("Error stopping RTCPeerConnection senders:", error);
      }
      pcRef.current.close();
      pcRef.current = null;
    }

    const stream = localStreamRef.current;
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      localStreamRef.current = null;
    }

    // Stop any tracks we have ever opened in this session.
    mediaTrackRegistryRef.current.forEach((track) => {
      try {
        track.stop();
      } catch (error) {
        console.error("Error stopping media track:", error);
      }
    });
    mediaTrackRegistryRef.current.clear();

    if (localVideoRef.current) {
      const attachedStream = localVideoRef.current.srcObject;
      if (attachedStream && typeof attachedStream.getTracks === "function") {
        attachedStream.getTracks().forEach((track) => track.stop());
      }
      localVideoRef.current.pause();
      localVideoRef.current.srcObject = null;
    }

    // Extra safeguard for any leftover preview elements.
    document.querySelectorAll("video").forEach((videoEl) => {
      const src = videoEl.srcObject;
      if (src && typeof src.getTracks === "function") {
        src.getTracks().forEach((track) => track.stop());
      }
      videoEl.pause();
      videoEl.srcObject = null;
    });

    if (overlayCanvasRef.current) {
      const overlayCtx = overlayCanvasRef.current.getContext("2d");
      overlayCtx.clearRect(0, 0, overlayCanvasRef.current.width, overlayCanvasRef.current.height);
    }

    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext("2d");
      ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      ctx.fillStyle = "#0a0f23";
      ctx.fillRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      ctx.fillStyle = "#c7d2ea";
      ctx.font = "600 22px Outfit";
      ctx.textAlign = "center";
      ctx.fillText("Camera Stopped", canvasRef.current.width / 2, canvasRef.current.height / 2);
    }

    setLandmarks([]);
  };

  const startWebRTC = async () => {
    stopWebRTC();

    const canUseGetUserMedia =
      typeof navigator !== "undefined" &&
      navigator.mediaDevices &&
      typeof navigator.mediaDevices.getUserMedia === "function";

    if (!canUseGetUserMedia) {
      const isLikelyInsecureOrigin =
        typeof window !== "undefined" &&
        window.location.protocol !== "https:" &&
        window.location.hostname !== "localhost" &&
        window.location.hostname !== "127.0.0.1";

      const reason = isLikelyInsecureOrigin
        ? "Camera access is blocked on insecure HTTP origin. Open the app on HTTPS (or localhost)."
        : "This browser/device does not expose camera APIs (mediaDevices.getUserMedia).";

      throw new Error(reason);
    }

    let localStream;
    try {
      localStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: { ideal: "user" },
        },
        audio: false,
      });
    } catch (error) {
      if (error?.name === "NotAllowedError") {
        throw new Error(
          "Camera permission denied. Allow camera access in browser site settings and try again."
        );
      }
      if (error?.name === "NotFoundError") {
        throw new Error(
          "No camera device found. Connect a camera and retry."
        );
      }
      if (error?.name === "NotReadableError") {
        throw new Error(
          "Camera is busy in another app/tab. Close other camera apps and retry."
        );
      }
      throw new Error(
        "Unable to access camera. Check browser permissions and HTTPS, then retry."
      );
    }
    localStreamRef.current = localStream;
    localStream.getTracks().forEach((track) => mediaTrackRegistryRef.current.add(track));

    if (localVideoRef.current) {
      localVideoRef.current.srcObject = localStream;
      try {
        await localVideoRef.current.play();
      } catch (playError) {
        console.warn("Local preview play warning:", playError);
      }
    }
    setIsWebRTCActive(true);

    const pc = new RTCPeerConnection();
    pcRef.current = pc;
    localStream.getTracks().forEach((track) => pc.addTrack(track, localStream));

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    const response = await fetch(apiUrl("/webrtc/offer"), {
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
    if (pc.signalingState === "closed") {
      throw new Error("WebRTC session was closed before negotiation completed.");
    }
    await pc.setRemoteDescription(answer);
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

    const ws = new WebSocket(wsUrl("/ws"));

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

  // ✅ Badge queue system — show badge when queue has items and no badge is showing
  useEffect(() => {
    if (showBadge !== null || badgeQueue.length === 0) return;

    setShowBadge(badgeQueue[0]);
  }, [badgeQueue, showBadge]);

  // ✅ Auto-hide badge after 3 seconds
  useEffect(() => {
    if (showBadge === null) return;

    const timer = setTimeout(() => {
      setShowBadge(null);
      setBadgeQueue(prev => prev.slice(1));
    }, 3000);

    return () => clearTimeout(timer);
  }, [showBadge]);

  const xpPercent = state.xp_required
    ? (state.xp / state.xp_required) * 100
    : 0;
  const isPlankActive = (state.exercise || selectedExercise) === "Low Plank";

  const exercises = ["Squat", "Knee/Regular Pushups", "Lunge", "Low Plank"];

  // Map exercises to camera positioning guidance
  const cameraPosGuide = {
    "Squat": "Face camera sideways (profile view)",
    "Knee/Regular Pushups": "Face camera sideways (profile view)",
    "Lunge": "Face camera front-on (frontal view)",
    "Low Plank": "Face camera sideways (profile view)",
  };

  const startWorkout = async () => {
    const myStartSequence = ++startSequenceRef.current;
    setCameraError("");

    try {
      await startSessionWithRetry();

      await startWebRTC();

      // If a newer start/stop happened while this one was in-flight, abort this run.
      if (myStartSequence !== startSequenceRef.current) {
        stopWebRTC();
        return;
      }

      setIsWorkoutActive(true);
    } catch (error) {
      console.error("Start workout error:", error);

      const isFetchFailure =
        error?.name === "TypeError" ||
        String(error?.message || "").toLowerCase().includes("failed to fetch");

      if (isFetchFailure) {
        setCameraError(
          "Could not reach backend. Render free tier may be waking up; wait 20-40 seconds and click Start Workout again."
        );
      } else {
        setCameraError(error?.message || "Could not start camera/workout.");
      }

      stopWebRTC();
      setIsWorkoutActive(false);

      // If backend session started before camera setup failed, stop it so UI and server stay in sync.
      try {
        await fetch(apiUrl(`/stop?name=${username}`), {
          method: "POST",
        });
      } catch (stopError) {
        console.error("Start workout cleanup stop error:", stopError);
      }
    }
  };

  const stopWorkout = async () => {
    // Invalidate any in-flight start attempt so stop always wins.
    startSequenceRef.current += 1;
    setIsWorkoutActive(false);
    setCameraError("");

    try {
      const res = await fetch(apiUrl(`/stop?name=${username}`), {
        method: "POST"
      });
      if (!res.ok) {
        throw new Error("Failed to stop workout");
      }

      const historyRes = await fetch(apiUrl(`/history?name=${username}`));
      const data = await historyRes.json();
      setHistory(data);
    } catch (error) {
      console.error("Stop workout error:", error);
    } finally {
      stopWebRTC();
    }
  };

  const handleSignout = async () => {
    try {
      await fetch(apiUrl(`/signout?name=${username}`), { method: "POST" });
    } catch (error) {
      console.error("Sign out error:", error);
    }

    stopWebRTC();
    setIsWorkoutActive(false);
    setState({ ...INITIAL_STATE });
    setHistory([]);
    setLeaderboard([]);
    setBadgeQueue([]);
    setShowBadge(null);
    setCameraError("");
    localStorage.removeItem("username");
    setUsername("");
  };

  if (!username) {
    return <Login setUsername={setUsername} />;
  }

  return (
    <div className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <header className="hero">
        <div>
          <p className="eyebrow">AI Powered Coaching</p>
          <h1 className="title">AI Gym Trainer</h1>
          <p className="subtitle">
            Real-time rep tracking, posture feedback, and progress metrics in one live training board.
          </p>
        </div>
        <div className="user-pill">
          <div>
            <span className="pill-label">Athlete: </span>
            <strong>{username}</strong>
          </div>
          <button type="button" className="logout-btn" onClick={handleSignout}>
            Sign Out
          </button>
        </div>
      </header>

      <section className="exercise-section">
        <h2 className="section-heading">Choose Workout</h2>
        <div className="exercise-grid">
          {exercises.map((ex) => (
            <button
              key={ex}
              type="button"
              className={`exercise-card ${selectedExercise === ex ? "active" : ""}`}
              onClick={() => setSelectedExercise(ex)}
            >
              {ex}
            </button>
          ))}
        </div>
      </section>

      <div className="controls">
        <button
          className="button"
          onClick={startWorkout}
          disabled={isWorkoutActive || isWebRTCActive}
        >
          Start Workout
        </button>

        <button
          className="button button-stop"
          onClick={stopWorkout}
          disabled={!(isWorkoutActive || isWebRTCActive)}
        >
          Stop Workout
        </button>
      </div>

      {cameraError ? <p className="camera-error">{cameraError}</p> : null}

      <div className="main">
        {/* CAMERA */}
        <section className="camera-container card-surface">
          <div className="camera-header">
            <h2>Live Camera</h2>
            <span className={`status-chip ${isWebRTCActive ? "live" : "idle"}`}>
              {isWebRTCActive ? "Streaming" : "Idle"}
            </span>
          </div>

          <div className="camera-frame">
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
        </section>

        {/* RIGHT PANEL */}
        <aside className="panel">
          <div className="card current-exercise">
            <h2>{state.exercise || selectedExercise}</h2>
            <p>{cameraPosGuide[state.exercise || selectedExercise] || "Face camera for detection"}</p>
          </div>

          <div className="card reps-card">
            <h3>{isPlankActive ? "Low Plank Timer" : "Reps"}</h3>
            <p className="big-text">{isPlankActive ? formatDuration(state.reps) : state.reps}</p>
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

          <div className="card feedback-card">
            <h3>Feedback</h3>
            <p>{state.feedback || "Keep it up! 🔥"}</p>
          </div>

          <div className="card leaderboard">
            <h3>Level-wise Leaderboard</h3>
            {leaderboard.map((user, i) => (
              <div key={i} className="leaderboard-item">
                <span>{i + 1}. {user.name}</span>
                <span>{user.xp} XP</span>
              </div>
            ))}
          </div>

          {/* ✅ HISTORY UI (NEW) */}
          <div className="card">
            <h3>Workout History</h3>

            {history.length === 0 ? (
              <p>No workouts yet</p>
            ) : (
              <div className="history-scroll" role="region" aria-label="Workout history list">
                {history.slice().reverse().map((h, i) => (
                  <div key={i} className="history-item">
                    <span>{h.exercise}</span>
                    <span>{h.reps} reps</span>
                    <span>{new Date(h.date).toLocaleDateString()}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </aside>
      </div>

      {showBadge && (
        <div className="badge-popup">
          {showBadge} Unlocked!
        </div>
      )}
    </div>
  );
}

export default App;