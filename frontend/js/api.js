/**
 * API Client for College Event Management System
 * Wraps Fetch API with JSON headers, credentials, and error handling.
 */

const API = {
  async request(endpoint, options = {}) {
    const defaultHeaders = {
      "Content-Type": "application/json",
      "Accept": "application/json",
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {}),
      },
    };

    try {
      const response = await fetch(endpoint, config);
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorMsg = data.error || data.message || `Request failed with status ${response.status}`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  // Auth Endpoints
  login(email, password) {
    return this.request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  register(userData) {
    return this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  },

  logout() {
    return this.request("/api/auth/logout", {
      method: "POST",
    });
  },

  getCurrentUser() {
    return this.request("/api/auth/me");
  },

  // Events Endpoints
  getEvents(params = {}) {
    const query = new URLSearchParams();
    if (params.search) query.append("search", params.search);
    if (params.category && params.category !== "All") query.append("category", params.category);
    if (params.status) query.append("status", params.status);
    if (params.sort) query.append("sort", params.sort);

    const qs = query.toString();
    return this.request(`/api/events${qs ? "?" + qs : ""}`);
  },

  getEvent(id) {
    return this.request(`/api/events/${id}`);
  },

  createEvent(eventData) {
    return this.request("/api/events", {
      method: "POST",
      body: JSON.stringify(eventData),
    });
  },

  updateEvent(id, eventData) {
    return this.request(`/api/events/${id}`, {
      method: "PUT",
      body: JSON.stringify(eventData),
    });
  },

  deleteEvent(id) {
    return this.request(`/api/events/${id}`, {
      method: "DELETE",
    });
  },

  // Registration Endpoints
  registerForEvent(eventId) {
    return this.request(`/api/events/${eventId}/register`, {
      method: "POST",
    });
  },

  unregisterFromEvent(eventId) {
    return this.request(`/api/events/${eventId}/unregister`, {
      method: "POST",
    });
  },

  getMyRegistrations() {
    return this.request("/api/my-registrations");
  },

  getEventAttendees(eventId) {
    return this.request(`/api/events/${eventId}/registrations`);
  },

  // Stats Endpoints
  getStatsSummary() {
    return this.request("/api/stats/summary");
  },
};

window.API = API;
