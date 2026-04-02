import React, { useState } from "react";
import { apiUrl } from "./apiConfig";

function Login({ setUsername }) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const handleSignIn = () => {
    if (!name.trim()) {
      setError("Please enter a username to sign up or sign in.");
      return;
    }

  fetch(apiUrl(`/signin?name=${encodeURIComponent(name)}`), {
      method: "POST"
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data?.detail || "Sign in failed");
        }
        return data;
      })
      .then(data => {
        setError("");
        localStorage.setItem("username", data.name);
        setUsername(data.name);
      })
      .catch(err => setError(err.message || "Unable to sign in right now."));
  };

  return (
    <div className="login">
      <h2>Sign Up / Sign In</h2>
      <input
        type="text"
        placeholder="Choose or enter username"
        value={name}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            handleSignIn();
          }
        }}
      />
      <button onClick={handleSignIn}>Submit</button>
      {error ? <p style={{ color: "#b00020", marginTop: "10px" }}>{error}</p> : null}
    </div>
  );
}

export default Login;
