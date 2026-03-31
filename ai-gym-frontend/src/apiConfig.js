const FALLBACK_HOST = typeof window !== "undefined" ? window.location.hostname : "127.0.0.1";
const FALLBACK_PROTOCOL = typeof window !== "undefined" && window.location.protocol === "https:"
  ? "https"
  : "http";
const DEFAULT_API_BASE = `${FALLBACK_PROTOCOL}://${FALLBACK_HOST}:8000`;

export const API_BASE = (process.env.REACT_APP_API_BASE_URL || DEFAULT_API_BASE).replace(/\/$/, "");

export const WS_BASE = API_BASE.startsWith("https://")
  ? API_BASE.replace("https://", "wss://")
  : API_BASE.replace("http://", "ws://");
