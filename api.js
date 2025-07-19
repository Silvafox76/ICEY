const API_BASE_URL = 
  process.env.NODE_ENV === 'production' 
    ? '/api' 
    : 'http://localhost:5000/api';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('access_token');
  }

  setToken(token) {
    console.log("Setting token:", token);
    this.token = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
    console.log("Token set, this.token is now:", this.token);
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
      console.log("Adding Authorization header:", headers.Authorization);
    } else {
      console.log("No token available for Authorization header");
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (response.status === 401) {
        // Token expired or invalid
        this.setToken(null);
        window.location.href = '/login';
        return;
      }
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || "Request failed");
      }
      
      return data;
    } catch (error) {
      throw error;
    }
  }

  // Authentication
  async login(username, password) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    
    return response;
  }

  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser() {
    // Temporarily use non-JWT endpoint for testing
    return this.request("/auth/me-temp");
  }

  async logout() {
    this.setToken(null);
  }

  // Inventory
  async getInventory(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/inventory?${queryString}` : '/inventory';
    return this.request(endpoint);
  }

  async getInventoryItem(id) {
    return this.request(`/inventory/${id}`);
  }

  async createInventoryItem(itemData) {
    return this.request('/inventory', {
      method: 'POST',
      body: JSON.stringify(itemData),
    });
  }

  async updateInventoryItem(id, itemData) {
    return this.request(`/inventory/${id}`, {
      method: 'PUT',
      body: JSON.stringify(itemData),
    });
  }

  async deleteInventoryItem(id) {
    return this.request(`/inventory/${id}`, {
      method: 'DELETE',
    });
  }

  async checkOutItem(id, checkoutData) {
    return this.request(`/inventory/${id}/check-out`, {
      method: 'POST',
      body: JSON.stringify(checkoutData),
    });
  }

  async checkInItem(id, checkinData) {
    return this.request(`/inventory/${id}/check-in`, {
      method: 'POST',
      body: JSON.stringify(checkinData),
    });
  }

  async getCategories() {
    return this.request('/inventory/categories');
  }

  // Jobs API
  async getJobs(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/jobs${queryString ? `?${queryString}` : ""}`);
  }

  async getJob(id) {
    return this.request(`/jobs/${id}`);
  }

  async createJob(jobData) {
    return this.request("/jobs", {
      method: "POST",
      body: JSON.stringify(jobData),
    });
  }

  async updateJob(id, jobData) {
    return this.request(`/jobs/${id}`, {
      method: "PUT",
      body: JSON.stringify(jobData),
    });
  }

  async deleteJob(id) {
    return this.request(`/jobs/${id}`, {
      method: "DELETE",
    });
  }

  async getJobAssignments(id) {
    return this.request(`/jobs/${id}/assignments`);
  }

  async getDashboardStats() {
    // Temporarily use non-JWT endpoint for testing
    return this.request("/jobs/dashboard-temp");
  }

  // Reports
  async getInventoryUsageReport(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/reports/inventory-usage?${queryString}` : '/reports/inventory-usage';
    return this.request(endpoint);
  }

  async getJobSummaryReport(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/reports/job-summary?${queryString}` : '/reports/job-summary';
    return this.request(endpoint);
  }

  async getInventoryStatusReport(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/reports/inventory-status?${queryString}` : '/reports/inventory-status';
    return this.request(endpoint);
  }

  async getOverdueItemsReport() {
    // Temporarily use non-JWT endpoint for testing
    return this.request('/reports/overdue-items-temp');
  }

  // Users
  async getUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/users?${queryString}` : '/users';
    return this.request(endpoint);
  }

  async getUser(id) {
    return this.request(`/users/${id}`);
  }

  async createUser(userData) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async updateUser(id, userData) {
    return this.request(`/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async deleteUser(id) {
    return this.request(`/users/${id}`, {
      method: 'DELETE',
    });
  }
}

export const apiClient = new ApiClient();

