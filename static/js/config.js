// ===========================
// config.js — App-wide constants
// ===========================

export const API_BASE = "";   // same origin as Flask

export const ROLES = {
  STUDENT: "student",
  FACULTY: "faculty",
  ADMIN:   "admin",
};

export const DASHBOARD = {
  student: "/dashboard.student.html",
  faculty: "/dashboard.faculty.html",
  admin:   "/admin_dashboard.html",
};