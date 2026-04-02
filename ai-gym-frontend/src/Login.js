import React, { useState } from "react";
import { apiUrl } from "./apiConfig";

function Login({ setUsername }) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const handleLogin = () => {
    if (!name.trim()) {
      setError("Please enter a username.");
      return;
    }

  fetch(apiUrl(`/login?name=${encodeURIComponent(name)}`), {
      method: "POST"
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data?.detail || "Login failed");
        }
        return data;
      })
      .then(data => {
        setError("");
        localStorage.setItem("username", data.name);
        setUsername(data.name);
      })
      .catch(err => setError(err.message || "Unable to login right now."));
  };

  return (
    <div className="login">
      <h2>Login</h2>
      <input
        type="text"
        placeholder="Enter username"
        value={name}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            handleLogin();
          }
        }}
      />
      <button onClick={handleLogin}>Login</button>
      {error ? <p style={{ color: "#b00020", marginTop: "10px" }}>{error}</p> : null}
    </div>
  );
}

export default Login;
