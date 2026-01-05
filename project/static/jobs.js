console.log("Jobs JS loaded");

const API_URL = "http://127.0.0.1:8000";
const params = new URLSearchParams(window.location.search);
const jobId = params.get("job_id");

/* =========================
   PAGE LOAD
========================= */
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("jobForm");
  const container = document.getElementById("jobsContainer");

  if (form) {
    form.addEventListener("submit", createJob);
  }

  if (container) {
    setTimeout(loadJobs, 200); // 🔑 allow auth cookie to settle
  }

  if (jobId) {
    loadJobForEdit();
  }
});

/* =========================
   CREATE / UPDATE JOB
========================= */
async function createJob(event) {
  event.preventDefault();

  const jobData = {
    title: document.getElementById("title").value,
    description: document.getElementById("description").value,
    qualifications: document.getElementById("qualifications").value,
    responsibilities: document.getElementById("responsibilities").value,
    location: document.getElementById("location").value,
    salary_range: document.getElementById("salary_range").value,
  };

  const url = jobId ? `${API_URL}/jobs/${jobId}` : `${API_URL}/jobs`;
  const method = jobId ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
    body: JSON.stringify(jobData),
  });

  if (res.ok) {
    alert(
      jobId ? "Job updated successfully ✅" : "Job created successfully ✅"
    );
    window.location.href = "/job-listings";
  } else {
    const err = await res.json();
    alert(err.detail || "Operation failed ❌");
  }
}

/* =========================
   LOAD JOB LIST
========================= */
async function loadJobs() {
  const res = await fetch(`${API_URL}/jobs`, {
    credentials: "same-origin",
  });

  if (!res.ok) {
    console.error("Failed to load jobs");
    return;
  }

  const jobs = await res.json();
  const container = document.getElementById("jobsContainer");
  container.innerHTML = "";

  if (jobs.length === 0) {
    container.innerHTML = "<p>No jobs yet.</p>";
    return;
  }

  jobs.forEach((job) => {
    container.innerHTML += `
      <div class="job-card">
        <h3>${job.title}</h3>
        <p><b>Location:</b> ${job.location}</p>
        <p><b>Salary:</b> ${job.salary_range}</p>
        <button onclick="viewJob(${job.id})">View</button>
        <button onclick="editJob(${job.id})">Edit</button>
        <button onclick="deleteJob(${job.id})">Delete</button>

      </div>
    `;
  });
}

/* =========================
   LOAD JOB FOR EDIT
========================= */
async function loadJobForEdit() {
  const res = await fetch(`${API_URL}/jobs`, {
    credentials: "same-origin",
  });

  if (!res.ok) return;

  const jobs = await res.json();
  const job = jobs.find((j) => j.id == jobId);

  if (!job) {
    alert("Job not found");
    return;
  }

  document.getElementById("title").value = job.title;
  document.getElementById("description").value = job.description;
  document.getElementById("qualifications").value = job.qualifications;
  document.getElementById("responsibilities").value = job.responsibilities;
  document.getElementById("location").value = job.location;
  document.getElementById("salary_range").value = job.salary_range;
}

/* =========================
   DELETE JOB
========================= */
async function deleteJob(id) {
  if (!confirm("Delete job?")) return;

  const res = await fetch(`${API_URL}/jobs/${id}`, {
    method: "DELETE",
    credentials: "same-origin",
  });

  if (res.ok) {
    alert("Job deleted ✅");
    loadJobs();
  } else {
    alert("Delete failed ❌");
  }
}

/* =========================
   EDIT REDIRECT
========================= */
function editJob(id) {
  window.location.href = `/job-form?job_id=${id}`;
}

function viewJob(id) {
  window.location.href = `/job-view?job_id=${id}`;
}
