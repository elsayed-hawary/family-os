const API_BASE = window.location.origin;

class API {
    constructor() {
        this.token = localStorage.getItem('token');
    }
    
    async request(endpoint, method = 'GET', data = null) {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        const options = {
            method,
            headers,
            credentials: 'include'
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, options);
            const result = await response.json();
            
            // Don't logout on login/register endpoints
            if (response.status === 401 && 
                endpoint !== '/api/auth/login' && 
                endpoint !== '/api/auth/register' &&
                !endpoint.includes('/join/')) {
                this.logout();
                if (!window.location.pathname.includes('/login') && 
                    !window.location.pathname.includes('/register') &&
                    !window.location.pathname.includes('/join')) {
                    window.location.href = '/login.html';
                }
            }
            
            return result;
        } catch (error) {
            console.error('API Error:', error);
            return { success: false, message: 'Connection error' };
        }
    }
    
    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }
    
    logout() {
        this.token = null;
        localStorage.removeItem('token');
    }
    
    // Auth
    async register(data) {
        return this.request('/api/auth/register', 'POST', data);
    }
    
    async login(identifier, password) {
        return this.request('/api/auth/login', 'POST', { identifier, password });
    }
    
    async getCurrentUser() {
        return this.request('/api/auth/me');
    }
    
    async getJoinInfo(familyCode) {
        return this.request(`/api/auth/join/${familyCode}`);
    }
    
    async joinFamily(familyCode, data) {
        return this.request(`/api/auth/join/${familyCode}`, 'POST', data);
    }
    
    // Tasks
    async getTasks() {
        return this.request('/api/tasks');
    }
    
    async createTask(data) {
        return this.request('/api/tasks', 'POST', data);
    }
    
    async updateTask(taskId, data) {
        return this.request(`/api/tasks/${taskId}`, 'PUT', data);
    }
    
    async deleteTask(taskId) {
        return this.request(`/api/tasks/${taskId}`, 'DELETE');
    }
    
    // Expenses
    async getExpenses() {
        return this.request('/api/expenses');
    }
    
    async createExpense(data) {
        return this.request('/api/expenses', 'POST', data);
    }
    
    async deleteExpense(expenseId) {
        return this.request(`/api/expenses/${expenseId}`, 'DELETE');
    }
    
    // Events
    async getEvents() {
        return this.request('/api/events');
    }
    
    async createEvent(data) {
        return this.request('/api/events', 'POST', data);
    }
    
    async deleteEvent(eventId) {
        return this.request(`/api/events/${eventId}`, 'DELETE');
    }
    
    // Children
    async getChildren() {
        return this.request('/api/children');
    }
    
    async createChild(data) {
        return this.request('/api/children', 'POST', data);
    }
    
    async updateChild(childId, data) {
        return this.request(`/api/children/${childId}`, 'PUT', data);
    }
    
    async deleteChild(childId) {
        return this.request(`/api/children/${childId}`, 'DELETE');
    }
    
    // Child Tasks
    async getChildTasks(childId) {
        return this.request(`/api/children/${childId}/tasks`);
    }
    
    async createChildTask(childId, data) {
        return this.request(`/api/children/${childId}/tasks`, 'POST', data);
    }
    
    async completeChildTask(taskId) {
        return this.request(`/api/children/tasks/${taskId}/complete`, 'POST');
    }
    
    // Rewards
    async getRewards(childId) {
        return this.request(`/api/children/${childId}/rewards`);
    }
    
    async createReward(childId, data) {
        return this.request(`/api/children/${childId}/rewards`, 'POST', data);
    }
    
    async claimReward(rewardId) {
        return this.request(`/api/children/rewards/${rewardId}/claim`, 'POST');
    }
    
    // Notifications
    async getNotifications() {
        return this.request('/api/notifications');
    }
    
    async markNotificationRead(notificationId) {
        return this.request(`/api/notifications/${notificationId}/read`, 'POST');
    }
    
    async getUnreadCount() {
        return this.request('/api/notifications/unread/count');
    }
    
    // Settings
    async getSettings() {
        return this.request('/api/settings');
    }
    
    async updateSettings(data) {
        return this.request('/api/settings', 'PUT', data);
    }
    
    async updateSectionsVisibility(data) {
        return this.request('/api/settings/sections', 'PUT', data);
    }
}

const api = new API();