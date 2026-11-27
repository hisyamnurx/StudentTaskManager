// tasks management: search, filter, sort, crud, and task assignment

import {
  apiRequest,
  escapeHtml,
  priorityBadgeClass,
  renderDeadlineCell,
  statusBadgeClass,
} from "./api.js";
import { hideAlert, initAppLayout, showAlert } from "./layout.js";

let allStudents = [];
let allCourses = [];
let currentTasks = [];
let editingTaskId = null;

function populateDropdowns() {
  const filterStudent = document.getElementById("filterStudent");
  const filterCourse = document.getElementById("filterCourse");
  const formStudent = document.getElementById("taskStudent");
  const formCourse = document.getElementById("taskCourse");

  filterStudent.innerHTML = '<option value="">All students</option>' +
    allStudents.map((s) => `<option value="${s.id}">${escapeHtml(s.nama)}</option>`).join("");

  filterCourse.innerHTML = '<option value="">All courses</option>' +
    allCourses.map((c) => `<option value="${c.id}">${escapeHtml(c.nama)}</option>`).join("");

  formStudent.innerHTML = '<option value="">Select student...</option>' +
    allStudents.map((s) => `<option value="${s.id}">${escapeHtml(s.nama)} (${escapeHtml(s.nim)})</option>`).join("");

  formCourse.innerHTML = '<option value="">Select course...</option>' +
    allCourses.map((c) => `<option value="${c.id}">${escapeHtml(c.kode)} - ${escapeHtml(c.nama)}</option>`).join("");
}

function renderTaskTable() {
  const tbody = document.getElementById("tasksBody");
  const countBadge = document.getElementById("taskCountBadge");
  countBadge.textContent = `${currentTasks.length} ${currentTasks.length === 1 ? "task" : "tasks"}`;

  if (currentTasks.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No tasks match the current filters.</td></tr>';
    return;
  }

  tbody.innerHTML = currentTasks
    .map((task) => `
      <tr>
        <td class="cell-strong">${escapeHtml(task.judul)}</td>
        <td class="cell-muted">${escapeHtml(task.course_name)}</td>
        <td>${escapeHtml(task.student_name)}</td>
        <td>${renderDeadlineCell(task.deadline, task.deadline_status)}</td>
        <td><span class="badge ${priorityBadgeClass(task.prioritas)}">${escapeHtml(task.prioritas)}</span></td>
        <td><span class="badge ${statusBadgeClass(task.status)}">${escapeHtml(task.status)}</span></td>
        <td>
          <div class="actions-cell">
            <button type="button" class="btn btn-table-edit" data-action="edit" data-id="${task.id}">Edit</button>
            <button type="button" class="btn btn-table-delete" data-action="delete" data-id="${task.id}">Delete</button>
          </div>
        </td>
      </tr>
    `)
    .join("");
}

async function fetchTasks() {
  const params = new URLSearchParams();
  const search = document.getElementById("filterSearch").value.trim();
  const studentId = document.getElementById("filterStudent").value;
  const courseId = document.getElementById("filterCourse").value;
  const status = document.getElementById("filterStatus").value;
  const priority = document.getElementById("filterPriority").value;
  const sort = document.getElementById("filterSort").value;

  if (search) params.set("search", search);
  if (studentId) params.set("student_id", studentId);
  if (courseId) params.set("course_id", courseId);
  if (status) params.set("status", status);
  if (priority) params.set("priority", priority);
  if (sort) params.set("sort", sort);

  const query = params.toString();
  const data = await apiRequest(`/api/tasks${query ? `?${query}` : ""}`);
  currentTasks = data.tasks;
  renderTaskTable();
}

function resetTaskForm() {
  editingTaskId = null;
  document.getElementById("taskForm").reset();
  document.getElementById("taskFormTitle").textContent = "Task Form (Add Task)";
  document.getElementById("saveTaskBtn").textContent = "Save Task";
  hideAlert(document.getElementById("taskFormAlert"));
}

function loadTaskIntoForm(task) {
  editingTaskId = task.id;
  document.getElementById("taskTitle").value = task.judul;
  document.getElementById("taskStudent").value = String(task.student_id);
  document.getElementById("taskCourse").value = String(task.course_id);
  document.getElementById("taskDeadline").value = task.deadline;
  document.getElementById("taskDescription").value = task.deskripsi || "";
  document.getElementById("taskPriority").value = task.prioritas;
  document.getElementById("taskStatus").value = task.status;
  document.getElementById("taskFormTitle").textContent = `Task Form (Edit Task #${task.id})`;
  document.getElementById("saveTaskBtn").textContent = "Update Task";
  hideAlert(document.getElementById("taskFormAlert"));
  document.getElementById("taskFormCard").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

document.addEventListener("DOMContentLoaded", async () => {
  const user = await initAppLayout("tasks");
  if (!user) return;

  const [studentsRes, coursesRes] = await Promise.all([
    apiRequest("/api/students"),
    apiRequest("/api/courses"),
  ]);
  allStudents = studentsRes.students;
  allCourses = coursesRes.courses;
  populateDropdowns();
  await fetchTasks();

  document.getElementById("headerAddTaskBtn").addEventListener("click", () => {
    resetTaskForm();
    document.getElementById("taskFormCard").scrollIntoView({ behavior: "smooth", block: "nearest" });
    document.getElementById("taskTitle").focus();
  });

  document.getElementById("filterForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    await fetchTasks();
  });

  document.getElementById("resetFiltersBtn").addEventListener("click", async () => {
    document.getElementById("filterForm").reset();
    await fetchTasks();
  });

  document.getElementById("tasksBody").addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const taskId = Number(btn.dataset.id);
    const task = currentTasks.find((t) => t.id === taskId);
    if (!task) return;

    if (btn.dataset.action === "edit") {
      loadTaskIntoForm(task);
    } else if (btn.dataset.action === "delete") {
      try {
        await apiRequest(`/api/tasks/${taskId}`, { method: "DELETE" });
        if (editingTaskId === taskId) resetTaskForm();
        await fetchTasks();
      } catch (err) {
        showAlert(document.getElementById("taskFormAlert"), err.message, "error");
      }
    }
  });

  document.getElementById("cancelTaskBtn").addEventListener("click", resetTaskForm);

  document.getElementById("taskForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const alertBox = document.getElementById("taskFormAlert");
    hideAlert(alertBox);

    const payload = {
      judul: document.getElementById("taskTitle").value.trim(),
      student_id: document.getElementById("taskStudent").value,
      course_id: document.getElementById("taskCourse").value,
      deadline: document.getElementById("taskDeadline").value,
      deskripsi: document.getElementById("taskDescription").value.trim(),
      prioritas: document.getElementById("taskPriority").value,
      status: document.getElementById("taskStatus").value,
    };

    try {
      if (editingTaskId) {
        await apiRequest(`/api/tasks/${editingTaskId}`, { method: "PUT", body: payload });
        resetTaskForm();
        showAlert(alertBox, "Task updated successfully.", "success");
      } else {
        await apiRequest("/api/tasks", { method: "POST", body: payload });
        resetTaskForm();
        showAlert(alertBox, "Task created successfully.", "success");
      }
      await fetchTasks();
    } catch (err) {
      showAlert(alertBox, err.message, "error");
    }
  });
});
