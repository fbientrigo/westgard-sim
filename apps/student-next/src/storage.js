// src/storage.js
// Thin localStorage helpers. No scoring history, no streaks, no timers —
// only lightweight session continuity as specified in the contract.

function safeParse(raw, fallback) {
  if (raw === null) return fallback;
  try {
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export function readJSON(key, fallback) {
  try {
    return safeParse(window.localStorage.getItem(key), fallback);
  } catch {
    return fallback;
  }
}

export function writeJSON(key, value) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Storage may be unavailable (private mode, quota). Fail silently;
    // the app must keep working without persistence.
  }
}

export function clearKey(key) {
  try {
    window.localStorage.removeItem(key);
  } catch {
    // ignore
  }
}

export const PRACTICE_KEY = "wnext:practice:v1";
export const CARDS_KEY = "wnext:cards:v1";
