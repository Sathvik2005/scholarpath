import { useState } from 'react';
import { api, label } from '../api.js';
import { useApi } from '../useApi.js';

const DIM_LABEL = {
  ACADEMIC: 'Academic',
  FINANCIAL: 'Financial',
  DEMOGRAPHIC: 'Demographic',
  GEOGRAPHIC: 'Geographic',
  DOCUMENTATION: 'Documentation',
  DEADLINE: 'Deadline',
};

function MatchCard({ match, index }) {
  const [open, setOpen] = useState(false);
  const s = match.scholarship;
  const days = match.days_until_deadline;

  return (
    <div className={`match-card ${open ? 'open' : ''}`} style={{ animationDelay: `${index * 45}ms` }}>
      <div
        className="match-head"
        role="button"
        tabIndex={0}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), setOpen((o) => !o))}
      >
        <div>
          <div className="title">{s.name}</div>
          <div className="provider">
            {s.provider} · {s.amount}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div className={`verdict-pill ${match.overall_verdict}`}>{label(match.overall_verdict)}</div>
          <span className="chevron">▾</span>
        </div>
      </div>
      <div className="match-body-wrap">
        <div className="match-body">
          {match.dimension_results.map((d) => (
            <div className="dim-row" key={d.dimension}>
              <div className="dim-name">{DIM_LABEL[d.dimension]}</div>
              <div>
                <div className="dim-reason">{d.reason}</div>
                <div className="dim-evidence">"{d.evidence}"</div>
                {d.missing_requirement && <div className="missing-tag">Missing: {label(d.missing_requirement)}</div>}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="deadline-line">
        <span>Deadline: {new Date(s.deadline).toLocaleDateString()}</span>
        <span>
          <strong>
            {days} day{days === 1 ? '' : 's'}
          </strong>{' '}
          remaining
        </span>
      </div>
    </div>
  );
}

export default function Matches() {
  const { status, data } = useApi(api.matches);
  const [showNotEligible, setShowNotEligible] = useState(false);

  let content;
  if (status === 'loading') content = <div className="empty-state">Loading your matches…</div>;
  else if (status === 'error') content = <div className="empty-state">Could not reach the ScholarPath API.</div>;
  else if (!data.length) content = <div className="empty-state">No matches yet — complete your profile first.</div>;
  else {
    const count = (v) => data.filter((m) => m.overall_verdict === v).length;
    const shown = data.filter((m) => m.overall_verdict !== 'NOT_ELIGIBLE');
    const notEligible = data.filter((m) => m.overall_verdict === 'NOT_ELIGIBLE');
    const upcoming = shown.filter((m) => m.days_until_deadline <= 14).length;

    content = (
      <>
        <div className="summary-row">
          <div className="summary-box el">
            <div className="n">{count('ELIGIBLE')}</div>
            <div className="l">Fully eligible</div>
          </div>
          <div className="summary-box pa">
            <div className="n">{count('PARTIAL')}</div>
            <div className="l">Missing something</div>
          </div>
          <div className="summary-box dl">
            <div className="n">{upcoming}</div>
            <div className="l">Due within 14 days</div>
          </div>
        </div>
        {shown.map((m, i) => (
          <MatchCard key={m.id} match={m} index={i} />
        ))}
        {notEligible.length > 0 &&
          (showNotEligible ? (
            <div style={{ marginTop: 10 }}>
              {notEligible.map((m, i) => (
                <MatchCard key={m.id} match={m} index={i} />
              ))}
            </div>
          ) : (
            <button className="not-eligible-toggle" style={{ width: '100%', background: 'none' }} onClick={() => setShowNotEligible(true)}>
              Show {notEligible.length} not-eligible scholarship{notEligible.length === 1 ? '' : 's'}
            </button>
          ))}
      </>
    );
  }

  return (
    <div className="container">
      <h2 style={{ fontSize: 28, margin: '0 0 6px' }}>Your Scholarship Fit Map</h2>
      <p style={{ color: 'var(--muted)', margin: '0 0 30px', fontSize: 14.5 }}>
        Ranked by fit, then by deadline. Tap a scholarship to see the full breakdown.
      </p>
      {content}
    </div>
  );
}
