// courses management: search, sks filter, crud, and delete protection

import { apiRequest, escapeHtml } from "./api.js";
import { hideAlert, initAppLayout, showAlert } from "./layout.js";

let currentCourses = [];
let editingCourseId = null;

function renderCourseTable(totalSks) {
  const tbody = document.getElementById("coursesBody");
  const badge = document.getElementById("courseCountBadge");
  badge.textContent = `${currentCourses.length} ${currentCourses.length === 1 ? "course" : "courses"} · ${totalSks} SKS total`;

  if (currentCourses.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No courses found.</td></tr>';
    return;
  }

  tbody.innerHTML = currentCourses
    .map((course) => {
      const taskLabel = `${course.linked_tasks} ${course.linked_tasks === 1 ? "task" : "tasks"}`;
      const taskBadge = course.linked_tasks > 0 ? "badge-primary" : "badge-neutral";
      const inUseNote = course.can_delete ? "" : '<span class="in-use-note">In use</span>';
      return `
        <tr>
          <td class="cell-code">${escapeHtml(course.kode)}</td>
          <td class="cell-strong">${escapeHtml(course.nama)}</td>
          <td><span class="badge badge-neutral">${course.sks} SKS</span></td>
          <td><span class="badge ${taskBadge}">${taskLabel}</span></td>
          <td>
            <div class="actions-cell">
              <button type="button" class="btn btn-table-edit" data-action="edit" data-id="${course.id}">Edit</button>
              <button type="button" class="btn btn-table-delete" data-action="delete" data-id="${course.id}" ${course.can_delete ? "" : "disabled"}>Delete</button>
              ${inUseNote}
            </div>
          </td>
        </tr>
      `;
    })
    .join("");
}

async function fetchCourses() {
  const params = new URLSearchParams();
  const search = document.getElementById("courseSearch").value.trim();
  const sks = document.getElementById("courseSksFilter").value;
  if (search) params.set("search", search);
  if (sks) params.set("sks", sks);

  const query = params.toString();
  const data = await apiRequest(`/api/courses${query ? `?${query}` : ""}`);
  currentCourses = data.courses;
  const visibleSks = currentCourses.reduce((sum, c) => sum + Number(c.sks), 0);
  renderCourseTable(visibleSks);
}

function resetCourseForm() {
  editingCourseId = null;
  document.getElementById("courseForm").reset();
  document.getElementById("courseFormTitle").textContent = "Course Form (Add Course)";
  document.getElementById("saveCourseBtn").textContent = "Save Course";
  hideAlert(document.getElementById("courseFormAlert"));
}

function loadCourseIntoForm(course) {
  editingCourseId = course.id;
  document.getElementById("courseCode").value = course.kode;
  document.getElementById("courseName").value = course.nama;
  document.getElementById("courseSks").value = String(course.sks);
  document.getElementById("courseFormTitle").textContent = `Course Form (Edit Course #${course.id})`;
  document.getElementById("saveCourseBtn").textContent = "Update Course";
  hideAlert(document.getElementById("courseFormAlert"));
  document.getElementById("courseFormCard").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

document.addEventListener("DOMContentLoaded", async () => {
  const user = await initAppLayout("courses");
  if (!user) return;
  await fetchCourses();

  document.getElementById("headerAddCourseBtn").addEventListener("click", () => {
    resetCourseForm();
    document.getElementById("courseFormCard").scrollIntoView({ behavior: "smooth", block: "nearest" });
    document.getElementById("courseCode").focus();
  });

  document.getElementById("courseFilterForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    await fetchCourses();
  });

  document.getElementById("resetCourseFiltersBtn").addEventListener("click", async () => {
    document.getElementById("courseFilterForm").reset();
    await fetchCourses();
  });

  document.getElementById("coursesBody").addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const courseId = Number(btn.dataset.id);
    const course = currentCourses.find((c) => c.id === courseId);
    if (!course) return;

    const alertBox = document.getElementById("courseFormAlert");
    if (btn.dataset.action === "edit") {
      loadCourseIntoForm(course);
    } else if (btn.dataset.action === "delete") {
      try {
        await apiRequest(`/api/courses/${courseId}`, { method: "DELETE" });
        if (editingCourseId === courseId) resetCourseForm();
        await fetchCourses();
      } catch (err) {
        showAlert(alertBox, err.message, "error");
      }
    }
  });

  document.getElementById("cancelCourseBtn").addEventListener("click", resetCourseForm);

  document.getElementById("courseForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const alertBox = document.getElementById("courseFormAlert");
    hideAlert(alertBox);

    const payload = {
      kode: document.getElementById("courseCode").value.trim(),
      nama: document.getElementById("courseName").value.trim(),
      sks: document.getElementById("courseSks").value,
    };

    try {
      if (editingCourseId) {
        await apiRequest(`/api/courses/${editingCourseId}`, { method: "PUT", body: payload });
        resetCourseForm();
        showAlert(alertBox, "Course updated successfully.", "success");
      } else {
        await apiRequest("/api/courses", { method: "POST", body: payload });
        resetCourseForm();
        showAlert(alertBox, "Course created successfully.", "success");
      }
      await fetchCourses();
    } catch (err) {
      showAlert(alertBox, err.message, "error");
    }
  });
});
