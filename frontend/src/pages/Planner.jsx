import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import ProgressBar from "./ProgressBar.jsx";

const LEVELS = ["foundation", "diploma", "degree"];

export default function Planner({ student: s, onSaved }) {
  const nav = useNavigate();
  const [courses, setCourses] = useState([]);
  const [selected, setSelected] = useState([]);
  const [step, setStep] = useState(1);
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const max = s.max_courses_per_term;

  useEffect(() => { api.courses().then(setCourses); }, []);

  const byId = useMemo(() => Object.fromEntries(courses.map((c) => [c.id, c])), [courses]);
  const chosen = selected.map((id) => byId[id]).filter(Boolean);
  const credits = chosen.reduce((n, c) => n + c.credits, 0);
  const projects = chosen.filter((c) => c.kind === "project").length;

  function toggle(c) {
    setError("");
    if (c.completed || !c.prereqs_met) return;
    if (selected.includes(c.id)) return setSelected(selected.filter((x) => x !== c.id));
    if (selected.length >= max) return setError(`Max ${max} courses per term.`);
    setSelected([...selected, c.id]);
  }

  async function save() {
    try {
      await api.createPlan(name.trim() || `${s.next_term} plan`, selected);
      await onSaved();
      nav("/plans");
    } catch (e) { setError(e.message); }
  }

  const titles = { 1: `Select courses you plan to take for ${s.next_term}`, 2: "Review your selection", 3: "Name and save your plan" };

  return (
    <>
      <div className="row gap">
        <h1>{s.next_term} Planning</h1>
        <span className="pill blue">Step {step} of 3</span>
        <span className="muted grow">{titles[step]}</span>
        <span className="pill orange">Max {max} courses per term</span>
      </div>

      <div className="card">
        <h3>Your Progress</h3>
        <ProgressBar completed={s.completed_credits} planned={s.planned_credits + credits} total={s.total_credits} />
      </div>

      {error && <div className="alert error">{error}</div>}

      <div className="split">
        <div>
          {step === 1 && LEVELS.map((lvl) => {
            const items = courses.filter((c) => c.level === lvl);
            if (!items.length) return null;
            return (
              <section key={lvl} className="card">
                <h3 className="cap">{lvl} Level <span className="muted small">{items.length} items</span></h3>
                {["theory", "project"].map((kind) => {
                  const list = items.filter((c) => c.kind === kind);
                  if (!list.length) return null;
                  return (
                    <div key={kind}>
                      <h4 className="cap">{kind} Courses <span className="pill blue small">{list.length}</span></h4>
                      <div className="grid2">
                        {list.map((c) => {
                          const locked = c.completed || !c.prereqs_met;
                          return (
                            <button key={c.id} onClick={() => toggle(c)} disabled={locked}
                              className={`course ${selected.includes(c.id) ? "on" : ""} ${locked ? "locked" : ""}`}>
                              <div className="row between">
                                <span className="code">{c.id}</span>
                                <span className="pill blue small">{c.credits} credits</span>
                              </div>
                              <div className="title">{c.name}</div>
                              <div className="muted small">
                                {c.completed ? "Completed"
                                  : c.prerequisites.length ? `Prerequisites: ${c.prerequisites.join(", ")}` : "No prerequisites"}
                                {!c.completed && !c.prereqs_met && " (not met)"}
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </section>
            );
          })}

          {step === 2 && (
            <div className="card">
              <h3>Review</h3>
              {chosen.map((c) => (
                <div key={c.id} className="row between line"><span><b>{c.id}</b> {c.name}</span><span>{c.credits} cr</span></div>
              ))}
              <div className="row between line"><b>Total</b><b>{credits} credits</b></div>
            </div>
          )}

          {step === 3 && (
            <div className="card">
              <h3>Plan name</h3>
              <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder={`${s.next_term} plan`} />
            </div>
          )}
        </div>

        <aside className="card sticky">
          <h3>Selection Summary</h3>
          <div className="grid2">
            <div className="tile blue"><div className="big">{selected.length}<span className="muted small"> / {max}</span></div>Courses</div>
            <div className="tile red"><div className="big">{projects}</div>Projects</div>
          </div>
          <h5>CREDITS BREAKDOWN</h5>
          <div className="row between"><span>Selected credits</span><b>{credits}</b></div>
          <div className="actions">
            {step > 1 && <button className="btn" onClick={() => setStep(step - 1)}>Back</button>}
            {step < 3 && <button className="btn primary" disabled={!selected.length} onClick={() => setStep(step + 1)}>Next</button>}
            {step === 3 && <button className="btn primary" onClick={save}>Save Plan</button>}
          </div>
        </aside>
      </div>
    </>
  );
}
