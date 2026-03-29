// ===========================
// auth.js — Auth actions (login / logout / guard)
// ===========================

import { saveSession, clearSession, isLoggedIn, getSession } from "./state.js";
import { DASHBOARD } from "./config.js";

/**
 * Persist a successful auth response and redirect to the right dashboard.
 * Called by both login.page.js and signup.page.js after a successful API call.
 *
 * @param {string} token
 * @param {object} user  — shape: { unique_id, name, email, role, college_id }
 */
export function handleAuthSuccess(token, user) {
  saveSession(token, user);

  const role = (user.role || "student").toLowerCase();
  const dest  = DASHBOARD[role] || DASHBOARD.student;

  setTimeout(() => { window.location.href = dest; }, 600);
}

/**
 * Log out: clear session and go to login page.
 */
export function logout() {
  clearSession();
  window.location.href = "/sign_in.html";
}

/**
 * Route-guard helper — call at top of any protected page.
 * Redirects to login if no session exists.
 */
export function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = "/sign_in.html";
  }
}

/**
 * Legacy-compatible login() shim so nothing breaks if other files call it.
 * Prefer handleAuthSuccess() for new code.
 */
export function login(token, user) {
  handleAuthSuccess(token, user);
}

export { isLoggedIn, getSession };