/**
 * Dashboard Base Functionality
 * Common dashboard features: sidebar, navbar, user menu
 */

const DashboardBase = {
  currentUser: null,

  /**
   * Initialize dashboard
   */
  async init() {
    // Load current user
    this.currentUser = await Auth.getCurrentUser();
    
    if (!this.currentUser) {
      window.location.href = '/login';
      return;
    }

    // Initialize components
    this.initUserMenu();
    this.initSidebar();
    this.updateUserInfo();
  },

  /**
   * Initialize user menu dropdown
   */
  initUserMenu() {
    const userMenu = document.querySelector('.user-menu');
    const trigger = document.querySelector('.user-menu-trigger');
    const dropdown = document.querySelector('.user-menu-dropdown');

    if (!userMenu || !trigger || !dropdown) return;

    // Toggle dropdown
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      userMenu.classList.toggle('active');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (!userMenu.contains(e.target)) {
        userMenu.classList.remove('active');
      }
    });

    // Handle logout
    const logoutBtn = dropdown.querySelector('.user-menu-item.logout');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', async () => {
        await Auth.logout();
      });
    }
  },

  /**
   * Initialize sidebar
   */
  initSidebar() {
    const sidebar = document.querySelector('.dashboard-sidebar');
    const toggleBtn = document.querySelector('.sidebar-toggle');

    if (!sidebar) return;

    // Mobile toggle
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
      });
    }

    // Close sidebar on mobile when clicking outside
    if (window.innerWidth <= 1024) {
      document.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target) && !e.target.closest('.sidebar-toggle')) {
          sidebar.classList.remove('open');
        }
      });
    }

    // Handle window resize
    window.addEventListener('resize', () => {
      if (window.innerWidth > 1024) {
        sidebar.classList.remove('open');
      }
    });

    // Mark active menu item
    this.setActiveMenuItem();
  },

  /**
   * Set active menu item based on current page
   */
  setActiveMenuItem() {
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.sidebar-menu-link');

    menuLinks.forEach((link) => {
      const href = link.getAttribute('href');
      if (href && currentPath.includes(href.split('/').pop())) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  },

  /**
   * Update user info in navbar
   */
  updateUserInfo() {
    if (!this.currentUser) return;

    // Update avatar
    const avatar = document.querySelector('.user-avatar');
    if (avatar) {
      const initials = this.currentUser.email.charAt(0).toUpperCase();
      avatar.textContent = initials;
    }

    // Update email
    const emailEl = document.querySelector('.user-email');
    if (emailEl) {
      emailEl.textContent = this.currentUser.email;
    }

    // Update welcome message
    const welcomeName = document.querySelector('.welcome-name');
    if (welcomeName) {
      const name = this.currentUser.email.split('@')[0];
      welcomeName.textContent = `, ${name}`;
    }
  },

  /**
   * Format date
   */
  formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  },

  /**
   * Format date time
   */
  formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  },

  /**
   * Show loading state
   */
  showLoading(element) {
    if (!element) return;
    element.innerHTML = '<div class="loading"></div>';
    element.classList.add('loading-container');
  },

  /**
   * Hide loading state
   */
  hideLoading(element) {
    if (!element) return;
    element.classList.remove('loading-container');
  },

  /**
   * Show error message
   */
  showError(message, container) {
    if (!container) return;
    container.innerHTML = `
      <div class="alert alert-error">
        <span>${message}</span>
      </div>
    `;
  },

  /**
   * Show success message
   */
  showSuccess(message, container) {
    if (!container) return;
    container.innerHTML = `
      <div class="alert alert-success">
        <span>${message}</span>
      </div>
    `;
    // Auto-hide after 3 seconds
    setTimeout(() => {
      container.innerHTML = '';
    }, 3000);
  },
};

// Export for use in other modules
if (typeof window !== 'undefined') {
  window.DashboardBase = DashboardBase;
}

