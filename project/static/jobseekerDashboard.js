/**
 * Job Seeker Dashboard
 * Job seeker-specific functionality
 */

const JobseekerDashboard = {
  /**
   * Initialize job seeker dashboard
   */
  async init() {
    // Initialize base dashboard first
    await DashboardBase.init();

    // Load dashboard data
    await this.loadDashboardData();
  },

  /**
   * Load dashboard data
   */
  async loadDashboardData() {
    // TODO: Replace with actual API calls when backend is ready
    this.loadAppliedJobs();
    this.loadNotifications();
    this.updateKPIs();
  },

  /**
   * Load applied jobs (placeholder)
   */
  async loadAppliedJobs() {
    // TODO: Fetch from API endpoint like /api/jobseeker/applications
    const appliedJobsContainer = document.getElementById('appliedJobsTable');
    if (!appliedJobsContainer) return;

    try {
      // Placeholder data structure
      const applications = [
        // Example structure:
        // {
        //   id: 1,
        //   job_title: "Senior Software Engineer",
        //   company: "Tech Corp",
        //   status: "pending",
        //   applied_date: "2024-01-15T10:00:00Z"
        // }
      ];

      if (applications.length === 0) {
        appliedJobsContainer.innerHTML = `
          <tr>
            <td colspan="5" class="empty-state-cell">
              <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <div class="empty-state-title">No applications yet</div>
                <div class="empty-state-text">Start browsing jobs to apply!</div>
              </div>
            </td>
          </tr>
        `;
        return;
      }

      // Render applications table
      appliedJobsContainer.innerHTML = applications
        .map(
          (app) => `
        <tr>
          <td><strong>${app.job_title}</strong></td>
          <td>${app.company}</td>
          <td>${this.getStatusBadge(app.status)}</td>
          <td>${DashboardBase.formatDate(app.applied_date)}</td>
          <td>
            <button class="btn btn-sm btn-secondary" onclick="JobseekerDashboard.viewApplication(${app.id})">
              View
            </button>
          </td>
        </tr>
      `
        )
        .join('');
    } catch (error) {
      console.error('Error loading applied jobs:', error);
      DashboardBase.showError('Failed to load applications', appliedJobsContainer);
    }
  },

  /**
   * Load notifications (placeholder)
   */
  async loadNotifications() {
    // TODO: Fetch from API endpoint like /api/jobseeker/notifications
    const notificationsContainer = document.getElementById('notificationsList');
    if (!notificationsContainer) return;

    // Placeholder - show empty state
    notificationsContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔔</div>
        <div class="empty-state-title">No new notifications</div>
        <div class="empty-state-text">You're all caught up!</div>
      </div>
    `;
  },

  /**
   * Update KPI cards
   */
  updateKPIs() {
    // TODO: Fetch real data from API
    const totalApplications = 0;
    const pendingApplications = 0;
    const acceptedApplications = 0;
    const rejectedApplications = 0;

    // Update KPI values
    const totalEl = document.getElementById('kpiTotalApplications');
    if (totalEl) totalEl.textContent = totalApplications;

    const pendingEl = document.getElementById('kpiPendingApplications');
    if (pendingEl) pendingEl.textContent = pendingApplications;

    const acceptedEl = document.getElementById('kpiAcceptedApplications');
    if (acceptedEl) acceptedEl.textContent = acceptedApplications;

    const rejectedEl = document.getElementById('kpiRejectedApplications');
    if (rejectedEl) rejectedEl.textContent = rejectedApplications;
  },

  /**
   * Get status badge HTML
   */
  getStatusBadge(status) {
    const badges = {
      pending: '<span class="badge badge-warning">Pending</span>',
      accepted: '<span class="badge badge-success">Accepted</span>',
      rejected: '<span class="badge badge-error">Rejected</span>',
      interviewing: '<span class="badge badge-info">Interviewing</span>',
    };
    return badges[status] || '<span class="badge badge-neutral">Unknown</span>';
  },

  /**
   * View application details
   */
  viewApplication(applicationId) {
    // TODO: Implement application detail view
    console.log('View application:', applicationId);
    alert('Application detail view coming soon!');
  },
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('/jobseeker')) {
      JobseekerDashboard.init();
    }
  });
} else {
  if (window.location.pathname.includes('/jobseeker')) {
    JobseekerDashboard.init();
  }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
  window.JobseekerDashboard = JobseekerDashboard;
}

