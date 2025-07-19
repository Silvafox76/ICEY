const API_BASE_URL = 
  '/api';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('access_token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
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
    
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    
    return response;
  }

  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser() {
    return this.request("/auth/me");
  }

  async logout() {
    this.setToken(null);
  }

  // Inventory
  async getInventory(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/inventory${queryString ? `?${queryString}` : ''}`);
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

  // Jobs
  async getJobs(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/jobs${queryString ? `?${queryString}` : ''}`);
  }

  async getJob(id) {
    return this.request(`/jobs/${id}`);
  }

  async createJob(jobData) {
    return this.request('/jobs', {
      method: 'POST',
      body: JSON.stringify(jobData),
    });
  }

  async updateJob(id, jobData) {
    return this.request(`/jobs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(jobData),
    });
  }

  async deleteJob(id) {
    return this.request(`/jobs/${id}`, {
      method: 'DELETE',
    });
  }

  async getJobAssignments(id) {
    return this.request(`/jobs/${id}/assignments');
  }

  async getDashboardStats() {
    return this.request('/jobs/dashboard');
  }

  // Reports
  async getInventoryUsageReport(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/reports/inventory-usage${queryString ? `?${queryString}` : ''}`);
  }

  async getJobSummaryReport(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/reports/job-summary${queryString ? `?${queryString}` : ''}`);
  }

  async getInventoryStatusReport(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/reports/inventory-status${queryString ? `?${queryString}` : ''}`);
  }

  async getOverdueItemsReport() {
    return this.request('/reports/overdue-items');
  }

  // Users
  async getUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/users${queryString ? `?${queryString}` : ''}`);
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


