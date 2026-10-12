/**
 * Admin Dashboard - Analytics, Charts, Event CRUD, and Attendee Management.
 */

// Toast Helper
function showToast(message, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  let icon = type === "success" ? "✅" : type === "error" ? "⚠️" : "ℹ️";
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

const Admin = {
  events: [],
  editingEventId: null,
  categoryChart: null,
  popularityChart: null,

  async init() {
    this.initTheme();
    await Auth.init();

    if (!Auth.isAdmin()) {
      this.showAdminLoginPrompt();
      return;
    }

    this.bindEvents();
    await this.loadDashboardData();
  },

  initTheme() {
    const savedTheme = localStorage.getItem("cems-theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
    const toggleBtn = document.getElementById("theme-toggle");
    if (toggleBtn) {
      toggleBtn.innerHTML = savedTheme === "dark" ? "☀️" : "🌙";
      toggleBtn.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") || "light";
        const next = current === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("cems-theme", next);
        toggleBtn.innerHTML = next === "dark" ? "☀️" : "🌙";
        // Re-render charts for dark/light palette
        this.renderCategoryChart();
      });
    }
  },

  showAdminLoginPrompt() {
    const gateEl = document.getElementById("admin-auth-gate");
    const mainEl = document.getElementById("admin-main-content");
    if (gateEl) gateEl.style.display = "flex";
    if (mainEl) mainEl.style.display = "none";
  },

  showMainDashboard() {
    const gateEl = document.getElementById("admin-auth-gate");
    const mainEl = document.getElementById("admin-main-content");
    if (gateEl) gateEl.style.display = "none";
    if (mainEl) mainEl.style.display = "block";
  },

  async handleAdminLogin(event) {
    event.preventDefault();
    const email = document.getElementById("admin-gate-email").value.trim();
    const password = document.getElementById("admin-gate-password").value;
    const errorEl = document.getElementById("admin-gate-error");

    if (errorEl) errorEl.style.display = "none";

    try {
      const res = await API.login(email, password);
      if (res.user.role !== "admin") {
        throw new Error("This account does not have administrator privileges.");
      }
      Auth.currentUser = res.user;
      Auth.updateUI();
      this.showMainDashboard();
      this.bindEvents();
      await this.loadDashboardData();
      showToast("Welcome to Admin Dashboard!", "success");
    } catch (err) {
      if (errorEl) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
      } else {
        showToast(err.message, "error");
      }
    }
  },

  bindEvents() {
    const eventForm = document.getElementById("event-form");
    if (eventForm) {
      eventForm.addEventListener("submit", (e) => this.handleEventFormSubmit(e));
    }

    const tableSearch = document.getElementById("admin-table-search");
    if (tableSearch) {
      tableSearch.addEventListener("input", (e) => {
        const val = e.target.value.toLowerCase().trim();
        this.filterTableRows(val);
      });
    }
  },

  async loadDashboardData() {
    this.showMainDashboard();
    await Promise.all([
      this.loadMetricsAndCharts(),
      this.loadEventsTable(),
    ]);
  },

  async loadMetricsAndCharts() {
    try {
      const data = await API.getStatsSummary();
      const m = data.metrics || {};

      document.getElementById("stat-total-events").textContent = m.total_events || 0;
      document.getElementById("stat-upcoming-events").textContent = m.upcoming_events || 0;
      document.getElementById("stat-total-students").textContent = m.total_students || 0;
      document.getElementById("stat-total-registrations").textContent = m.total_registrations || 0;

      this.renderCategoryChart(data.category_breakdown || []);
      this.renderPopularityChart(data.popular_events || []);
    } catch (err) {
      console.error("Stats Error:", err);
      showToast("Failed to load statistics summary: " + err.message, "error");
    }
  },

  renderCategoryChart(breakdown = []) {
    const canvas = document.getElementById("categoryChart");
    if (!canvas) return;

    const labels = breakdown.map((b) => b.category);
    const dataCounts = breakdown.map((b) => b.registration_count);
    const backgroundColors = ["#2563eb", "#db2777", "#059669", "#d97706"];

    if (window.Chart) {
      if (this.categoryChart) this.categoryChart.destroy();
      this.categoryChart = new Chart(canvas, {
        type: "doughnut",
        data: {
          labels: labels,
          datasets: [
            {
              data: dataCounts,
              backgroundColor: backgroundColors,
              borderWidth: 2,
              borderColor: document.documentElement.getAttribute("data-theme") === "dark" ? "#1f2937" : "#ffffff",
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "bottom",
              labels: {
                color: document.documentElement.getAttribute("data-theme") === "dark" ? "#f9fafb" : "#0f172a",
                boxWidth: 12,
                font: { size: 12 },
              },
            },
          },
        },
      });
    } else {
      // Native SVG / HTML Bar visualization fallback
      this.renderFallbackCategoryList(canvas.parentElement, breakdown);
    }
  },

  renderFallbackCategoryList(container, breakdown) {
    const total = breakdown.reduce((acc, curr) => acc + curr.registration_count, 0) || 1;
    container.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 1rem; padding: 1rem 0;">
        ${breakdown.map((b) => {
          const pct = Math.round((b.registration_count / total) * 100);
          return `
            <div>
              <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.35rem; font-weight: 600;">
                <span>${b.category} (${b.event_count} Events)</span>
                <span>${b.registration_count} Registrations (${pct}%)</span>
              </div>
              <div style="height: 10px; background: var(--bg-input); border-radius: var(--radius-full); overflow: hidden;">
                <div style="height: 100%; width: ${pct}%; background: var(--cat-${b.category === 'Technical' ? 'tech' : b.category === 'Cultural' ? 'cultural' : b.category === 'Sports' ? 'sports' : 'workshop'});"></div>
              </div>
            </div>
          `;
        }).join("")}
      </div>
    `;
  },

  renderPopularityChart(popular = []) {
    const canvas = document.getElementById("popularityChart");
    if (!canvas) return;

    const labels = popular.map((p) => p.title.length > 20 ? p.title.substring(0, 20) + "..." : p.title);
    const dataCounts = popular.map((p) => p.registration_count);

    if (window.Chart) {
      if (this.popularityChart) this.popularityChart.destroy();
      this.popularityChart = new Chart(canvas, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Registrations",
              data: dataCounts,
              backgroundColor: "#4f46e5",
              borderRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1, color: document.documentElement.getAttribute("data-theme") === "dark" ? "#9ca3af" : "#64748b" },
              grid: { color: document.documentElement.getAttribute("data-theme") === "dark" ? "#374151" : "#e2e8f0" },
            },
            x: {
              ticks: { color: document.documentElement.getAttribute("data-theme") === "dark" ? "#9ca3af" : "#64748b" },
              grid: { display: false },
            },
          },
          plugins: {
            legend: { display: false },
          },
        },
      });
    }
  },

  async loadEventsTable() {
    const tbody = document.getElementById("events-table-body");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2rem;">Loading events...</td></tr>`;

    try {
      const data = await API.getEvents({ sort: "date_asc" });
      this.events = data.events || [];
      this.renderTableRows(this.events);
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--danger); padding: 2rem;">Error: ${err.message}</td></tr>`;
    }
  },

  renderTableRows(eventsList) {
    const tbody = document.getElementById("events-table-body");
    if (!tbody) return;

    if (eventsList.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">No events found. Click "Create Event" to add one!</td></tr>`;
      return;
    }

    tbody.innerHTML = eventsList
      .map(
        (ev) => `
        <tr data-id="${ev.id}">
          <td style="font-weight: 600;">${ev.title}</td>
          <td><span class="event-category-badge cat-${ev.category}" style="position: static; font-size: 0.72rem; padding: 0.2rem 0.5rem;">${ev.category}</span></td>
          <td>${ev.event_date} <span style="font-size: 0.78rem; color: var(--text-muted);">${ev.event_time}</span></td>
          <td style="color: var(--text-muted);">${ev.venue}</td>
          <td>
            <strong>${ev.registered_count}</strong> / ${ev.capacity}
            <span style="font-size: 0.75rem; color: ${ev.spots_left <= 5 ? 'var(--danger)' : 'var(--text-muted)'};">(${ev.spots_left} left)</span>
          </td>
          <td>
            <div style="display: flex; gap: 0.4rem;">
              <button class="btn btn-outline btn-sm" onclick="Admin.viewAttendees(${ev.id})" title="View Registered Students">
                👥 Attendees (${ev.registered_count})
              </button>
              <button class="btn btn-outline btn-sm" onclick="Admin.openEditEventModal(${ev.id})" title="Edit Event">
                ✏️ Edit
              </button>
              <button class="btn btn-danger btn-sm" onclick="Admin.deleteEvent(${ev.id})" title="Delete Event">
                🗑️
              </button>
            </div>
          </td>
        </tr>
      `
      )
      .join("");
  },

  filterTableRows(searchTerm) {
    if (!searchTerm) {
      this.renderTableRows(this.events);
      return;
    }
    const filtered = this.events.filter(
      (ev) =>
        ev.title.toLowerCase().includes(searchTerm) ||
        ev.category.toLowerCase().includes(searchTerm) ||
        ev.venue.toLowerCase().includes(searchTerm)
    );
    this.renderTableRows(filtered);
  },

  openCreateEventModal() {
    this.editingEventId = null;
    document.getElementById("event-modal-title").textContent = "Create New College Event";
    const form = document.getElementById("event-form");
    if (form) form.reset();
    document.getElementById("event-error").style.display = "none";
    document.getElementById("event-modal").classList.add("active");
  },

  openEditEventModal(eventId) {
    const ev = this.events.find((e) => e.id === eventId);
    if (!ev) return;

    this.editingEventId = eventId;
    document.getElementById("event-modal-title").textContent = "Edit College Event";
    document.getElementById("event-error").style.display = "none";

    document.getElementById("ev-title").value = ev.title || "";
    document.getElementById("ev-category").value = ev.category || "Technical";
    document.getElementById("ev-desc").value = ev.description || "";
    document.getElementById("ev-date").value = ev.event_date || "";
    document.getElementById("ev-time").value = ev.event_time || "";
    document.getElementById("ev-venue").value = ev.venue || "";
    document.getElementById("ev-capacity").value = ev.capacity || 50;
    document.getElementById("ev-deadline").value = ev.registration_deadline || "";
    document.getElementById("ev-contact").value = ev.organizer_contact || "";
    document.getElementById("ev-banner").value = ev.banner_url || "";

    document.getElementById("event-modal").classList.add("active");
  },

  closeEventModal() {
    document.getElementById("event-modal").classList.remove("active");
  },

  async handleEventFormSubmit(event) {
    event.preventDefault();
    const errorEl = document.getElementById("event-error");
    if (errorEl) errorEl.style.display = "none";

    const payload = {
      title: document.getElementById("ev-title").value.trim(),
      category: document.getElementById("ev-category").value,
      description: document.getElementById("ev-desc").value.trim(),
      event_date: document.getElementById("ev-date").value,
      event_time: document.getElementById("ev-time").value,
      venue: document.getElementById("ev-venue").value.trim(),
      capacity: parseInt(document.getElementById("ev-capacity").value, 10),
      registration_deadline: document.getElementById("ev-deadline").value || null,
      organizer_contact: document.getElementById("ev-contact").value.trim(),
      banner_url: document.getElementById("ev-banner").value.trim(),
    };

    try {
      if (this.editingEventId) {
        await API.updateEvent(this.editingEventId, payload);
        showToast("Event updated successfully!", "success");
      } else {
        await API.createEvent(payload);
        showToast("Event created successfully!", "success");
      }
      this.closeEventModal();
      await this.loadDashboardData();
    } catch (err) {
      if (errorEl) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
      } else {
        showToast(err.message, "error");
      }
    }
  },

  async deleteEvent(eventId) {
    const ev = this.events.find((e) => e.id === eventId);
    const title = ev ? ev.title : "this event";
    if (confirm(`Are you sure you want to permanently delete "${title}"? All student registrations for this event will also be removed.`)) {
      try {
        await API.deleteEvent(eventId);
        showToast(`Event deleted successfully.`, "info");
        await this.loadDashboardData();
      } catch (err) {
        showToast(err.message, "error");
      }
    }
  },

  async viewAttendees(eventId) {
    const modal = document.getElementById("attendees-modal");
    const titleEl = document.getElementById("attendees-event-title");
    const countEl = document.getElementById("attendees-count-badge");
    const bodyEl = document.getElementById("attendees-list-body");

    if (bodyEl) bodyEl.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 2rem;">Loading registered students...</td></tr>`;
    if (modal) modal.classList.add("active");

    try {
      const data = await API.getEventAttendees(eventId);
      if (titleEl) titleEl.textContent = data.event_title;
      if (countEl) countEl.textContent = `${data.total_registered} / ${data.capacity} Registered`;

      const students = data.students || [];
      if (students.length === 0) {
        bodyEl.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">No students have registered for this event yet.</td></tr>`;
        return;
      }

      bodyEl.innerHTML = students
        .map(
          (s, idx) => `
          <tr>
            <td>${idx + 1}</td>
            <td style="font-weight: 600;">${s.name}</td>
            <td><code>${s.roll_number || 'N/A'}</code></td>
            <td>${s.department || 'N/A'} <span style="font-size: 0.78rem; color: var(--text-muted);">(${s.semester || 'N/A'})</span></td>
            <td><a href="mailto:${s.email}" style="color: var(--primary);">${s.email}</a></td>
          </tr>
        `
        )
        .join("");
    } catch (err) {
      if (bodyEl) {
        bodyEl.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--danger); padding: 2rem;">Error: ${err.message}</td></tr>`;
      }
    }
  },

  closeAttendeesModal() {
    document.getElementById("attendees-modal").classList.remove("active");
  },

  printAttendance() {
    window.print();
  },
};

window.Admin = Admin;

document.addEventListener("DOMContentLoaded", () => {
  Admin.init();
});
