export default function ProgressBar({ completed, planned = 0, total }) {
  const remaining = Math.max(total - completed - planned, 0);
  const pct = (n) => `${(n / total) * 100}%`;
  return (
    <div>
      <div className="bar">
        {completed > 0 && <div className="seg green" style={{ width: pct(completed) }}>{completed}</div>}
        {planned > 0 && <div className="seg blue" style={{ width: pct(planned) }}>{planned}</div>}
        <div className="seg grey" style={{ flex: 1 }}>{remaining}</div>
      </div>
      <div className="legend">
        <span><i className="dot green" /> Completed: {completed}</span>
        <span><i className="dot blue" /> Planned: {planned}</span>
        <span><i className="dot grey" /> Remaining: {total - completed}</span>
        <b className="right">{completed} / {total} credits</b>
      </div>
    </div>
  );
}
