/**
 * Auth state management, modal handlers, and session checking.
 */

const Auth = {
  currentUser: null,

  async init() {
    try {
      const res = await API.getCurrentUser();
      this.currentUser = res.user || null;
      this.updateUI();
    } catch (err) {
      this.currentUser = null;
      this.updateUI();
    }
  },

  isLoggedIn() {
    return !!this.currentUser;
  },

  isAdmin() {
    return this.currentUser && this.currentUser.role === "admin";
  },

  updateUI() {
    const authActions = document.getElementById("nav-auth-actions");
    const userMenu = document.getElementById("nav-user-menu");
    const adminLink = document.getElementById("nav-admin-link");

    if (adminLink) {
      if (this.isAdmin()) {
        adminLink.style.display = "inline-flex";
      } else {
        adminLink.style.display = "none";
      }
    }

    if (!authActions || !userMenu) return;

    if (this.currentUser) {
      authActions.style.display = "none";
      userMenu.style.display = "flex";

      const nameEl = document.getElementById("nav-user-name");
      const roleBadge = document.getElementById("nav-user-role");
      const avatarEl = document.getElementById("nav-user-avatar");

      if (nameEl) nameEl.textContent = this.currentUser.name;
      if (roleBadge) {
        roleBadge.textContent = this.currentUser.role.toUpperCase();
        roleBadge.className = `btn-sm ${this.currentUser.role === "admin" ? "btn-danger" : "btn-outline"}`;
      }
      if (avatarEl) {
        avatarEl.textContent = (this.currentUser.name || "U")[0].toUpperCase();
      }
    } else {
      authActions.style.display = "flex";
      userMenu.style.display = "none";
    }

    // Notify other components
    window.dispatchEvent(new CustomEvent("auth-state-changed", { detail: this.currentUser }));
  },

  showLoginModal() {
    const modal = document.getElementById("login-modal");
    if (modal) modal.classList.add("active");
  },

  hideLoginModal() {
    const modal = document.getElementById("login-modal");
    if (modal) modal.classList.remove("active");
  },

  showRegisterModal() {
    const modal = document.getElementById("register-modal");
    if (modal) modal.classList.add("active");
  },

  hideRegisterModal() {
    const modal = document.getElementById("register-modal");
    if (modal) modal.classList.remove("active");
  },

  async handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    const errorEl = document.getElementById("login-error");

    if (errorEl) errorEl.style.display = "none";

    try {
      const res = await API.login(email, password);
      this.currentUser = res.user;
      this.hideLoginModal();
      this.updateUI();
      showToast(res.message || "Welcome back!", "success");

      // Reset form
      event.target.reset();
    } catch (err) {
      if (errorEl) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
      } else {
        showToast(err.message, "error");
      }
    }
  },

  async handleRegister(event) {
    event.preventDefault();
    const errorEl = document.getElementById("register-error");
    if (errorEl) errorEl.style.display = "none";

    const name = document.getElementById("reg-name").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    const rollNumber = document.getElementById("reg-roll").value.trim();
    const department = document.getElementById("reg-dept").value;
    const semester = document.getElementById("reg-sem").value;

    try {
      const res = await API.register({
        name,
        email,
        password,
        roll_number: rollNumber,
        department,
        semester,
        role: "student",
      });

      this.currentUser = res.user;
      this.hideRegisterModal();
      this.updateUI();
      showToast("Student account created successfully! Welcome aboard.", "success");
      event.target.reset();
    } catch (err) {
      if (errorEl) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
      } else {
        showToast(err.message, "error");
      }
    }
  },

  async handleLogout() {
    try {
      await API.logout();
      this.currentUser = null;
      this.updateUI();
      showToast("Logged out successfully.", "info");
      // If on admin page and not admin anymore, redirect to home
      if (window.location.pathname.includes("admin")) {
        window.location.href = "/";
      }
    } catch (err) {
      showToast(err.message, "error");
    }
  },
};

window.Auth = Auth;
