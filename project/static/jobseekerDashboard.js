/**
 * Job Seeker Dashboard
 * Job seeker-specific functionality
 */

const JobseekerDashboard = {
  summary: { total: 0, pending: 0, accepted: 0, rejected: 0 },
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
    await this.loadAppliedJobs();
    this.loadNotifications();
  },

  /**
   * Load applied jobs (placeholder)
   */
  async loadAppliedJobs() {
    const appliedJobsContainer = document.getElementById('appliedJobsTable');
    if (!appliedJobsContainer) return;

    try {
      appliedJobsContainer.innerHTML = `
        <tr>
          <td colspan="5" class="empty-state-cell">
            <div class="empty-state">
              <div class="empty-state-icon">📋</div>
              <div class="empty-state-title">Loading applications…</div>
            </div>
          </td>
        </tr>
      `;
      const res = await Auth.apiCall('/applications/me', { method: 'GET' });
      const data = await res.json();
      const applications = data && Array.isArray(data.applications) ? data.applications : [];
      this.summary = data && data.summary ? data.summary : this.summary;

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
        this.updateKPIs();
        return;
      }

      // Render applications table
      appliedJobsContainer.innerHTML = applications
        .map(
          (app) => `
        <tr>
          <td><strong>${app.jobTitle}</strong></td>
          <td>${app.companyName || ''}</td>
          <td>${this.getStatusBadge(app.status)}</td>
          <td>${DashboardBase.formatDate(app.appliedAt)}</td>
          <td>
            <button class="btn btn-sm btn-secondary" onclick="JobseekerDashboard.viewApplication(${app.applicationId})">
              View
            </button>
          </td>
        </tr>
      `
        )
        .join('');

      this.updateKPIs();
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
    const totalApplications = this.summary?.total ?? 0;
    const pendingApplications = this.summary?.pending ?? 0;
    const acceptedApplications = this.summary?.accepted ?? 0;
    const rejectedApplications = this.summary?.rejected ?? 0;

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

