import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function SavedPlans({ onChange }) {
  const [plans, setPlans] = useState(null);
  const load = () => api.plans().then(setPlans);
  useEffect(() => { load(); }, []);

  async function remove(id) {
    await api.deletePlan(id);
    await load();
    onChange?.();
  }

  if (!plans) return <div>Loading…</div>;
  return (
    <>
      <h1>Saved Plans</h1>
      {!plans.length && <div className="card">No plans yet. <Link to="/planner">Create one</Link>.</div>}
      <div className="kanban-board">
        {plans.map((p, i) => {
          const color = ["blue", "orange", "green"][i % 3];
          return (
            <div key={p.id} className={`kanban-col ${color}`}>
              <div className="kanban-header">
                <h3>{p.name}</h3>
                <span className="sub">{p.total_credits} credits • {p.courses.length} courses</span>
                <button className="kanban-del" onClick={() => remove(p.id)} title="Delete Plan">✕</button>
              </div>
              <div className="kanban-body">
                {p.courses.map((c, idx) => (
                  <div key={c.id} className="k-card">
                    <div className="k-card-index">{idx + 1}</div>
                    <div className="k-card-content">
                      <div className="k-card-title">{c.name}</div>
                      <div className="k-card-code">{c.id}</div>
                    </div>
                    <div className="k-card-credits">{c.credits}</div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}
