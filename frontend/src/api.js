// No login: each browser gets a random id, and its data is stored under that id.
function clientId() {
  let id = localStorage.getItem("cp_client_id");
  if (!id) {
    id = crypto.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}-xxxxxxxx`;
    localStorage.setItem("cp_client_id", id);
  }
  return id;
}

async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", "X-Client-Id": clientId(), ...(options.headers || {}) },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail ?? detail; } catch {}
    throw new Error(Array.isArray(detail) ? detail.join(" ") : detail);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  student: () => request("/student"),
  updateName: (name) => request("/student", { method: "PUT", body: JSON.stringify({ name }) }),
  courses: () => request("/courses"),

  progress: () => request("/progress"),
  plans: () => request("/plans"),
  createPlan: (name, terms, term_labels) => request("/plans", { method: "POST", body: JSON.stringify({ name, terms, term_labels }) }),
  getPlan: (id) => request(`/plans/${id}`),
  updatePlan: (id, name, terms, term_labels) => request(`/plans/${id}`, { method: "PUT", body: JSON.stringify({ name, terms, term_labels }) }),
  deletePlan: (id) => request(`/plans/${id}`, { method: "DELETE" }),
  complete: (id) => request(`/courses/${id}/complete`, { method: "POST" }),
  uncomplete: (id) => request(`/courses/${id}/complete`, { method: "DELETE" }),
};
