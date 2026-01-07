/**
 * Browse Jobs Page (Job Seeker)
 * Fetches ACTIVE jobs from Job Listing service and supports Apply flow.
 */

const BrowseJobs = {
  async init() {
    await DashboardBase.init();
    await this.loadJobs();
  },

  setLoading() {
    const tbody = document.getElementById('browseJobsTable');
    if (!tbody) return;
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="empty-state-cell">
          <div class="empty-state">
            <div class="empty-state-icon">💼</div>
            <div class="empty-state-title">Loading jobs…</div>
          </div>
        </td>
      </tr>
    `;
  },

  setEmpty() {
    const tbody = document.getElementById('browseJobsTable');
    if (!tbody) return;
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="empty-state-cell">
          <div class="empty-state">
            <div class="empty-state-icon">💼</div>
            <div class="empty-state-title">No active jobs found</div>
            <div class="empty-state-text">Please check back later.</div>
          </div>
        </td>
      </tr>
    `;
  },

  async loadJobs() {
    const alerts = document.getElementById('browseJobsAlerts');
    if (alerts) alerts.innerHTML = '';

    this.setLoading();

    try {
      const res = await Auth.apiCall('/jobs?status=ACTIVE', { method: 'GET' });
      const jobs = await res.json();

      const tbody = document.getElementById('browseJobsTable');
      if (!tbody) return;

      if (!jobs || jobs.length === 0) {
        this.setEmpty();
        return;
      }

      tbody.innerHTML = jobs
        .map(
          (job) => `
        <tr>
          <td><strong>${job.jobTitle}</strong></td>
          <td>${job.companyName || ''}</td>
          <td>${job.location || ''}</td>
          <td>${job.jobType || ''}</td>
          <td>${job.salaryRange || ''}</td>
          <td>${DashboardBase.formatDate(job.createdAt)}</td>
          <td>
            <button class="btn btn-sm btn-primary" onclick="BrowseJobs.apply(${job.jobId})">Apply</button>
          </td>
        </tr>
      `
        )
        .join('');
    } catch (error) {
      console.error('Error loading jobs:', error);
      DashboardBase.showError(error.message || 'Failed to load jobs', alerts);
      this.setEmpty();
    }
  },

  async apply(jobId) {
    const alerts = document.getElementById('browseJobsAlerts');
    if (alerts) alerts.innerHTML = '';

    // Native confirm uses browser modal without introducing new UI components/styles.
    if (!confirm('Apply to this job?')) return;

    try {
      await Auth.apiCall('/applications', {
        method: 'POST',
        body: JSON.stringify({ jobId }),
      });

      DashboardBase.showSuccess('Application submitted. Redirecting…', alerts);
      setTimeout(() => (window.location.href = '/dashboard/jobseeker#applications'), 700);
    } catch (error) {
      console.error('Error applying:', error);
      DashboardBase.showError(error.message || 'Failed to apply', alerts);
    }
  },
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname === '/jobs/browse') {
      BrowseJobs.init();
    }
  });
} else {
  if (window.location.pathname === '/jobs/browse') {
    BrowseJobs.init();
  }
}

if (typeof window !== 'undefined') {
  window.BrowseJobs = BrowseJobs;
}


