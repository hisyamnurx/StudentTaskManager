// login and register form handlers

import { apiRequest, clearToken, saveToken } from "./api.js";
import { hideAlert, showAlert } from "./layout.js";

async function redirectIfAuthenticated() {
  try {
    await apiRequest("/api/auth/me");
    window.location.href = "/dashboard.html";
  } catch {
    clearToken();
  }
}

function initLoginPage() {
  const form = document.getElementById("loginForm");
  if (!form) return;

  const alertBox = document.getElementById("authAlert");
  const params = new URLSearchParams(window.location.search);
  if (params.get("registered") === "1") {
    showAlert(alertBox, "Account created successfully. Please sign in.", "success");
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideAlert(alertBox);

    const identifier = document.getElementById("loginIdentifier").value.trim();
    const password = document.getElementById("loginPassword").value;

    if (!identifier || !password) {
      showAlert(alertBox, "Email / NIM and password are required.", "error");
      return;
    }

    try {
      const data = await apiRequest("/api/auth/login", {
        method: "POST",
        body: { identifier, password },
      });
      saveToken(data.token);
      window.location.href = "/dashboard.html";
    } catch (err) {
      showAlert(alertBox, `Validation error: ${err.message}`, "error");
    }
  });
}

function initRegisterPage() {
  const form = document.getElementById("registerForm");
  if (!form) return;

  const alertBox = document.getElementById("authAlert");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideAlert(alertBox);

    const full_name = document.getElementById("regFullName").value.trim();
    const nim = document.getElementById("regNim").value.trim();
    const email = document.getElementById("regEmail").value.trim();
    const password = document.getElementById("regPassword").value;
    const confirm_password = document.getElementById("regConfirmPassword").value;

    if (!full_name || !nim || !email || !password || !confirm_password) {
      showAlert(alertBox, "Validation error: All fields are required.", "error");
      return;
    }
    if (password !== confirm_password) {
      showAlert(alertBox, "Validation error: Passwords do not match.", "error");
      return;
    }

    try {
      await apiRequest("/api/auth/register", {
        method: "POST",
        body: { full_name, nim, email, password, confirm_password },
      });
      window.location.href = "/login.html?registered=1";
    } catch (err) {
      showAlert(alertBox, `Validation error: ${err.message}`, "error");
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  await redirectIfAuthenticated();
  initLoginPage();
  initRegisterPage();
});
