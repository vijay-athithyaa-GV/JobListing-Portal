/**
 * Employer Dashboard
 * Employer-specific functionality
 */

const EmployerDashboard = {
  jobs: [],
  jobCounts: {},
  /**
   * Initialize employer dashboard
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
    await this.loadJobListings();
    await this.loadRecentApplications();
  },

  /**
   * Load job listings (placeholder)
   */
  async loadJobListings() {
    const jobsContainer = document.getElementById('jobListingsTable');
    if (!jobsContainer) return;

    try {
      jobsContainer.innerHTML = `
        <tr>
          <td colspan="5" class="empty-state-cell">
            <div class="empty-state">
              <div class="empty-state-icon">💼</div>
              <div class="empty-state-title">Loading jobs…</div>
            </div>
          </td>
        </tr>
      `;
      const user = DashboardBase.currentUser || (await Auth.getCurrentUser());
      if (!user) return;

      const res = await Auth.apiCall(`/jobs?employerId=${user.id}`, { method: 'GET' });
      const jobs = await res.json();
      this.jobs = Array.isArray(jobs) ? jobs : [];

      // Per-job application counts for this employer
      try {
        const countsRes = await Auth.apiCall('/applications/employer/job-counts', { method: 'GET' });
        this.jobCounts = (await countsRes.json()) || {};
      } catch (e) {
        this.jobCounts = {};
      }

      if (this.jobs.length === 0) {
        jobsContainer.innerHTML = `
          <tr>
            <td colspan="5" class="empty-state-cell">
              <div class="empty-state">
                <div class="empty-state-icon">💼</div>
                <div class="empty-state-title">No job listings yet</div>
                <div class="empty-state-text">Create your first job posting to get started!</div>
              </div>
            </td>
          </tr>
        `;
        this.updateKPIs();
        return;
      }

      // Render jobs table
      jobsContainer.innerHTML = this.jobs
        .map(
          (job) => `
        <tr>
          <td><strong>${job.jobTitle}</strong></td>
          <td>${(this.jobCounts && this.jobCounts[String(job.jobId)]) ? this.jobCounts[String(job.jobId)] : (job.applicationsCount ?? 0)}</td>
          <td>${this.getStatusBadge(job.status)}</td>
          <td>${DashboardBase.formatDate(job.createdAt)}</td>
          <td>
            <div class="action-buttons">
              <button class="btn btn-sm btn-secondary" onclick="EmployerDashboard.editJob(${job.jobId})">
                Edit
              </button>
              <button class="btn btn-sm btn-secondary" onclick="EmployerDashboard.closeJob(${job.jobId})">
                Close Job
              </button>
              <button class="btn btn-sm btn-danger" onclick="EmployerDashboard.deleteJob(${job.jobId})">
                Delete
              </button>
            </div>
          </td>
        </tr>
      `
        )
        .join('');

      this.updateKPIs();
    } catch (error) {
      console.error('Error loading job listings:', error);
      DashboardBase.showError('Failed to load job listings', jobsContainer);
    }
  },

  /**
   * Load recent applications (placeholder)
   */
  async loadRecentApplications() {
    const applicationsContainer = document.getElementById('recentApplicationsTable');
    if (!applicationsContainer) return;

    try {
      applicationsContainer.innerHTML = `
        <tr>
          <td colspan="5" class="empty-state-cell">
            <div class="empty-state">
              <div class="empty-state-icon">📄</div>
              <div class="empty-state-title">Loading applications…</div>
            </div>
          </td>
        </tr>
      `;

      const res = await Auth.apiCall('/applications/employer/recent?limit=5', { method: 'GET' });
      const applications = await res.json();

      if (applications.length === 0) {
        applicationsContainer.innerHTML = `
          <tr>
            <td colspan="5" class="empty-state-cell">
              <div class="empty-state">
                <div class="empty-state-icon">📄</div>
                <div class="empty-state-title">No applications yet</div>
                <div class="empty-state-text">Applications will appear here once candidates apply to your jobs.</div>
              </div>
            </td>
          </tr>
        `;
        return;
      }

      // Render applications table
      applicationsContainer.innerHTML = applications
        .map(
          (app) => `
        <tr>
          <td><strong>${app.candidateName}</strong></td>
          <td>${app.jobTitle}</td>
          <td>${this.getStatusBadge(app.status)}</td>
          <td>${DashboardBase.formatDate(app.appliedAt)}</td>
          <td>
            <button class="btn btn-sm btn-primary" onclick="EmployerDashboard.viewApplication(${app.applicationId})">
              Review
            </button>
          </td>
        </tr>
      `
        )
        .join('');
    } catch (error) {
      console.error('Error loading recent applications:', error);
      DashboardBase.showError('Failed to load applications', applicationsContainer);
    }
  },

  /**
   * Update KPI cards
   */
  updateKPIs() {
    const totalJobs = Array.isArray(this.jobs) ? this.jobs.length : 0;
    const activeJobs = Array.isArray(this.jobs)
      ? this.jobs.filter((j) => (j.status || '').toLowerCase() === 'active').length
      : 0;

    // Update KPI values
    const totalJobsEl = document.getElementById('kpiTotalJobs');
    if (totalJobsEl) totalJobsEl.textContent = totalJobs;

    const activeJobsEl = document.getElementById('kpiActiveJobs');
    if (activeJobsEl) activeJobsEl.textContent = activeJobs;

    // Employer application summary
    Auth.apiCall('/applications/employer/summary', { method: 'GET' })
      .then((res) => res.json())
      .then((summary) => {
        const totalApplications = summary?.total ?? 0;
        const pendingApplications = summary?.pending ?? 0;

        const totalAppsEl = document.getElementById('kpiTotalApplications');
        if (totalAppsEl) totalAppsEl.textContent = totalApplications;

        const pendingAppsEl = document.getElementById('kpiPendingApplications');
        if (pendingAppsEl) pendingAppsEl.textContent = pendingApplications;
      })
      .catch(() => {
        // keep existing values on error
      });
  },

  /**
   * Get status badge HTML
   */
  getStatusBadge(status) {
    const badges = {
      active: '<span class="badge badge-success">Active</span>',
      draft: '<span class="badge badge-neutral">Draft</span>',
      closed: '<span class="badge badge-error">Closed</span>',
      pending: '<span class="badge badge-warning">Pending</span>',
      accepted: '<span class="badge badge-success">Accepted</span>',
      rejected: '<span class="badge badge-error">Rejected</span>',
    };
    return badges[status] || '<span class="badge badge-neutral">Unknown</span>';
  },

  /**
   * View job details
   */
  viewJob(jobId) {
    // TODO: Implement job detail view
    console.log('View job:', jobId);
    alert('Job detail view coming soon!');
  },

  /**
   * Edit job
   */
  editJob(jobId) {
    window.location.href = `/jobs/post?id=${jobId}`;
  },

  async closeJob(jobId) {
    if (!confirm('Close this job?')) return;

    try {
      await Auth.apiCall(`/jobs/${jobId}`, {
        method: 'PUT',
        body: JSON.stringify({ status: 'closed' }),
      });
      DashboardBase.showSuccess('Job closed successfully', document.querySelector('.dashboard-content'));
      await this.loadJobListings();
    } catch (error) {
      console.error('Error closing job:', error);
      DashboardBase.showError(error.message || 'Failed to close job', document.querySelector('.dashboard-content'));
    }
  },

  /**
   * Delete job
   */
  async deleteJob(jobId) {
    if (!confirm('Are you sure you want to delete this job listing?')) {
      return;
    }

    try {
      await Auth.apiCall(`/jobs/${jobId}`, { method: 'DELETE' });
      DashboardBase.showSuccess('Job deleted successfully', document.querySelector('.dashboard-content'));
      await this.loadJobListings();
    } catch (error) {
      console.error('Error deleting job:', error);
      DashboardBase.showError(error.message || 'Failed to delete job', document.querySelector('.dashboard-content'));
    }
  },

  /**
   * View application details
   */
  viewApplication(applicationId) {
    window.location.href = `/applications/review?id=${applicationId}`;
  },
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('/employer')) {
      EmployerDashboard.init();
    }
  });
} else {
  if (window.location.pathname.includes('/employer')) {
    EmployerDashboard.init();
  }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
  window.EmployerDashboard = EmployerDashboard;
}

