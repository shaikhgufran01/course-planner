import { useEffect, useState } from "react";
import { api } from "../api";
import ProgressBar from "./ProgressBar.jsx";

export default function CreditTracker({ onChange }) {
  const [courses, setCourses] = useState([]);
  const [progress, setProgress] = useState(null);

  const load = async () => {
    const [c, p] = await Promise.all([api.courses(), api.progress()]);
    setCourses(c); setProgress(p);
  };
  useEffect(() => { load(); }, []);

  async function toggle(c) {
    await (c.completed ? api.uncomplete(c.id) : api.complete(c.id));
    await load();
    onChange?.();
  }

  if (!progress) return <div>Loading…</div>;
  return (
    <>
      <h1>Credit Progress Tracker</h1>
      <div className="card">
        <ProgressBar completed={progress.completed_credits} total={progress.total_credits} />
        <div className="grid3 mt">
          {Object.entries(progress.by_level).map(([lvl, v]) => (
            <div key={lvl} className="tile blue"><div className="cap">{lvl}</div><b>{v.completed_credits} / {v.total_credits}</b></div>
          ))}
        </div>
      </div>
      <div className="card">
        <h3>Mark completed courses</h3>
        {courses.map((c) => (
          <label key={c.id} className="row between line">
            <span><b>{c.id}</b> {c.name} <span className="muted small">({c.credits} cr)</span></span>
            <input type="checkbox" checked={c.completed} onChange={() => toggle(c)} />
          </label>
        ))}
      </div>
    </>
  );
}
