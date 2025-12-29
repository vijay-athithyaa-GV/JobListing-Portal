# Testing Guide - Dashboard System

## 🚀 Quick Start Guide

### Step 1: Activate Virtual Environment

```powershell
# Make sure you're in the project root directory
cd "C:\Users\gvvij\OneDrive\Desktop\Job Portal"
.\.venv\Scripts\Activate.ps1
```

### Step 2: Set Environment Variables

If you don't have a `.env` file, create one or set environment variables in PowerShell:

```powershell
$env:DATABASE_URL="postgresql+asyncpg://postgres:yourpassword@localhost:5432/job_portal"
$env:SECRET_KEY="dev-secret-key-change-in-production"
$env:ACCESS_TOKEN_EXPIRE_MINUTES="60"
$env:COOKIE_SECURE="false"
```

**Note:** Replace `yourpassword` with your actual PostgreSQL password.

### Step 3: Start the Server

```powershell
cd project
uvicorn main:app --reload
```

Or from the project root:
```powershell
uvicorn project.main:app --reload
```

The server will start at: **http://127.0.0.1:8000**

---

## 🔄 Authentication Flow Explained

Yes, it goes **directly from authentication to the Dashboard**! Here's the complete flow:

### Flow Diagram:
```
1. User visits: http://127.0.0.1:8000/
   ↓
2. Redirects to: /dashboard
   ↓
3. Check: Is user authenticated?
   ├─ NO → Redirect to /login
   └─ YES → Redirect to role-specific dashboard
       ├─ job_seeker → /dashboard/jobseeker
       └─ employer → /dashboard/employer

4. User logs in at /login
   ↓
5. After successful login:
   - JWT token stored in HTTP-only cookie
   - Frontend fetches user role
   - Redirects to appropriate dashboard:
       ├─ job_seeker → /dashboard/jobseeker
       └─ employer → /dashboard/employer
```

---

## 🧪 Testing Steps

### Test 1: Register a Job Seeker Account

1. Open browser: http://127.0.0.1:8000
2. You'll be redirected to `/login` (since not authenticated)
3. Click "Register" link or go to: http://127.0.0.1:8000/register
4. Fill in the form:
   - **Email**: `jobseeker@test.com`
   - **Password**: `password123` (min 8 characters)
   - **Role**: Select "Job Seeker"
5. Click "Create account"
6. **Expected**: Success message → Auto-redirect to `/login`

### Test 2: Login as Job Seeker

1. At login page, enter:
   - **Email**: `jobseeker@test.com`
   - **Password**: `password123`
2. Click "Login"
3. **Expected**: 
   - Login successful
   - **Auto-redirect to**: `/dashboard/jobseeker`
   - You should see the **Job Seeker Dashboard** with:
     - Top navbar with "Job Seeker Dashboard" title
     - Sidebar with menu items (Dashboard, Browse Jobs, Applied Jobs, etc.)
     - KPI cards (Total Applications, Pending, Accepted, Rejected)
     - Applied Jobs table (empty state shown)
     - Notifications section

### Test 3: Register an Employer Account

1. Logout (click user avatar → Logout) or go to: http://127.0.0.1:8000/register
2. Fill in the form:
   - **Email**: `employer@test.com`
   - **Password**: `password123`
   - **Role**: Select "Employer"
3. Click "Create account"
4. **Expected**: Success message → Auto-redirect to `/login`

### Test 4: Login as Employer

1. At login page, enter:
   - **Email**: `employer@test.com`
   - **Password**: `password123`
2. Click "Login"
3. **Expected**: 
   - Login successful
   - **Auto-redirect to**: `/dashboard/employer`
   - You should see the **Employer Dashboard** with:
     - Top navbar with "Employer Dashboard" title
     - Sidebar with menu items (Dashboard, Post Job, Manage Jobs, Applications, etc.)
     - KPI cards (Total Jobs, Active Jobs, Total Applications, Pending Review)
     - Job Listings table (empty state shown)
     - Recent Applications table (empty state shown)

### Test 5: Role-Based Access Control

1. **Test Job Seeker can't access Employer Dashboard:**
   - Login as job seeker
   - Try to manually navigate to: http://127.0.0.1:8000/dashboard/employer
   - **Expected**: Should get 403 Forbidden or redirect to job seeker dashboard

2. **Test Employer can't access Job Seeker Dashboard:**
   - Login as employer
   - Try to manually navigate to: http://127.0.0.1:8000/dashboard/jobseeker
   - **Expected**: Should get 403 Forbidden or redirect to employer dashboard

### Test 6: Dashboard Features

1. **User Menu:**
   - Click on user avatar/email in top-right
   - **Expected**: Dropdown menu appears with:
     - Profile
     - Settings
     - Logout

2. **Logout:**
   - Click "Logout" from user menu
   - **Expected**: 
     - Cookie cleared
     - Redirect to `/login`

3. **Sidebar Navigation:**
   - Click different menu items
   - **Expected**: Active state highlights current page
   - Links are functional (even if pages don't exist yet)

4. **Responsive Design:**
   - Resize browser window to mobile size
   - **Expected**: Sidebar should collapse/hide on mobile

---

## 🎯 What to Expect

### Job Seeker Dashboard Features:
- ✅ Professional dark theme UI
- ✅ Welcome message with user name
- ✅ 4 KPI cards showing application statistics
- ✅ Applied Jobs table (currently empty - shows empty state)
- ✅ Notifications section (currently empty - shows empty state)
- ✅ Sidebar navigation
- ✅ User profile dropdown menu

### Employer Dashboard Features:
- ✅ Professional dark theme UI
- ✅ Welcome message with user name
- ✅ 4 KPI cards showing job/application statistics
- ✅ Job Listings management table (currently empty - shows empty state)
- ✅ Recent Applications table (currently empty - shows empty state)
- ✅ Analytics section placeholder
- ✅ Sidebar navigation
- ✅ User profile dropdown menu

---

## 🐛 Troubleshooting

### Issue: "Not authenticated" or redirect loop
**Solution**: 
- Clear browser cookies
- Make sure JWT token is being set (check browser DevTools → Application → Cookies)
- Verify SECRET_KEY is set in environment

### Issue: 403 Forbidden when accessing dashboard
**Solution**:
- Make sure you're logged in with the correct role
- Check that the user role matches the dashboard you're trying to access
- Try logging out and logging back in

### Issue: Database connection error
**Solution**:
- Ensure PostgreSQL is running
- Check DATABASE_URL environment variable
- Verify database `job_portal` exists
- Check PostgreSQL credentials

### Issue: CSS/JS not loading
**Solution**:
- Check browser console for 404 errors
- Verify static files are in `project/static/` directory
- Make sure server is running from correct directory
- Hard refresh browser (Ctrl+F5)

### Issue: Templates not found
**Solution**:
- Verify HTML files are in `project/templates/` directory
- Check that Jinja2 templates directory is configured correctly
- Restart the server

---

## 📝 Testing Checklist

- [ ] Server starts without errors
- [ ] Can register a job seeker account
- [ ] Can register an employer account
- [ ] Job seeker login redirects to `/dashboard/jobseeker`
- [ ] Employer login redirects to `/dashboard/employer`
- [ ] Job seeker dashboard displays correctly
- [ ] Employer dashboard displays correctly
- [ ] Role-based access control works (can't access wrong dashboard)
- [ ] User menu dropdown works
- [ ] Logout works correctly
- [ ] Sidebar navigation highlights active item
- [ ] Dashboard is responsive (mobile view)
- [ ] Empty states display correctly
- [ ] KPI cards show (even if zeros)
- [ ] CSS styling is applied correctly
- [ ] No console errors in browser DevTools

---

## 🎨 Visual Checks

When you first open the dashboards, you should see:

1. **Professional Design**: 
   - Dark theme with purple/green gradient background
   - Clean, modern UI
   - Proper spacing and typography

2. **Layout**:
   - Fixed top navbar
   - Sidebar on the left
   - Main content area with cards and tables
   - Everything properly aligned

3. **Colors**:
   - Primary purple buttons
   - Green success indicators
   - Red error indicators
   - Proper contrast for readability

---

## 🔜 Next Steps

Once testing is complete, you can:

1. **Connect Real Data**: Update the JavaScript files to fetch data from actual API endpoints
2. **Add Functionality**: Implement job posting, application submission, etc.
3. **Add More Features**: Profile management, notifications, etc.
4. **Customize**: Adjust colors, styling, or layout as needed

---

## 📞 Quick Reference

**URLs:**
- Root: http://127.0.0.1:8000/
- Login: http://127.0.0.1:8000/login
- Register: http://127.0.0.1:8000/register
- Job Seeker Dashboard: http://127.0.0.1:8000/dashboard/jobseeker
- Employer Dashboard: http://127.0.0.1:8000/dashboard/employer

**Commands:**
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Start server
cd project
uvicorn main:app --reload

# Or from root
uvicorn project.main:app --reload
```

---

Happy Testing! 🎉

