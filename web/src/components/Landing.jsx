import { lazy, Suspense, useCallback, useState } from 'react';

// three.js is large; load it separately so the rest of the app isn't blocked on it.
const FitRadar3D = lazy(() => import('./FitRadar3D.jsx'));

const HOW = [
  ['01', 'Build your profile', 'Academic, financial, demographic, and geographic details — once, editable anytime.'],
  ['02', 'Get matched', 'We check your profile against government, state, private, and institutional scholarships.'],
  ['03', 'See why', "Every match shows the exact criteria you meet — and what's missing, if anything."],
  ['04', 'Never miss a date', 'Deadlines are tracked automatically so eligibility never expires unused.'],
];

export default function Landing({ onStart }) {
  const [webglFailed, setWebglFailed] = useState(false);
  const onUnsupported = useCallback(() => setWebglFailed(true), []);

  return (
    <div className="container">
      <div className="hero">
        <div>
          <h1>Find every scholarship you actually qualify for.</h1>
          <p className="lede">
            ScholarPath matches you to scholarships, explains exactly why you're eligible, flags what's missing, and
            tracks every deadline — so you never lose funding to paperwork or a missed date.
          </p>
          <div style={{ display: 'flex', gap: 12 }}>
            <button className="btn btn-primary" onClick={onStart}>Build My Profile</button>
            <button
              className="btn btn-secondary"
              onClick={() => document.getElementById('how').scrollIntoView({ behavior: 'smooth' })}
            >
              How It Works
            </button>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-big">1 in 3</div>
          <div className="stat-caption">
            eligible students never receive the scholarship they qualified for — mostly due to paperwork, awareness
            gaps, and missed deadlines, not ineligibility.
          </div>
          {webglFailed ? (
            <div className="fitmap-preview">
              <div className="fitmap-cell el">Academic ✓</div>
              <div className="fitmap-cell el">Financial ✓</div>
              <div className="fitmap-cell pa">Docs — 1 missing</div>
            </div>
          ) : (
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: 6 }}>
              <Suspense fallback={<div style={{ width: 300, height: 300 }} />}>
                <FitRadar3D onUnsupported={onUnsupported} />
              </Suspense>
            </div>
          )}
          <div className="fit3d-caption">
            Your Scholarship Fit Map — six dimensions, one shape. Fuller = closer to fully eligible.
          </div>
        </div>
      </div>

      <div className="how-it-works" id="how">
        <h2 style={{ fontSize: 26, margin: 0 }}>How it works</h2>
        <div className="how-grid">
          {HOW.map(([num, title, text]) => (
            <div className="how-step" key={num}>
              <div className="num">{num}</div>
              <h3>{title}</h3>
              <p>{text}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="trust-note">
        <div>
          <strong>What ScholarPath doesn't do</strong>
          We never guarantee you'll be selected, and we never submit applications for you. We assess published
          eligibility criteria only — your final application and documents are always your own. Your profile data is
          never sold or shared.
        </div>
      </div>
    </div>
  );
}
