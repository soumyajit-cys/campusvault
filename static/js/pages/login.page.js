// ===========================
// login.page.js
// Handles the sign-in page
// ===========================

import { isNotEmpty }       from "../lib/validator.js";
import { apiFetch }         from "../api.js";
import { handleAuthSuccess } from "../auth.js";
import { showToast }        from "../ui.js";
import { showError, clearError, setLoading } from "../lib/dom.js";

document.addEventListener("DOMContentLoaded", () => {
  const form      = document.getElementById("login-form");
  const errorEl   = document.getElementById("login-error");
  const submitBtn = form.querySelector("button[type='submit']");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError(errorEl);

    // ── Read form fields ────────────────────────────────────────────────
    // HTML uses id="siteid" for the College ID / User-ID field
    const college_id = document.getElementById("siteid").value.trim();
    const password   = document.getElementById("password").value;

    // ── Client-side validation ──────────────────────────────────────────
    if (!isNotEmpty(college_id)) {
      showError(errorEl, "Please enter your User ID.");
      return;
    }
    if (!isNotEmpty(password)) {
      showError(errorEl, "Please enter your password.");
      return;
    }

    setLoading(submitBtn, true);

    try {
      // ── Call backend ────────────────────────────────────────────────
      const res = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ college_id, password }),
      });

      if (!res || res.error) {
        const msg = res?.error || "Login failed. Please try again.";
        showError(errorEl, msg);
        return;
      }

      // ── Success ─────────────────────────────────────────────────────
      const token = res.token || res.data?.token;
      const user  = res.user  || res.data?.user;

      if (!token || !user) {
        showError(errorEl, "Unexpected server response. Please try again.");
        return;
      }

      showToast(`Welcome back, ${user.name}!`, "success");
      handleAuthSuccess(token, user);   // saves session + redirects

    } catch (err) {
      console.error("Login error:", err);
      showError(errorEl, "Could not reach the server. Try again later.");
    } finally {
      setLoading(submitBtn, false, "Login");
    }
  });
});