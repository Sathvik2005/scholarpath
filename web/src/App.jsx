import { useState } from 'react';
import Landing from './components/Landing.jsx';
import ProfileBuilder from './components/ProfileBuilder.jsx';
import Documents from './components/Documents.jsx';
import Matches from './components/Matches.jsx';
import Deadlines from './components/Deadlines.jsx';

const TABS = [
  { key: 'landing', label: 'Home' },
  { key: 'profile', label: 'Build Profile' },
  { key: 'documents', label: 'Documents' },
  { key: 'matches', label: 'My Matches' },
  { key: 'deadlines', label: 'Deadlines' },
];

export default function App() {
  const [view, setView] = useState('landing');

  return (
    <>
      <header className="site">
        <div className="container">
          <div className="brand">ScholarPath</div>
          <nav className="tabs">
            {TABS.map((t) => (
              <button key={t.key} className={view === t.key ? 'active' : ''} onClick={() => setView(t.key)}>
                {t.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* key={view} remounts the section so the view-in animation replays and data reloads */}
      <section className="view active" key={view}>
        {view === 'landing' && <Landing onStart={() => setView('profile')} />}
        {view === 'profile' && <ProfileBuilder onDone={() => setView('documents')} />}
        {view === 'documents' && <Documents />}
        {view === 'matches' && <Matches />}
        {view === 'deadlines' && <Deadlines />}
      </section>
    </>
  );
}
