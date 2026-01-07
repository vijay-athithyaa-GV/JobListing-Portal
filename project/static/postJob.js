/**
 * Post Job Page
 * Uses existing dashboard patterns (Auth.apiCall + DashboardBase alerts).
 */

const PostJobPage = {
  jobId: null,

  async init() {
    await DashboardBase.init();

    const meta = document.getElementById('postJobMeta');
    const rawId = meta ? meta.getAttribute('data-job-id') : null;
    const parsed = rawId ? Number(rawId) : NaN;
    this.jobId = Number.isFinite(parsed) ? parsed : null;

    const cancelBtn = document.getElementById('cancelPostJob');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => {
        window.location.href = '/dashboard/employer#jobs';
      });
    }

    this.bindForm();

    if (this.jobId) {
      await this.loadJobForEdit(this.jobId);
    }
  },

  async loadJobForEdit(jobId) {
    const titleEl = document.getElementById('postJobTitle');
    if (titleEl) titleEl.textContent = 'Edit Job';

    try {
      const res = await Auth.apiCall(`/jobs/${jobId}`, { method: 'GET' });
      const job = await res.json();

      document.getElementById('jobTitle').value = job.jobTitle || '';
      document.getElementById('jobDescription').value = job.jobDescription || '';
      document.getElementById('qualifications').value = job.qualifications || '';
      document.getElementById('responsibilities').value = job.responsibilities || '';
      document.getElementById('jobType').value = job.jobType || '';
      document.getElementById('location').value = job.location || '';
      document.getElementById('salaryRange').value = job.salaryRange || '';

      const submitBtn = document.getElementById('submitPostJob');
      if (submitBtn) submitBtn.textContent = 'Update';
    } catch (error) {
      console.error('Error loading job:', error);
      DashboardBase.showError('Failed to load job details', document.getElementById('postJobAlerts'));
    }
  },

  bindForm() {
    const form = document.getElementById('postJobForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const alerts = document.getElementById('postJobAlerts');
      if (alerts) alerts.innerHTML = '';

      const submitBtn = document.getElementById('submitPostJob');
      const originalBtnHtml = submitBtn ? submitBtn.innerHTML : '';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span> Please wait';
      }

      const payload = {
        jobTitle: document.getElementById('jobTitle').value,
        jobDescription: document.getElementById('jobDescription').value,
        qualifications: document.getElementById('qualifications').value || null,
        responsibilities: document.getElementById('responsibilities').value || null,
        jobType: document.getElementById('jobType').value,
        location: document.getElementById('location').value,
        salaryRange: document.getElementById('salaryRange').value || null,
      };

      try {
        const isEdit = !!this.jobId;
        const url = isEdit ? `/jobs/${this.jobId}` : '/jobs';
        const method = isEdit ? 'PUT' : 'POST';

        await Auth.apiCall(url, {
          method,
          body: JSON.stringify(payload),
        });

        DashboardBase.showSuccess(
          isEdit ? 'Job updated successfully. Redirecting…' : 'Job posted successfully. Redirecting…',
          alerts
        );
        setTimeout(() => (window.location.href = '/dashboard/employer#jobs'), 700);
      } catch (error) {
        console.error('Error saving job:', error);
        DashboardBase.showError(error.message || 'Failed to save job', alerts);
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalBtnHtml;
        }
      }
    });
  },
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname === '/jobs/post') {
      PostJobPage.init();
    }
  });
} else {
  if (window.location.pathname === '/jobs/post') {
    PostJobPage.init();
  }
}

if (typeof window !== 'undefined') {
  window.PostJobPage = PostJobPage;
}


