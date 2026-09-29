import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function Recommendations() {
  const [list, setList] = useState(null);
  useEffect(() => { api.recommendations().then(setList); }, []);
  if (!list) return <div>Loading…</div>;
  return (
    <>
      <h1>Recommendations</h1>
      <p className="muted">Courses whose prerequisites you have already completed.</p>
      <div className="grid2">
        {list.map((c) => (
          <div key={c.id} className="course static">
            <div className="row between"><span className="code">{c.id}</span><span className="pill blue small">{c.credits} credits</span></div>
            <div className="title">{c.name}</div>
            <div className="muted small cap">{c.level} · {c.kind}</div>
          </div>
        ))}
      </div>
      <Link to="/planner" className="btn primary">Plan these courses</Link>
    </>
  );
}
