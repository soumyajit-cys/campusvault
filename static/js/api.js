// Centralized API wrapper used by all page controllers

const API_BASE = "";   // same origin — Flask serves both frontend + API

/**
 * Wraps fetch with JSON defaults and auth header injection.
 * Always resolves (never throws on HTTP errors); returns parsed JSON or null.
 */
export async function apiFetch(path, options = {}) {
  const token = sessionStorage.getItem("auth_token");

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  // Try to parse JSON regardless of status code
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  // Attach HTTP status so callers can inspect it if needed
  if (data && typeof data === "object") data._status = res.status;

  return data;
}