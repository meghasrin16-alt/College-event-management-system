/**
 * Student Portal - Event Discovery, Search, Category Filter, and Registration Logic.
 */

// Global Toast Notification Helper
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
  
  let icon = "ℹ️";
  if (type === "success") icon = "✅";
  if (type === "error") icon = "⚠️";

  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

const App = {
  events: [],
  currentCategory: "All",
  searchQuery: "",
  currentStatus: "all",
  currentSort: "date_asc",
  selectedEvent: null,

  async init() {
    this.initTheme();
    this.bindEvents();
    await Auth.init();
    await this.loadEvents();

    window.addEventListener("auth-state-changed", () => {
      this.loadEvents();
    });
  },

  initTheme() {
    const savedTheme = localStorage.getItem("cems-theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
    this.updateThemeButton(savedTheme);

    const toggleBtn = document.getElementById("theme-toggle");
    if (toggleBtn) {
      toggleBtn.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") || "light";
        const next = current === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("cems-theme", next);
        this.updateThemeButton(next);
      });
    }
  },

  updateThemeButton(theme) {
    const toggleBtn = document.getElementById("theme-toggle");
    if (toggleBtn) {
      toggleBtn.innerHTML = theme === "dark" ? "☀️" : "🌙";
      toggleBtn.setAttribute("title", `Switch to ${theme === "dark" ? "light" : "dark"} mode`);
    }
  },

  bindEvents() {
    // Search input
    const searchInput = document.getElementById("search-input");
    if (searchInput) {
      let debounceTimer;
      searchInput.addEventListener("input", (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          this.searchQuery = e.target.value.trim();
          this.loadEvents();
        }, 250);
      });
    }

    // Category pills
    const pills = document.querySelectorAll(".cat-pill");
    pills.forEach((pill) => {
      pill.addEventListener("click", () => {
        pills.forEach((p) => p.classList.remove("active"));
        pill.classList.add("active");
        this.currentCategory = pill.getAttribute("data-category") || "All";
        this.loadEvents();
      });
    });

    // Status filter
    const statusSelect = document.getElementById("status-filter");
    if (statusSelect) {
      statusSelect.addEventListener("change", (e) => {
        this.currentStatus = e.target.value;
        this.loadEvents();
      });
    }

    // Sort filter
    const sortSelect = document.getElementById("sort-filter");
    if (sortSelect) {
      sortSelect.addEventListener("change", (e) => {
        this.currentSort = e.target.value;
        this.loadEvents();
      });
    }

    // Auth forms
    const loginForm = document.getElementById("login-form");
    if (loginForm) loginForm.addEventListener("submit", (e) => Auth.handleLogin(e));

    const registerForm = document.getElementById("register-form");
    if (registerForm) registerForm.addEventListener("submit", (e) => Auth.handleRegister(e));

    // Modal switchers
    const switchToReg = document.getElementById("switch-to-register");
    if (switchToReg) {
      switchToReg.addEventListener("click", (e) => {
        e.preventDefault();
        Auth.hideLoginModal();
        Auth.showRegisterModal();
      });
    }

    const switchToLogin = document.getElementById("switch-to-login");
    if (switchToLogin) {
      switchToLogin.addEventListener("click", (e) => {
        e.preventDefault();
        Auth.hideRegisterModal();
        Auth.showLoginModal();
      });
    }

    // My Registrations button
    const myRegsBtn = document.getElementById("btn-my-registrations");
    if (myRegsBtn) {
      myRegsBtn.addEventListener("click", () => this.showMyRegistrationsModal());
    }
  },

  async loadEvents() {
    const grid = document.getElementById("events-grid");
    const countBadge = document.getElementById("event-count-badge");
    if (grid) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted);">
          Loading events...
        </div>
      `;
    }

    try {
      const data = await API.getEvents({
        search: this.searchQuery,
        category: this.currentCategory,
        status: this.currentStatus,
        sort: this.currentSort,
      });

      this.events = data.events || [];
      if (countBadge) countBadge.textContent = `${this.events.length} Events`;
      this.renderEvents();
    } catch (err) {
      if (grid) {
        grid.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--danger);">
            Failed to load events: ${err.message}
          </div>
        `;
      }
    }
  },

  renderEvents() {
    const grid = document.getElementById("events-grid");
    if (!grid) return;

    if (this.events.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 1rem; color: var(--text-muted); background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px dashed var(--border-color);">
          <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">📅</div>
          <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.5rem;">No Events Found</h3>
          <p>Try adjusting your search criteria or switching to a different category filter.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = this.events
      .map((ev) => {
        const dateObj = new Date(ev.event_date + "T" + (ev.event_time || "00:00"));
        const dateFormatted = !isNaN(dateObj)
          ? dateObj.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
          : ev.event_date;
        
        const banner = ev.banner_url || "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80";
        const percentFilled = Math.min(100, Math.round((ev.registered_count / ev.capacity) * 100));

        // Action button states
        let actionBtn = "";
        if (ev.is_registered) {
          actionBtn = `
            <button class="btn btn-outline btn-sm" style="color: var(--success); border-color: var(--success);" onclick="App.showUnregisterConfirm(${ev.id})">
              ✓ Registered (Cancel)
            </button>
          `;
        } else if (ev.is_full) {
          actionBtn = `
            <button class="btn btn-outline btn-sm" disabled style="opacity: 0.6; cursor: not-allowed;">
              Sold Out
            </button>
          `;
        } else {
          actionBtn = `
            <button class="btn btn-primary btn-sm" onclick="App.handleRegisterClick(${ev.id})">
              Register Now
            </button>
          `;
        }

        return `
          <article class="event-card">
            <div class="event-card-media">
              <img src="${banner}" alt="${ev.title}" class="event-card-img" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80'" />
              <span class="event-category-badge cat-${ev.category}">${ev.category}</span>
              <div class="event-date-chip">📅 ${dateFormatted}</div>
            </div>
            
            <div class="event-card-body">
              <h3 class="event-card-title">${ev.title}</h3>
              <p class="event-card-desc">${ev.description}</p>
              
              <div class="event-meta-list">
                <div class="event-meta-item">
                  <span>⏰</span> <span>${ev.event_time}</span>
                </div>
                <div class="event-meta-item">
                  <span>📍</span> <span>${ev.venue}</span>
                </div>
              </div>

              <div class="event-capacity-info">
                <div class="capacity-labels">
                  <span>Spots Left: <strong style="color: ${ev.spots_left <= 5 ? 'var(--danger)' : 'var(--text-main)'};">${ev.spots_left}</strong></span>
                  <span>${ev.registered_count} / ${ev.capacity}</span>
                </div>
                <div class="capacity-progress-bar">
                  <div class="capacity-progress-fill ${ev.is_full ? 'full' : ''}" style="width: ${percentFilled}%;"></div>
                </div>
              </div>

              <div class="event-card-footer">
                <button class="btn btn-outline btn-sm" style="flex: 1;" onclick="App.openEventDetails(${ev.id})">
                  Details
                </button>
                <div style="flex: 1;">
                  ${actionBtn}
                </div>
              </div>
            </div>
          </article>
        `;
      })
      .join("");
  },

  async handleRegisterClick(eventId) {
    if (!Auth.isLoggedIn()) {
      showToast("Please log in as a student to register for events.", "info");
      Auth.showLoginModal();
      return;
    }

    if (Auth.currentUser.role !== "student") {
      showToast("Only student accounts can register for events.", "error");
      return;
    }

    try {
      const res = await API.registerForEvent(eventId);
      showToast(res.message || "Registered successfully!", "success");
      await this.loadEvents();
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async showUnregisterConfirm(eventId) {
    if (confirm("Are you sure you want to cancel your registration? Your spot will be made available for others.")) {
      try {
        const res = await API.unregisterFromEvent(eventId);
        showToast(res.message || "Registration cancelled.", "info");
        await this.loadEvents();
      } catch (err) {
        showToast(err.message, "error");
      }
    }
  },

  async openEventDetails(eventId) {
    try {
      const data = await API.getEvent(eventId);
      const ev = data.event;
      this.selectedEvent = ev;

      const modal = document.getElementById("details-modal");
      const titleEl = document.getElementById("details-title");
      const bodyEl = document.getElementById("details-body");
      const footerEl = document.getElementById("details-footer");

      if (titleEl) titleEl.textContent = ev.title;

      const dateObj = new Date(ev.event_date + "T" + (ev.event_time || "00:00"));
      const dateFormatted = !isNaN(dateObj)
        ? dateObj.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" })
        : ev.event_date;

      if (bodyEl) {
        bodyEl.innerHTML = `
          <div style="margin-bottom: 1.25rem; border-radius: var(--radius-md); overflow: hidden; max-height: 220px;">
            <img src="${ev.banner_url || 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80'}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80'"/>
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 1rem;">
            <span class="event-category-badge cat-${ev.category}">${ev.category}</span>
            <span style="font-size: 0.85rem; color: var(--text-muted);">Capacity: ${ev.capacity} Seats</span>
            <span style="font-size: 0.85rem; font-weight: 600; color: ${ev.spots_left <= 5 ? 'var(--danger)' : 'var(--success)'};">${ev.spots_left} Seats Remaining</span>
          </div>
          <p style="font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.5rem; color: var(--text-main);">${ev.description}</p>
          
          <div style="background: var(--bg-input); padding: 1rem; border-radius: var(--radius-md); display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.88rem;">
            <div>📅 <strong>Date:</strong> ${dateFormatted}</div>
            <div>⏰ <strong>Time:</strong> ${ev.event_time}</div>
            <div>📍 <strong>Venue:</strong> ${ev.venue}</div>
            ${ev.registration_deadline ? `<div>⏳ <strong>Registration Deadline:</strong> ${ev.registration_deadline}</div>` : ""}
            ${ev.organizer_contact ? `<div>📞 <strong>Organizer Contact:</strong> ${ev.organizer_contact}</div>` : ""}
          </div>
        `;
      }

      if (footerEl) {
        let actionBtn = "";
        if (ev.is_registered) {
          actionBtn = `<button class="btn btn-outline" style="color: var(--danger); border-color: var(--danger);" onclick="App.showUnregisterConfirm(${ev.id}); App.closeDetailsModal();">Cancel Registration</button>`;
        } else if (ev.is_full) {
          actionBtn = `<button class="btn btn-outline" disabled style="opacity: 0.6;">Event Full</button>`;
        } else {
          actionBtn = `<button class="btn btn-primary" onclick="App.handleRegisterClick(${ev.id}); App.closeDetailsModal();">Register For Event</button>`;
        }

        footerEl.innerHTML = `
          <button class="btn btn-outline" onclick="App.closeDetailsModal()">Close</button>
          ${actionBtn}
        `;
      }

      if (modal) modal.classList.add("active");
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  closeDetailsModal() {
    const modal = document.getElementById("details-modal");
    if (modal) modal.classList.remove("active");
  },

  async showMyRegistrationsModal() {
    if (!Auth.isLoggedIn()) {
      showToast("Please log in to view your registrations.", "info");
      Auth.showLoginModal();
      return;
    }

    const modal = document.getElementById("my-regs-modal");
    const listEl = document.getElementById("my-regs-list");

    if (!modal || !listEl) return;

    listEl.innerHTML = "<div style='text-align: center; padding: 2rem;'>Loading your registered events...</div>";
    modal.classList.add("active");

    try {
      const res = await API.getMyRegistrations();
      const regs = res.registrations || [];

      if (regs.length === 0) {
        listEl.innerHTML = `
          <div style="text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎟️</div>
            <h4>You haven't registered for any events yet.</h4>
            <p style="font-size: 0.85rem; margin-top: 0.25rem;">Explore upcoming events on the homepage and reserve your spot!</p>
          </div>
        `;
        return;
      }

      listEl.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 0.85rem;">
          ${regs.map((r) => `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; border: 1px solid var(--border-color); border-radius: var(--radius-md); background: var(--bg-card); gap: 1rem; flex-wrap: wrap;">
              <div>
                <span class="event-category-badge cat-${r.category}" style="position: static; font-size: 0.7rem; padding: 0.15rem 0.5rem;">${r.category}</span>
                <h4 style="font-weight: 700; margin: 0.35rem 0 0.2rem 0; font-size: 1rem;">${r.title}</h4>
                <div style="font-size: 0.8rem; color: var(--text-muted);">
                  📅 ${r.event_date} at ${r.event_time} &bull; 📍 ${r.venue}
                </div>
              </div>
              <div>
                <button class="btn btn-outline btn-sm" style="color: var(--danger); border-color: var(--danger);" onclick="App.showUnregisterConfirm(${r.event_id}); App.closeMyRegistrationsModal();">
                  Cancel Spot
                </button>
              </div>
            </div>
          `).join("")}
        </div>
      `;
    } catch (err) {
      listEl.innerHTML = `<div style="color: var(--danger); text-align: center; padding: 2rem;">Error: ${err.message}</div>`;
    }
  },

  closeMyRegistrationsModal() {
    const modal = document.getElementById("my-regs-modal");
    if (modal) modal.classList.remove("active");
  },
};

window.App = App;

// Bootstrap on DOM Content Loaded
document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
