// dashboard statistics, completion progress, and upcoming deadlines logic

import { apiRequest, escapeHtml, renderDeadlineCell, statusBadgeClass } from "./api.js";
import { initAppLayout } from "./layout.js";

async function loadDashboard() {
  const data = await apiRequest("/api/dashboard");
  const { stats, upcoming_deadlines: upcoming, entity_summary: summary } = data;

  document.getElementById("kpiTotal").textContent = stats.total_tasks;
  document.getElementById("kpiTodo").textContent = stats.todo;
  document.getElementById("kpiInProgress").textContent = stats.in_progress;
  document.getElementById("kpiCompleted").textContent = stats.completed;
  document.getElementById("kpiOverdue").textContent = stats.overdue;

  const alertBadge = document.getElementById("kpiOverdueBadge");
  if (alertBadge) {
    alertBadge.style.display = stats.overdue > 0 ? "inline-flex" : "none";
  }

  document.getElementById("completionPercent").textContent = `${stats.completion_rate}%`;
  document.getElementById("completionFill").style.width = `${stats.completion_rate}%`;
  document.getElementById("completionCaption").textContent =
    `${stats.completed} of ${stats.total_tasks} tasks completed`;

  const tbody = document.getElementById("upcomingBody");
  if (upcoming.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="empty-state">All tasks are completed.</td></tr>';
  } else {
    tbody.innerHTML = upcoming
      .map((item) => `
        <tr>
          <td class="cell-strong">${escapeHtml(item.judul)}</td>
          <td class="cell-muted">${escapeHtml(item.course_name)}</td>
          <td>${renderDeadlineCell(item.deadline, item.deadline_status)}</td>
          <td><span class="badge ${statusBadgeClass(item.status)}">${escapeHtml(item.status)}</span></td>
        </tr>
      `)
      .join("");
  }

  document.getElementById("sumStudentsTitle").textContent = `Students: ${summary.total_students} records`;
  document.getElementById("sumStudentsDesc").textContent = `${summary.active_students} students with active tasks`;

  document.getElementById("sumCoursesTitle").textContent = `Courses: ${summary.total_courses} courses`;
  document.getElementById("sumCoursesDesc").textContent = `${summary.total_sks} total credit hours (SKS)`;

  document.getElementById("sumTasksTitle").textContent = `Unfinished Tasks: ${summary.unfinished_tasks} tasks`;
  document.getElementById("sumTasksDesc").textContent =
    `${summary.overdue} overdue · ${summary.due_today} due today`;
}

document.addEventListener("DOMContentLoaded", async () => {
  const user = await initAppLayout("dashboard");
  if (!user) return;
  await loadDashboard();
});
