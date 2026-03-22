class FamilyApp {
    constructor() {
        this.currentUser = null;
        this.currentFamily = null;
        this.tasks = [];
        this.expenses = [];
        this.events = [];
        this.children = [];
        this.notifications = [];
        this.eventSource = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        this.init();
    }
    
    async init() {
        const token = localStorage.getItem('token');
        const publicPages = ['/login.html', '/register.html', '/join.html'];
        const isPublicPage = publicPages.includes(window.location.pathname) || 
                            window.location.pathname.includes('/join/');
        
        if (token && !isPublicPage) {
            await this.loadCurrentUser();
            if (this.currentUser) {
                this.loadDashboardData();
                this.connectSSE();
            } else {
                window.location.href = '/login.html';
            }
        }
    }
    
    async loadCurrentUser() {
        const result = await api.getCurrentUser();
        if (result.success) {
            this.currentUser = result.user;
            document.getElementById('userName')?.innerText = this.currentUser.fullName;
            document.getElementById('userRole')?.innerText = `Роль: ${this.currentUser.role}`;
            if (this.currentUser.isFamilyHead) {
                const badge = document.getElementById('userBadge');
                if (badge) badge.innerText = '👑 Глава семьи';
            }
        }
        return result.success;
    }
    
    async loadDashboardData() {
        await Promise.all([
            this.loadTasks(),
            this.loadExpenses(),
            this.loadEvents(),
            this.loadChildren(),
            this.loadNotifications()
        ]);
        
        this.updateStats();
        this.renderTasks();
        this.renderExpenses();
        this.renderEvents();
        this.renderChildren();
    }
    
    async loadTasks() {
        const result = await api.getTasks();
        if (result.success) {
            this.tasks = result.tasks;
        }
    }
    
    async loadExpenses() {
        const result = await api.getExpenses();
        if (result.success) {
            this.expenses = result.expenses;
        }
    }
    
    async loadEvents() {
        const result = await api.getEvents();
        if (result.success) {
            this.events = result.events;
        }
    }
    
    async loadChildren() {
        const result = await api.getChildren();
        if (result.success) {
            this.children = result.children;
        }
    }
    
    async loadNotifications() {
        const result = await api.getNotifications();
        if (result.success) {
            this.notifications = result.notifications;
            this.updateNotificationBadge();
        }
    }
    
    updateStats() {
        const pendingTasks = this.tasks.filter(t => t.status !== 'completed').length;
        const totalExpenses = this.expenses.reduce((sum, e) => sum + e.amount, 0);
        const upcomingEvents = this.events.filter(e => new Date(e.date) > new Date()).length;
        
        document.getElementById('pendingTasksCount')?.innerText = pendingTasks;
        document.getElementById('totalExpenses')?.innerText = totalExpenses;
        document.getElementById('upcomingEvents')?.innerText = upcomingEvents;
        document.getElementById('childrenCount')?.innerText = this.children.length;
    }
    
    updateNotificationBadge() {
        const unreadCount = this.notifications.filter(n => !n.read).length;
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            if (unreadCount > 0) {
                badge.style.display = 'flex';
                badge.innerText = unreadCount > 99 ? '99+' : unreadCount;
            } else {
                badge.style.display = 'none';
            }
        }
    }
    
    renderTasks() {
        const container = document.getElementById('tasksList');
        if (!container) return;
        
        const pendingTasks = this.tasks.filter(t => t.status !== 'completed').slice(0, 5);
        
        if (pendingTasks.length === 0) {
            container.innerHTML = '<div style="text-align:center; padding: 20px; color:#8e8e93;">Нет задач</div>';
            return;
        }
        
        container.innerHTML = pendingTasks.map(task => `
            <div class="task-item">
                <div class="task-info">
                    <div class="task-title">${this.escapeHtml(task.title)}</div>
                    <div class="task-assignee"><i class="fas fa-user"></i> ${task.assigneeName || 'Не назначен'}</div>
                </div>
                <button class="complete-btn" onclick="app.completeTask(${task.id})">Выполнено</button>
            </div>
        `).join('');
    }
    
    async completeTask(taskId) {
        const result = await api.updateTask(taskId, { status: 'completed' });
        if (result.success) {
            await this.loadTasks();
            this.renderTasks();
            this.updateStats();
            this.showToast('✅ Задача выполнена', 'Отлично!');
        }
    }
    
    renderExpenses() {
        const container = document.getElementById('expensesList');
        if (!container) return;
        
        const recentExpenses = this.expenses.slice(0, 5);
        
        if (recentExpenses.length === 0) {
            container.innerHTML = '<div style="text-align:center; padding: 20px; color:#8e8e93;">Нет расходов</div>';
            return;
        }
        
        container.innerHTML = recentExpenses.map(exp => `
            <div class="expense-item">
                <div class="expense-info">
                    <div class="expense-desc">${this.escapeHtml(exp.description)}</div>
                    <div class="expense-amount">${exp.amount} ₽ - ${exp.category}</div>
                </div>
                <button class="delete-expense" onclick="app.deleteExpense(${exp.id})"><i class="fas fa-trash-alt"></i></button>
            </div>
        `).join('');
    }
    
    async deleteExpense(expenseId) {
        if (!confirm('Удалить расход?')) return;
        const result = await api.deleteExpense(expenseId);
        if (result.success) {
            await this.loadExpenses();
            this.renderExpenses();
            this.updateStats();
        }
    }
    
    renderEvents() {
        const container = document.getElementById('eventsList');
        if (!container) return;
        
        const upcomingEvents = this.events
            .filter(e => new Date(e.date) > new Date())
            .sort((a, b) => new Date(a.date) - new Date(b.date))
            .slice(0, 5);
        
        if (upcomingEvents.length === 0) {
            container.innerHTML = '<div style="text-align:center; padding: 20px; color:#8e8e93;">Нет предстоящих событий</div>';
            return;
        }
        
        container.innerHTML = upcomingEvents.map(event => {
            const eventDate = new Date(event.date);
            const daysRemaining = Math.ceil((eventDate - new Date()) / (1000 * 60 * 60 * 24));
            return `
                <div class="event-item" style="border-right: 4px solid ${event.color || '#667eea'}">
                    <div class="event-info">
                        <div class="event-title">${this.escapeHtml(event.title)}</div>
                        <div class="event-date">${eventDate.toLocaleDateString()} • ${daysRemaining} дн</div>
                    </div>
                    <button class="delete-event" onclick="app.deleteEvent(${event.id})"><i class="fas fa-trash-alt"></i></button>
                </div>
            `;
        }).join('');
    }
    
    async deleteEvent(eventId) {
        if (!confirm('Удалить событие?')) return;
        const result = await api.deleteEvent(eventId);
        if (result.success) {
            await this.loadEvents();
            this.renderEvents();
        }
    }
    
    renderChildren() {
        const container = document.getElementById('childrenList');
        if (!container) return;
        
        if (this.children.length === 0) {
            container.innerHTML = '<div style="text-align:center; padding: 20px; color:#8e8e93;">Нет детей</div>';
            return;
        }
        
        container.innerHTML = this.children.map(child => `
            <div class="member-item">
                <div class="member-avatar">
                    <i class="fas fa-child"></i>
                </div>
                <div class="member-info">
                    <div class="member-name">${this.escapeHtml(child.name)}</div>
                    <div class="member-role">${child.age || '?'} лет • ${child.totalPoints || 0} очков</div>
                </div>
                <button class="small-btn" onclick="app.viewChild(${child.id})">Подробнее</button>
            </div>
        `).join('');
    }
    
    viewChild(childId) {
        window.location.href = `/children.html?id=${childId}`;
    }
    
    connectSSE() {
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        const token = localStorage.getItem('token');
        if (!token) return;
        
        const url = `/api/events/stream?token=${encodeURIComponent(token)}`;
        this.eventSource = new EventSource(url);
        
        this.eventSource.onmessage = (event) => {
            try {
                const notification = JSON.parse(event.data);
                this.notifications.unshift(notification);
                this.updateNotificationBadge();
                this.showToast(notification.title, notification.message);
            } catch (e) {
                console.error('SSE parse error:', e);
            }
        };
        
        this.eventSource.onerror = () => {
            console.error('SSE connection error');
            this.eventSource.close();
            
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                setTimeout(() => this.connectSSE(), 5000 * this.reconnectAttempts);
            }
        };
        
        this.eventSource.onopen = () => {
            this.reconnectAttempts = 0;
            console.log('SSE connected');
        };
    }
    
    showToast(title, message) {
        // Remove existing toast
        const existing = document.querySelector('.toast-notification');
        if (existing) existing.remove();
        
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.innerHTML = `
            <strong>${this.escapeHtml(title)}</strong>
            <p>${this.escapeHtml(message)}</p>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    openSideMenu() {
        document.getElementById('sideMenu')?.classList.add('open');
        document.getElementById('sideMenuOverlay')?.classList.add('active');
    }
    
    closeSideMenu() {
        document.getElementById('sideMenu')?.classList.remove('open');
        document.getElementById('sideMenuOverlay')?.classList.remove('active');
    }
    
    logout() {
        if (confirm('Вы уверены, что хотите выйти?')) {
            api.logout();
            if (this.eventSource) this.eventSource.close();
            window.location.href = '/login.html';
        }
    }
}

const app = new FamilyApp();
