// ===========================
// dom.js — Tiny DOM helpers
// ===========================

/** Show an error element with a message */
export function showError(el, message) {
  if (!el) return;
  el.textContent = message;
  el.classList.add("active");
}

/** Clear / hide an error element */
export function clearError(el) {
  if (!el) return;
  el.textContent = "";
  el.classList.remove("active");
}

/** Disable or re-enable a button with optional label change */
export function setLoading(btn, loading, label = "Login") {
  if (!btn) return;
  btn.disabled = loading;
  btn.textContent = loading ? "Please wait…" : label;
}