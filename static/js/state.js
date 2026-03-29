// ===========================
// state.js — Session read/write helpers
// ===========================

const KEYS = {
  TOKEN:     "auth_token",
  UNIQUE_ID: "user_unique_id",
  NAME:      "user_name",
  EMAIL:     "user_email",
  ROLE:      "user_role",
  COLLEGE_ID:"user_college_id",
};

/** Save full user session after login/signup */
export function saveSession(token, user) {
  sessionStorage.setItem(KEYS.TOKEN,      token);
  sessionStorage.setItem(KEYS.UNIQUE_ID,  user.unique_id   || "");
  sessionStorage.setItem(KEYS.NAME,       user.name        || "");
  sessionStorage.setItem(KEYS.EMAIL,      user.email       || "");
  sessionStorage.setItem(KEYS.ROLE,       user.role        || "");
  sessionStorage.setItem(KEYS.COLLEGE_ID, user.college_id  || "");
}

/** Clear session on logout */
export function clearSession() {
  Object.values(KEYS).forEach(k => sessionStorage.removeItem(k));
}

/** Get the current auth token */
export function getToken() {
  return sessionStorage.getItem(KEYS.TOKEN);
}

/** Get the full session as an object */
export function getSession() {
  return {
    token:      sessionStorage.getItem(KEYS.TOKEN),
    unique_id:  sessionStorage.getItem(KEYS.UNIQUE_ID),
    name:       sessionStorage.getItem(KEYS.NAME),
    email:      sessionStorage.getItem(KEYS.EMAIL),
    role:       sessionStorage.getItem(KEYS.ROLE),
    college_id: sessionStorage.getItem(KEYS.COLLEGE_ID),
  };
}

/** Returns true if a session token exists */
export function isLoggedIn() {
  return Boolean(sessionStorage.getItem(KEYS.TOKEN));
}