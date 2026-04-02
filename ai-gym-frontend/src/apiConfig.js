const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

const trimTrailingSlash = (value) => value.replace(/\/+$/, "");

export const API_BASE_URL = trimTrailingSlash(
  process.env.REACT_APP_API_BASE_URL || DEFAULT_API_BASE_URL
);

export const WS_BASE_URL = API_BASE_URL.startsWith("https://")
  ? API_BASE_URL.replace(/^https:\/\//, "wss://")
  : API_BASE_URL.replace(/^http:\/\//, "ws://");

export const apiUrl = (path) => `${API_BASE_URL}${path}`;
export const wsUrl = (path) => `${WS_BASE_URL}${path}`;
