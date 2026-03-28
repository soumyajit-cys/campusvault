// Shared UI utilities

/**
 * Show a brief toast notification.
 * @param {string} message
 * @param {"success"|"error"|"info"} type
 * @param {number} duration  ms before auto-dismiss
 */
export function showToast(message, type = "info", duration = 3000) {
  // Reuse existing container or create one
  let container = document.getElementById("cv-toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "cv-toast-container";
    Object.assign(container.style, {
      position: "fixed",
      bottom: "1.5rem",
      right: "1.5rem",
      display: "flex",
      flexDirection: "column",
      gap: "0.5rem",
      zIndex: 9999,
    });
    document.body.appendChild(container);
  }

  const colors = {
    success: "#22c55e",
    error:   "#ef4444",
    info:    "#3b82f6",
  };

  const toast = document.createElement("div");
  toast.textContent = message;
  Object.assign(toast.style, {
    background:   colors[type] || colors.info,
    color:        "#fff",
    padding:      "0.65rem 1.1rem",
    borderRadius: "0.4rem",
    fontWeight:   "600",
    fontSize:     "0.9rem",
    boxShadow:    "0 4px 12px rgba(0,0,0,.15)",
    opacity:      "1",
    transition:   "opacity 0.3s ease",
  });

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 320);
  }, duration);
}