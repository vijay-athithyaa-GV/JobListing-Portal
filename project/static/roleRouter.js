/**
 * Role-Based Router
 * Handles role-based routing and redirects
 */

const RoleRouter = {
  /**
   * Route user to appropriate dashboard based on role
   */
  async routeToDashboard() {
    const user = await Auth.getCurrentUser();
    
    if (!user) {
      window.location.href = '/login';
      return;
    }

    const role = user.role;
    const currentPath = window.location.pathname;

    // Map roles to dashboard paths
    const roleDashboards = {
      job_seeker: '/dashboard/jobseeker',
      employer: '/dashboard/employer',
    };

    const expectedPath = roleDashboards[role];

    // Redirect if on wrong dashboard
    if (currentPath !== expectedPath && currentPath.startsWith('/dashboard')) {
      window.location.href = expectedPath;
      return;
    }

    return user;
  },

  /**
   * Check if user has required role
   */
  async requireRole(allowedRoles) {
    const user = await Auth.getCurrentUser();
    
    if (!user) {
      window.location.href = '/login';
      return false;
    }

    if (!allowedRoles.includes(user.role)) {
      // Redirect to their correct dashboard
      await this.routeToDashboard();
      return false;
    }

    return true;
  },

  /**
   * Initialize router
   */
  async init() {
    // Ensure user is routed to correct dashboard
    await this.routeToDashboard();
  },
};

// Export for use in other modules
if (typeof window !== 'undefined') {
  window.RoleRouter = RoleRouter;
}

