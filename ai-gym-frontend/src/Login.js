import React, { useState } from "react";

function Login({ setUsername }) {
  const [name, setName] = useState("");

  const handleLogin = () => {
    if (!name) return;

    fetch(`http://127.0.0.1:8000/login?name=${name}`, {
      method: "POST"
    })
      .then(res => res.json())
      .then(data => {
        localStorage.setItem("username", data.name);
        setUsername(data.name);
      })
      .catch(err => console.error(err));
  };

  return (
    <div className="login">
      <h2>Login</h2>
      <input
        type="text"
        placeholder="Enter username"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <button onClick={handleLogin}>Enter</button>
    </div>
  );
}

export default Login;
