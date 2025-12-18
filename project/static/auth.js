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

async function registerFlow() {
  const form = document.getElementById("registerForm");
  if (!form) return;

  const emailEl = document.getElementById("regEmail");
  const passwordEl = document.getElementById("regPassword");
  const roleEl = document.getElementById("regRole");
  const errEl = document.getElementById("registerError");
  const okEl = document.getElementById("registerSuccess");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hide(errEl);
    hide(okEl);

    const payload = {
      email: emailEl.value,
      password: passwordEl.value,
      role: roleEl.value,
    };

    const res = await fetch("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      show(errEl, await parseError(res));
      return;
    }

    show(okEl, "Account created. Redirecting to login…");
    setTimeout(() => (window.location.href = "/login"), 650);
  });
}

async function loginFlow() {
  const form = document.getElementById("loginForm");
  if (!form) return;

  const emailEl = document.getElementById("loginEmail");
  const passwordEl = document.getElementById("loginPassword");
  const errEl = document.getElementById("loginError");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hide(errEl);

    const payload = {
      email: emailEl.value,
      password: passwordEl.value,
    };

    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      show(errEl, await parseError(res));
      return;
    }

    // Cookie is set by the response (HTTP-only). Redirect to protected dashboard.
    window.location.href = "/dashboard";
  });
}

registerFlow();
loginFlow();


