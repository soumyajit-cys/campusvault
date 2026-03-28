// Lightweight field validators

/** Returns true if value is a non-empty string */
export function isNotEmpty(value) {
  return typeof value === "string" && value.trim().length > 0;
}

/** Returns true if value looks like a valid email */
export function isEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((value || "").trim());
}

/** Returns true if value meets minimum length */
export function isMinLength(value, min) {
  return typeof value === "string" && value.length >= min;
}