import { Link } from "react-router-dom";
import ProgressBar from "./ProgressBar.jsx";

export default function Dashboard({ student: s }) {
  return (
    <>
      <div className="row between">
        <div>
          <div className="muted">Welcome</div>
          <h1>{s.name.toUpperCase()}</h1>
          <div className="muted">{s.program}</div>
          <span className="pill green">{s.status}</span>
        </div>
        <div className="right-col">
          <div className="muted">Current Term: <b>{s.current_term}</b> ({s.start_term})</div>
          <Link to="/planner" className="btn primary wide">Plan Your Courses</Link>
        </div>
      </div>

      <div className="grid3">
        <div className="card stat"><div className="muted">Current Level</div><div className="big">{s.level.toUpperCase()}</div><div className="muted">{s.program}</div></div>
        <div className="card stat"><div className="muted">Credits Earned</div><div className="big">{s.completed_credits}</div><div className="muted">{s.remaining_credits} credits remaining</div></div>
        <div className="card stat"><div className="muted">Total Terms</div><div className="big">{s.total_terms}</div><div className="muted">In program since {s.start_term}</div></div>
      </div>

      <div className="card">
        <h3>Your Progress</h3>
        <ProgressBar completed={s.completed_credits} planned={s.planned_credits} total={s.total_credits} />
      </div>
    </>
  );
}
