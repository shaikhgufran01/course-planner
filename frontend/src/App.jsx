import { useCallback, useEffect, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import { api } from "./api";
import Dashboard from "./pages/Dashboard.jsx";
import Planner from "./pages/Planner.jsx";
import SavedPlans from "./pages/SavedPlans.jsx";
import Recommendations from "./pages/Recommendations.jsx";
import CreditTracker from "./pages/CreditTracker.jsx";

const NAV = [
  ["MAIN", [["/", "Dashboard"]]],
  ["FOUNDATION", [["/recommendations", "Recommendations"]]],
  ["PLANNER", [["/planner", "Course Planner"], ["/plans", "Saved Plans"]]],
  ["PROGRESS", [["/tracker", "Credit Progress Tracker"]]],
];

export default function App() {
  const [student, setStudent] = useState(null);
  const [error, setError] = useState("");
  const [isAuth, setIsAuth] = useState(!!localStorage.getItem("token"));
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("password123");

  const refresh = useCallback(
    () => {
      if (!isAuth) return;
      api.student().then(setStudent).catch((e) => {
        if (e.message.includes("Could not validate credentials")) setIsAuth(false);
        else setError(e.message);
      })
    },
    [isAuth]
  );
  useEffect(() => { refresh(); }, [refresh]);

  async function handleLogin(e) {
    e.preventDefault();
    try {
      await api.login(email, password);
      setIsAuth(true);
      setError("");
    } catch (err) {
      setError("Login failed. Check credentials.");
    }
  }

  function handleLogout() {
    api.logout();
    setIsAuth(false);
    setStudent(null);
  }

  if (!isAuth) return (
    <div className="page" style={{ maxWidth: 400, margin: "100px auto" }}>
      <form className="card" onSubmit={handleLogin}>
        <h3>Login</h3>
        {error && <div className="alert error">{error}</div>}
        <div style={{ marginBottom: 16 }}>
          <label className="muted small">Email</label>
          <input className="input" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div style={{ marginBottom: 16 }}>
          <label className="muted small">Password</label>
          <input className="input" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>
        <button className="btn primary wide" type="submit">Sign In</button>
      </form>
    </div>
  );

  if (error) return <div className="page"><div className="alert error">API error: {error}. Is the backend running on :8000?</div></div>;
  if (!student) return <div className="page">Loading…</div>;

  return (
    <div className="layout">
      <aside className="sidebar">
        {NAV.map(([section, links]) => (
          <div key={section}>
            <div className="nav-section">{section}</div>
            {links.map(([to, label]) => (
              <NavLink key={to} to={to} end={to === "/"} className="nav-link">{label}</NavLink>
            ))}
          </div>
        ))}
        <div className="beta">
          <b>Beta:</b> This app is under beta testing. If you face any issues, please report them.
        </div>
        <div style={{ marginTop: 24 }}>
          <button className="btn danger wide" onClick={handleLogout}>Logout</button>
        </div>
      </aside>
      <main className="page">
        <Routes>
          <Route path="/" element={<Dashboard student={student} />} />
          <Route path="/planner" element={<Planner student={student} onSaved={refresh} />} />
          <Route path="/plans" element={<SavedPlans onChange={refresh} />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/tracker" element={<CreditTracker onChange={refresh} />} />
        </Routes>
      </main>
    </div>
  );
}
