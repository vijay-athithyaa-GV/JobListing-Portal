function show(el, message) {
  if (!el) return;
  el.textContent = message || "";
  el.classList.remove("hidden");
}

function hide(el) {
  if (!el) return;
  el.textContent = "";
  el.classList.add("hidden");
}

async function parseError(res) {
  try {
    const data = await res.json();
    if (data && typeof data.detail === "string") return data.detail;
    return JSON.stringify(data);
  } catch {
    return await res.text();
  }
}

async function loadJobSeekerProfile() {
  const container = document.getElementById("jsProfile");
  if (!container) return; // not on this page
  const errEl = document.getElementById("profileError");

  hide(errEl);
  container.classList.add("hidden");

  const res = await fetch("/profiles/jobseeker/me", { credentials: "same-origin" });
  if (!res.ok) {
    show(errEl, await parseError(res));
    return;
  }
  const p = await res.json();

  document.getElementById("v_full_name").textContent = p.full_name || "";
  document.getElementById("v_email").textContent = p.email || "";
  document.getElementById("v_phone").textContent = p.phone || "";
  document.getElementById("v_skills").textContent = p.skills || "";
  document.getElementById("v_experience_years").textContent = p.experience_years ?? "";
  document.getElementById("v_education").textContent = p.education || "";
  const resumeEl = document.getElementById("v_resume");
  if (p.resume_url) {
    resumeEl.innerHTML = `<a href="${p.resume_url}" target="_blank">View PDF</a>`;
  } else {
    resumeEl.innerHTML = `<span class="muted">Not uploaded</span>`;
  }

  container.classList.remove("hidden");
}

async function loadEmployerProfile() {
  const container = document.getElementById("emProfile");
  if (!container) return;
  const errEl = document.getElementById("profileError");

  hide(errEl);
  container.classList.add("hidden");

  const res = await fetch("/profiles/employer/me", { credentials: "same-origin" });
  if (!res.ok) {
    show(errEl, await parseError(res));
    return;
  }
  const p = await res.json();

  document.getElementById("e_company_name").textContent = p.company_name || "";
  document.getElementById("e_company_description").textContent = (p.company_description || "");
  document.getElementById("e_website").textContent = p.website || "";
  document.getElementById("e_location").textContent = p.location || "";
  document.getElementById("e_contact_email").textContent = p.contact_email || "";

  container.classList.remove("hidden");
}

function bindResumeUpload() {
  const form = document.getElementById("resumeForm");
  if (!form) return;
  const fileEl = document.getElementById("resumeFile");
  const errEl = document.getElementById("resumeError");
  const okEl = document.getElementById("resumeSuccess");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hide(errEl);
    hide(okEl);

    if (!fileEl.files || fileEl.files.length === 0) {
      show(errEl, "Please choose a PDF file.");
      return;
    }
    const file = fileEl.files[0];
    if (file.type !== "application/pdf") {
      show(errEl, "Only PDF files are allowed.");
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      show(errEl, "File exceeds 2MB limit.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/profiles/jobseeker/resume", {
      method: "POST",
      credentials: "same-origin",
      body: formData,
    });
    if (!res.ok) {
      show(errEl, await parseError(res));
      return;
    }
    const data = await res.json();
    show(okEl, "Uploaded successfully.");
    // Update link
    const resumeEl = document.getElementById("v_resume");
    if (resumeEl && data.resume_url) {
      resumeEl.innerHTML = `<a href="${data.resume_url}" target="_blank">View PDF</a>`;
    }
  });
}

async function preloadJobSeekerForm() {
  const form = document.getElementById("editJsForm");
  if (!form) return;
  const errEl = document.getElementById("editError");
  const okEl = document.getElementById("editSuccess");

  // Try to load existing profile
  const res = await fetch("/profiles/jobseeker/me", { credentials: "same-origin" });
  if (res.ok) {
    const p = await res.json();
    document.getElementById("js_full_name").value = p.full_name || "";
    document.getElementById("js_email").value = p.email || "";
    document.getElementById("js_phone").value = p.phone || "";
    document.getElementById("js_skills").value = p.skills || "";
    document.getElementById("js_experience_years").value = p.experience_years ?? "";
    document.getElementById("js_education").value = p.education || "";
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hide(errEl);
    hide(okEl);

    const payload = {
      full_name: document.getElementById("js_full_name").value,
      email: document.getElementById("js_email").value,
      phone: document.getElementById("js_phone").value || null,
      skills: document.getElementById("js_skills").value || null,
      experience_years: document.getElementById("js_experience_years").value ? Number(document.getElementById("js_experience_years").value) : null,
      education: document.getElementById("js_education").value || null,
    };

    // Determine create vs update
    const exists = (await fetch("/profiles/jobseeker/me", { credentials: "same-origin" })).ok;
    const method = exists ? "PUT" : "POST";
    const endpoint = exists ? "/profiles/jobseeker" : "/profiles/jobseeker";

    const res2 = await fetch(endpoint, {
      method,
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify(payload),
    });
    if (!res2.ok) {
      show(errEl, await parseError(res2));
      return;
    }
    show(okEl, "Saved successfully. Redirecting…");
    setTimeout(() => (window.location.href = "/profile/jobseeker"), 600);
  });
}

async function preloadEmployerForm() {
  const form = document.getElementById("editEmForm");
  if (!form) return;
  const errEl = document.getElementById("editError");
  const okEl = document.getElementById("editSuccess");

  const res = await fetch("/profiles/employer/me", { credentials: "same-origin" });
  if (res.ok) {
    const p = await res.json();
    document.getElementById("em_company_name").value = p.company_name || "";
    document.getElementById("em_company_description").value = p.company_description || "";
    document.getElementById("em_website").value = p.website || "";
    document.getElementById("em_location").value = p.location || "";
    document.getElementById("em_contact_email").value = p.contact_email || "";
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hide(errEl);
    hide(okEl);

    const payload = {
      company_name: document.getElementById("em_company_name").value,
      company_description: document.getElementById("em_company_description").value || null,
      website: document.getElementById("em_website").value || null,
      location: document.getElementById("em_location").value || null,
      contact_email: document.getElementById("em_contact_email").value || null,
    };

    // Determine create vs update
    const exists = (await fetch("/profiles/employer/me", { credentials: "same-origin" })).ok;
    const method = exists ? "PUT" : "POST";
    const endpoint = "/profiles/employer";

    const res2 = await fetch(endpoint, {
      method,
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify(payload),
    });
    if (!res2.ok) {
      show(errEl, await parseError(res2));
      return;
    }
    show(okEl, "Saved successfully. Redirecting…");
    setTimeout(() => (window.location.href = "/profile/employer"), 600);
  });
}

// Kick off page-specific logic
loadJobSeekerProfile();
loadEmployerProfile();
bindResumeUpload();
preloadJobSeekerForm();
preloadEmployerForm();


