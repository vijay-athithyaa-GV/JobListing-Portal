/**
 * Authentication Utilities
 * Centralized authentication and API communication
 */

const Auth = {
  /**
   * Get current user from API
   */
  async getCurrentUser() {
    try {
      const response = await fetch('/auth/me', {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          return null;
        }
        throw new Error('Failed to fetch user');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching current user:', error);
      return null;
    }
  },

  /**
   * Check if user is authenticated
   */
  async isAuthenticated() {
    const user = await this.getCurrentUser();
    return user !== null;
  },

  /**
   * Get user role
   */
  async getUserRole() {
    const user = await this.getCurrentUser();
    return user ? user.role : null;
  },

  /**
   * Logout user
   */
  async logout() {
    try {
      await fetch('/auth/logout', {
        method: 'POST',
        credentials: 'same-origin',
      });
      window.location.href = '/login';
    } catch (error) {
      console.error('Error during logout:', error);
      window.location.href = '/login';
    }
  },

  /**
   * Protected API call with error handling
   */
  async apiCall(url, options = {}) {
    const defaultOptions = {
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    if (response.status === 401) {
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Request failed');
    }

    return response;
  },
};

// Export for use in other modules
if (typeof window !== 'undefined') {
  window.Auth = Auth;
}

// Utility functions for error handling
function show(el, message) {
  if (!el) return;
  el.textContent = message || '';
  el.classList.remove('hidden');
}

function hide(el) {
  if (!el) return;
  el.textContent = '';
  el.classList.add('hidden');
}

async function parseError(res) {
  try {
    const data = await res.json();
    if (data && typeof data.detail === 'string') return data.detail;
    return JSON.stringify(data);
  } catch {
    return await res.text();
  }
}

// Register flow
async function registerFlow() {
  const form = document.getElementById('registerForm');
  if (!form) return;

  const emailEl = document.getElementById('regEmail');
  const passwordEl = document.getElementById('regPassword');
  const roleEl = document.getElementById('regRole');
  const errEl = document.getElementById('registerError');
  const okEl = document.getElementById('registerSuccess');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hide(errEl);
    hide(okEl);

    const payload = {
      email: emailEl.value,
      password: passwordEl.value,
      role: roleEl.value,
    };

    const res = await fetch('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      show(errEl, await parseError(res));
      return;
    }

    show(okEl, 'Account created. Redirecting to login…');
    setTimeout(() => (window.location.href = '/login'), 650);
  });
}

// Login flow
async function loginFlow() {
  const form = document.getElementById('loginForm');
  if (!form) return;

  const emailEl = document.getElementById('loginEmail');
  const passwordEl = document.getElementById('loginPassword');
  const errEl = document.getElementById('loginError');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hide(errEl);

    const payload = {
      email: emailEl.value,
      password: passwordEl.value,
    };

    const res = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      show(errEl, await parseError(res));
      return;
    }

    // Get user role to redirect to correct dashboard
    const user = await Auth.getCurrentUser();
    if (user) {
      if (user.role === 'job_seeker') {
        window.location.href = '/dashboard/jobseeker';
      } else if (user.role === 'employer') {
        window.location.href = '/dashboard/employer';
      } else {
        window.location.href = '/dashboard';
      }
    } else {
      window.location.href = '/dashboard';
    }
  });
}

// Initialize flows if forms exist
registerFlow();
loginFlow();
