// students management: search, crud, and relation delete protection

import { apiRequest, escapeHtml } from "./api.js";
import { hideAlert, initAppLayout, showAlert } from "./layout.js";

let currentStudents = [];
let editingStudentId = null;

function renderStudentTable() {
  const tbody = document.getElementById("studentsBody");
  const badge = document.getElementById("studentCountBadge");
  badge.textContent = `${currentStudents.length} ${currentStudents.length === 1 ? "student" : "students"} · In-memory records`;

  if (currentStudents.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No students found.</td></tr>';
    return;
  }

  tbody.innerHTML = currentStudents
    .map((student) => {
      const taskLabel = `${student.assigned_tasks} ${student.assigned_tasks === 1 ? "task" : "tasks"}`;
      const taskBadge = student.assigned_tasks > 0 ? "badge-primary" : "badge-neutral";
      const inUseNote = student.can_delete ? "" : '<span class="in-use-note">In use</span>';
      return `
        <tr>
          <td class="cell-code">${escapeHtml(student.nim)}</td>
          <td class="cell-strong">${escapeHtml(student.nama)}</td>
          <td class="cell-muted">${escapeHtml(student.email)}</td>
          <td><span class="badge ${taskBadge}">${taskLabel}</span></td>
          <td>
            <div class="actions-cell">
              <button type="button" class="btn btn-table-edit" data-action="edit" data-id="${student.id}">Edit</button>
              <button type="button" class="btn btn-table-delete" data-action="delete" data-id="${student.id}" ${student.can_delete ? "" : "disabled"}>Delete</button>
              ${inUseNote}
            </div>
          </td>
        </tr>
      `;
    })
    .join("");
}

async function fetchStudents() {
  const params = new URLSearchParams();
  const search = document.getElementById("studentSearch").value.trim();
  if (search) params.set("search", search);

  const query = params.toString();
  const data = await apiRequest(`/api/students${query ? `?${query}` : ""}`);
  currentStudents = data.students;
  renderStudentTable();
}

function resetStudentForm() {
  editingStudentId = null;
  document.getElementById("studentForm").reset();
  document.getElementById("studentFormTitle").textContent = "Student Form (Add Student)";
  document.getElementById("saveStudentBtn").textContent = "Save Student";
  hideAlert(document.getElementById("studentFormAlert"));
}

function loadStudentIntoForm(student) {
  editingStudentId = student.id;
  document.getElementById("studentNim").value = student.nim;
  document.getElementById("studentName").value = student.nama;
  document.getElementById("studentEmail").value = student.email;
  document.getElementById("studentFormTitle").textContent = `Student Form (Edit Student #${student.id})`;
  document.getElementById("saveStudentBtn").textContent = "Update Student";
  hideAlert(document.getElementById("studentFormAlert"));
  document.getElementById("studentFormCard").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

document.addEventListener("DOMContentLoaded", async () => {
  const user = await initAppLayout("students");
  if (!user) return;
  await fetchStudents();

  document.getElementById("headerAddStudentBtn").addEventListener("click", () => {
    resetStudentForm();
    document.getElementById("studentFormCard").scrollIntoView({ behavior: "smooth", block: "nearest" });
    document.getElementById("studentNim").focus();
  });

  document.getElementById("studentFilterForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    await fetchStudents();
  });

  document.getElementById("resetStudentFiltersBtn").addEventListener("click", async () => {
    document.getElementById("studentFilterForm").reset();
    await fetchStudents();
  });

  document.getElementById("studentsBody").addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const studentId = Number(btn.dataset.id);
    const student = currentStudents.find((s) => s.id === studentId);
    if (!student) return;

    const alertBox = document.getElementById("studentFormAlert");
    if (btn.dataset.action === "edit") {
      loadStudentIntoForm(student);
    } else if (btn.dataset.action === "delete") {
      try {
        await apiRequest(`/api/students/${studentId}`, { method: "DELETE" });
        if (editingStudentId === studentId) resetStudentForm();
        await fetchStudents();
      } catch (err) {
        showAlert(alertBox, err.message, "error");
      }
    }
  });

  document.getElementById("cancelStudentBtn").addEventListener("click", resetStudentForm);

  document.getElementById("studentForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const alertBox = document.getElementById("studentFormAlert");
    hideAlert(alertBox);

    const payload = {
      nim: document.getElementById("studentNim").value.trim(),
      nama: document.getElementById("studentName").value.trim(),
      email: document.getElementById("studentEmail").value.trim(),
    };

    try {
      if (editingStudentId) {
        await apiRequest(`/api/students/${editingStudentId}`, { method: "PUT", body: payload });
        resetStudentForm();
        showAlert(alertBox, "Student updated successfully.", "success");
      } else {
        await apiRequest("/api/students", { method: "POST", body: payload });
        resetStudentForm();
        showAlert(alertBox, "Student created successfully.", "success");
      }
      await fetchStudents();
    } catch (err) {
      showAlert(alertBox, err.message, "error");
    }
  });
});
