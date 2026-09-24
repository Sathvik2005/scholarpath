import { api, label } from '../api.js';
import { useApi } from '../useApi.js';

export default function Deadlines() {
  const { status, data } = useApi(api.deadlines);

  let content;
  if (status === 'loading') content = <div className="empty-state">Loading…</div>;
  else if (status === 'error') content = <div className="empty-state">Could not reach the ScholarPath API.</div>;
  else if (!data.length) content = <div className="empty-state">No deadlines yet — run your matches first.</div>;
  else
    content = data.map((it, i) => (
      <div
        className={`deadline-item ${it.urgent ? 'urgent' : ''}`}
        key={it.scholarship_id}
        style={{ animationDelay: `${i * 60}ms` }}
      >
        <div>
          <div className="name">{it.name}</div>
          <div className="when">
            {new Date(it.deadline).toLocaleDateString()} · {label(it.overall_verdict)}
          </div>
        </div>
        <div className="days">{it.days_until_deadline}d</div>
      </div>
    ));

  return (
    <div className="container" style={{ maxWidth: 680 }}>
      <h2 style={{ fontSize: 28, margin: '0 0 6px' }}>Upcoming Deadlines</h2>
      <p style={{ color: 'var(--muted)', margin: '0 0 30px', fontSize: 14.5 }}>
        Scholarships you're eligible or partially eligible for, soonest first.
      </p>
      {content}
    </div>
  );
}
