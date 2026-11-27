// shared application shell initialization, user header, and alert helpers

import { apiRequest, clearToken, requireSession } from "./api.js";

function getInitials(fullName) {
  const parts = String(fullName || "User")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  if (parts.length === 0) return "U";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export async function initAppLayout(activeKey) {
  const user = await requireSession();
  if (!user) return null;

  const avatarEl = document.getElementById("navUserAvatar");
  const nameEl = document.getElementById("navUserName");
  if (avatarEl) avatarEl.textContent = getInitials(user.full_name);
  if (nameEl) nameEl.textContent = user.full_name;

  document.querySelectorAll(".sidebar-nav .nav-item[data-nav]").forEach((el) => {
    if (el.dataset.nav === activeKey) {
      el.classList.add("active");
    } else {
      el.classList.remove("active");
    }
  });

  const signOutBtn = document.getElementById("signOutBtn");
  if (signOutBtn) {
    signOutBtn.addEventListener("click", async () => {
      try {
        await apiRequest("/api/auth/logout", { method: "POST" });
      } finally {
        clearToken();
        window.location.href = "/login.html";
      }
    });
  }

  return user;
}

export function showAlert(container, message, type = "error") {
  if (!container) return;
  const textEl = container.querySelector(".alert-text");
  if (textEl) textEl.textContent = message;
  container.classList.remove("alert-hidden", "alert-error", "alert-success");
  container.classList.add(type === "success" ? "alert-success" : "alert-error");
}

export function hideAlert(container) {
  if (!container) return;
  container.classList.add("alert-hidden");
}
