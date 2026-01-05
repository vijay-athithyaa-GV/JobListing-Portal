const API_URL = "http://127.0.0.1:8000";
const params = new URLSearchParams(window.location.search);
const jobId = params.get("job_id");

document.addEventListener("DOMContentLoaded", loadJob);

async function loadJob() {
  const res = await fetch(`${API_URL}/jobs`, {
    credentials: "same-origin",
  });

  if (!res.ok) {
    alert("Not authorized");
    window.location.href = "/login";
    return;
  }

  const jobs = await res.json();
  const job = jobs.find((j) => j.id == jobId);

  if (!job) {
    alert("Job not found");
    return;
  }

  document.getElementById("jobDetails").innerHTML = `
    <h3>${job.title}</h3>
    <p><b>Description:</b> ${job.description}</p>
    <p><b>Qualifications:</b> ${job.qualifications}</p>
    <p><b>Responsibilities:</b> ${job.responsibilities}</p>
    <p><b>Location:</b> ${job.location}</p>
    <p><b>Salary:</b> ${job.salary_range}</p>
  `;
}
