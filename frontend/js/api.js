// http client wrapper and shared formatting helpers

const API_BASE = window.location.port === "5000" || window.location.port === ""
  ? ""
  : "http://127.0.0.1:5000";

const TOKEN_KEY = "stm_auth_token";

export function saveToken(token) {
  if (token) {
    sessionStorage.setItem(TOKEN_KEY, token);
  }
}

export function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY);
}

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

export async function apiRequest(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method || "GET",
    headers,
    credentials: "include",
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  let data = {};
  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    const err = new Error(data.error || "Request failed.");
    err.status = response.status;
    throw err;
  }

  return data;
}

export async function requireSession() {
  try {
    const data = await apiRequest("/api/auth/me");
    return data.user;
  } catch {
    clearToken();
    window.location.href = "/login.html";
    return null;
  }
}

export function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export function formatDisplayDate(isoDate) {
  if (!isoDate) return "-";
  const parsed = new Date(`${isoDate}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return isoDate;
  return parsed.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function priorityBadgeClass(priority) {
  if (priority === "High") return "badge-danger";
  if (priority === "Medium") return "badge-warning";
  return "badge-neutral";
}

export function statusBadgeClass(status) {
  if (status === "Completed") return "badge-success";
  if (status === "In Progress") return "badge-primary";
  return "badge-neutral";
}

export function renderDeadlineCell(isoDate, deadlineStatus) {
  const formatted = escapeHtml(formatDisplayDate(isoDate));
  if (deadlineStatus === "overdue") {
    return `<span class="deadline-cell">${formatted} <span class="badge badge-danger">Overdue</span></span>`;
  }
  if (deadlineStatus === "due_today") {
    return `<span class="deadline-cell">${formatted} <span class="badge badge-warning">Due Today</span></span>`;
  }
  return `<span class="deadline-cell">${formatted}</span>`;
}
