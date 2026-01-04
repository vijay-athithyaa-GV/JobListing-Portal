console.log("Jobs JS loaded");

const API_URL = "http://127.0.0.1:8000";
const token = localStorage.getItem("token");
const params = new URLSearchParams(window.location.search);
const jobId = params.get("job_id");

/* =========================
   PAGE LOAD
========================= */
document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("jobsContainer");
  if (container) loadJobs();
  if (jobId) loadJobForEdit();
});

/* =========================
   CREATE / UPDATE JOB
========================= */
window.createJob = async function (event) {
  event.preventDefault();

  if (!token) {
    alert("Not logged in");
    return;
  }

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
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(jobData),
  });

  if (res.ok) {
    alert(jobId ? "Job updated" : "Job created");
    window.location.href = "/job-listings";
  } else {
    const err = await res.json();
    alert(err.detail || "Operation failed");
  }
};

/* =========================
   LOAD JOB LIST
========================= */
async function loadJobs() {
  const res = await fetch(`${API_URL}/jobs`, {
    headers: { Authorization: `Bearer ${token}` },
  });

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
    headers: { Authorization: `Bearer ${token}` },
  });

  const jobs = await res.json();
  const job = jobs.find((j) => j.id == jobId);

  if (!job) return alert("Job not found");

  title.value = job.title;
  description.value = job.description;
  qualifications.value = job.qualifications;
  responsibilities.value = job.responsibilities;
  location.value = job.location;
  salary_range.value = job.salary_range;
}

/* =========================
   DELETE JOB
========================= */
async function deleteJob(id) {
  if (!confirm("Delete job?")) return;

  const res = await fetch(`${API_URL}/jobs/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });

  if (res.ok) {
    alert("Deleted");
    loadJobs();
  } else {
    alert("Delete failed");
  }
}

/* =========================
   EDIT REDIRECT
========================= */
function editJob(id) {
  window.location.href = `/job-form?job_id=${id}`;
}
