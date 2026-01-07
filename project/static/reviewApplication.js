/**
 * Employer Review Application Page
 */

const ReviewApplication = {
  applicationId: null,
  detail: null,

  async init() {
    await DashboardBase.init();

    const meta = document.getElementById('reviewMeta');
    const rawId = meta ? meta.getAttribute('data-application-id') : null;
    const parsed = rawId ? Number(rawId) : NaN;

    // fallback to querystring if needed
    if (!Number.isFinite(parsed)) {
      const qs = new URLSearchParams(window.location.search);
      const qid = qs.get('id');
      const qn = qid ? Number(qid) : NaN;
      this.applicationId = Number.isFinite(qn) ? qn : null;
    } else {
      this.applicationId = parsed;
    }

    const backBtn = document.getElementById('backToDashboard');
    if (backBtn) {
      backBtn.addEventListener('click', () => {
        window.location.href = '/dashboard/employer#applications';
      });
    }

    const acceptBtn = document.getElementById('acceptBtn');
    if (acceptBtn) acceptBtn.addEventListener('click', () => this.updateStatus('accepted'));

    const rejectBtn = document.getElementById('rejectBtn');
    if (rejectBtn) rejectBtn.addEventListener('click', () => this.updateStatus('rejected'));

    await this.load();
  },

  async load() {
    const alerts = document.getElementById('reviewAlerts');
    if (alerts) alerts.innerHTML = '';

    const tbody = document.getElementById('reviewTable');
    if (!tbody) return;

    if (!this.applicationId) {
      DashboardBase.showError('Missing application id', alerts);
      return;
    }

    try {
      const res = await Auth.apiCall(`/applications/employer/${this.applicationId}`, { method: 'GET' });
      const detail = await res.json();
      this.detail = detail;

      const candidate = detail.candidate || {};
      const rows = [
        ['Candidate', candidate.name || ''],
        ['Email', candidate.email || ''],
        ['Phone', candidate.phone || ''],
        ['Skills', candidate.skills || ''],
        ['Resume', candidate.resumeUrl ? `<a href="${candidate.resumeUrl}" target="_blank">View PDF</a>` : ''],
        ['Job Title', detail.jobTitle || ''],
        ['Status', this.renderStatus(detail.status)],
        ['Applied', DashboardBase.formatDate(detail.appliedAt)],
      ];

      tbody.innerHTML = rows
        .map(
          ([k, v]) => `
        <tr>
          <td><strong>${k}</strong></td>
          <td>${v || ''}</td>
        </tr>
      `
        )
        .join('');
    } catch (error) {
      console.error('Error loading application:', error);
      DashboardBase.showError(error.message || 'Failed to load application', alerts);
      tbody.innerHTML = `
        <tr>
          <td colspan="2" class="empty-state-cell">
            <div class="empty-state">
              <div class="empty-state-icon">📄</div>
              <div class="empty-state-title">Unable to load application</div>
            </div>
          </td>
        </tr>
      `;
    }
  },

  renderStatus(status) {
    const s = (status || '').toLowerCase();
    const map = {
      pending: '<span class="badge badge-warning">Pending</span>',
      accepted: '<span class="badge badge-success">Accepted</span>',
      rejected: '<span class="badge badge-error">Rejected</span>',
    };
    return map[s] || '<span class="badge badge-neutral">Unknown</span>';
  },

  async updateStatus(next) {
    const alerts = document.getElementById('reviewAlerts');
    if (alerts) alerts.innerHTML = '';

    if (!this.applicationId) return;
    if (!confirm(`Mark this application as ${next}?`)) return;

    const acceptBtn = document.getElementById('acceptBtn');
    const rejectBtn = document.getElementById('rejectBtn');
    const disableAll = (v) => {
      if (acceptBtn) acceptBtn.disabled = v;
      if (rejectBtn) rejectBtn.disabled = v;
    };

    disableAll(true);

    try {
      await Auth.apiCall(`/applications/employer/${this.applicationId}`, {
        method: 'PUT',
        body: JSON.stringify({ status: next }),
      });
      DashboardBase.showSuccess('Application updated successfully.', alerts);
      await this.load();
    } catch (error) {
      console.error('Error updating application:', error);
      DashboardBase.showError(error.message || 'Failed to update application', alerts);
    } finally {
      disableAll(false);
    }
  },
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname === '/applications/review') {
      ReviewApplication.init();
    }
  });
} else {
  if (window.location.pathname === '/applications/review') {
    ReviewApplication.init();
  }
}

if (typeof window !== 'undefined') {
  window.ReviewApplication = ReviewApplication;
}


