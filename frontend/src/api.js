function getToken() { return localStorage.getItem("token"); }
function setToken(token) { localStorage.setItem("token", token); }
function removeToken() { localStorage.removeItem("token"); }

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`/api${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail ?? detail; } catch {}
    if (res.status === 401) removeToken();
    throw new Error(Array.isArray(detail) ? detail.join(" ") : detail);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  login: async (username, password) => {
    const res = await fetch("/api/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password })
    });
    if (!res.ok) throw new Error("Login failed");
    const data = await res.json();
    setToken(data.access_token);
    return data;
  },
  logout: () => removeToken(),
  student: () => request("/student"),
  courses: () => request("/courses"),
  recommendations: () => request("/recommendations"),
  progress: () => request("/progress"),
  plans: () => request("/plans"),
  createPlan: (name, course_ids) =>
    request("/plans", { method: "POST", body: JSON.stringify({ name, course_ids }) }),
  deletePlan: (id) => request(`/plans/${id}`, { method: "DELETE" }),
  complete: (id) => request(`/courses/${id}/complete`, { method: "POST" }),
  uncomplete: (id) => request(`/courses/${id}/complete`, { method: "DELETE" }),
};
