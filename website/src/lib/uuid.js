// src/lib/uuid.js
// Persist a stable per-browser UUID in localStorage.
//
// Used by:
//   • analytics.js (track unique visitors + heartbeat session key)
//   • seeddb.js (optional — to namespace a user's seeds)
//
// Why localStorage (not cookies):
//   • Survives across tabs + reloads.
//   • No HTTP overhead — pure client-side.
//   • For analytics we only need "is this the same browser" — not "who
//     is the logged-in user", so a localStorage UUID is enough.

const UUID_KEY = 'minebed:uuid';

/**
 * Return the existing UUID for this browser, or generate a new one and
 * persist it. Always returns a string (36 chars in standard UUID format
 * when crypto.randomUUID is available).
 */
export function getOrCreateUUID() {
  if (typeof localStorage === 'undefined') return 'anon-' + Date.now();

  let uuid = localStorage.getItem(UUID_KEY);
  if (uuid && uuid.length >= 8) return uuid;

  // Generate a fresh UUID
  uuid = generateUUID();
  try {
    localStorage.setItem(UUID_KEY, uuid);
  } catch (e) {
    // localStorage may be disabled (private mode) — return the in-memory
    // uuid anyway. Analytics will work for this session only.
  }
  return uuid;
}

/**
 * Public reset — useful if the user wants to "forget" their identity.
 * Exposed for a future Privacy / GDPR panel.
 */
export function resetUUID() {
  try {
    localStorage.removeItem(UUID_KEY);
  } catch (e) {}
}

function generateUUID() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  // Fallback RFC4122 v4 — uses Math.random (less ideal, but works in
  // every browser including IE11).
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
