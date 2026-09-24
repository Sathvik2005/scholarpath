import { useState } from 'react';
import { api, API, label } from '../api.js';

const DOC_OPTIONS = [
  'aadhaar',
  'income_certificate',
  'OBC_certificate',
  'SC_certificate',
  'bonafide_certificate',
  'bank_passbook',
  'admission_letter',
];

const INITIAL = {
  full_name: 'Priya Kumar',
  course: 'B.Tech',
  year_level: 2,
  marks_band: '75-90%',
  income_bracket: 'under_2.5L',
  category: '',
  gender: '',
  state: 'Tamil Nadu',
  area_type: 'rural',
  institution_type: 'government',
  documents_available: ['aadhaar', 'income_certificate'],
};

function Field({ label: text, why, children }) {
  return (
    <div className="field">
      <label>{text}</label>
      {children}
      {why && <div className="why">{why}</div>}
    </div>
  );
}

function Select({ value, onChange, options }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      {options.map((o) => {
        const [v, text] = Array.isArray(o) ? o : [o, o];
        return (
          <option key={v} value={v}>
            {text}
          </option>
        );
      })}
    </select>
  );
}

export default function ProfileBuilder({ onDone }) {
  const [form, setForm] = useState(INITIAL);
  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState('forward');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const set = (key) => (value) => setForm((f) => ({ ...f, [key]: value }));

  const toggleDoc = (doc) =>
    setForm((f) => ({
      ...f,
      documents_available: f.documents_available.includes(doc)
        ? f.documents_available.filter((d) => d !== doc)
        : [...f.documents_available, doc],
    }));

  const steps = [
    {
      title: 'About you',
      body: (
        <Field
          label="Full name"
          why="Used only to confirm your uploaded documents belong to you — never shared or sold."
        >
          <input type="text" value={form.full_name} onChange={(e) => set('full_name')(e.target.value)} />
        </Field>
      ),
      valid: form.full_name.trim().length > 0,
    },
    {
      title: 'Academic details',
      body: (
        <>
          <Field label="Course">
            <Select
              value={form.course}
              onChange={set('course')}
              options={['B.Tech', 'B.Sc', 'B.A', 'B.Com', 'M.Tech', 'Other']}
            />
          </Field>
          <Field label="Year of study">
            <input
              type="number"
              min="1"
              max="6"
              value={form.year_level}
              onChange={(e) => set('year_level')(e.target.value)}
            />
          </Field>
          <Field label="Marks / GPA band">
            <Select
              value={form.marks_band}
              onChange={set('marks_band')}
              options={['Above 90%', '75-90%', '60-75%', 'Below 60%']}
            />
          </Field>
        </>
      ),
      valid: Number(form.year_level) >= 1 && Number(form.year_level) <= 6,
    },
    {
      title: 'Financial details',
      body: (
        <Field
          label="Household income bracket"
          why="We ask for a bracket, not an exact figure, to match income-based eligibility only."
        >
          <Select
            value={form.income_bracket}
            onChange={set('income_bracket')}
            options={[
              ['under_2.5L', 'Under ₹2.5 lakh / year'],
              ['2.5L_5L', '₹2.5–5 lakh / year'],
              ['above_5L', 'Above ₹5 lakh / year'],
            ]}
          />
        </Field>
      ),
      valid: true,
    },
    {
      title: 'Demographic details',
      body: (
        <>
          <Field
            label="Category (optional)"
            why="Some scholarships are category-specific. Skip this and we'll only show category-neutral matches."
          >
            <Select
              value={form.category}
              onChange={set('category')}
              options={[['', 'Prefer not to say'], 'General', 'OBC', 'SC', 'ST', 'EWS']}
            />
          </Field>
          <Field label="Gender (optional)">
            <Select
              value={form.gender}
              onChange={set('gender')}
              options={[
                ['', 'Prefer not to say'],
                ['female', 'Female'],
                ['male', 'Male'],
                ['other', 'Other'],
              ]}
            />
          </Field>
        </>
      ),
      valid: true,
    },
    {
      title: 'Geographic details',
      body: (
        <>
          <Field label="State">
            <input type="text" value={form.state} onChange={(e) => set('state')(e.target.value)} />
          </Field>
          <Field label="Area type">
            <Select
              value={form.area_type}
              onChange={set('area_type')}
              options={[
                ['rural', 'Rural'],
                ['urban', 'Urban'],
              ]}
            />
          </Field>
          <Field label="Institution type">
            <Select
              value={form.institution_type}
              onChange={set('institution_type')}
              options={[
                ['government', 'Government'],
                ['private', 'Private'],
                ['aided', 'Aided'],
              ]}
            />
          </Field>
        </>
      ),
      valid: form.state.trim().length > 0,
    },
    {
      title: 'Documents on hand',
      body: (
        <>
          <div className="checkbox-grid">
            {DOC_OPTIONS.map((d) => (
              <label key={d}>
                <input type="checkbox" checked={form.documents_available.includes(d)} onChange={() => toggleDoc(d)} />{' '}
                {label(d)}
              </label>
            ))}
          </div>
          <div className="why" style={{ marginTop: 12 }}>
            A quick self-check for now. In the next step you'll actually upload these — we verify the real document
            rather than just trusting this checklist.
          </div>
        </>
      ),
      valid: true,
    },
  ];

  const current = steps[step];
  const isLast = step === steps.length - 1;

  const go = (delta) => {
    setDirection(delta > 0 ? 'forward' : 'back');
    setStep((s) => s + delta);
  };

  async function submit() {
    setSaving(true);
    setError(null);
    try {
      await api.saveProfile({
        ...form,
        full_name: form.full_name.trim(),
        year_level: parseInt(form.year_level, 10),
        category: form.category || null,
        gender: form.gender || null,
      });
      await api.runMatches();
      onDone();
    } catch {
      setError(`Could not reach the ScholarPath API. Make sure the backend is running on ${API || 'this server'}.`);
      setSaving(false);
    }
  }

  return (
    <div className="container" style={{ maxWidth: 640 }}>
      <div className="step-progress">
        {steps.map((_, i) => (
          <div key={i} className={`dot ${i < step ? 'done' : ''} ${i === step ? 'current' : ''}`} />
        ))}
      </div>
      <div id="profile-steps" key={step} className={direction === 'forward' ? 'slide-in-forward' : 'slide-in-back'}>
        <h2 style={{ fontSize: 22, marginBottom: 22 }}>{current.title}</h2>
        {current.body}
        {error && (
          <div className="finding HARD_STOP">
            <span className="tag">Error</span> {error}
          </div>
        )}
        <div className="step-nav">
          <button
            className="btn btn-secondary"
            style={{ visibility: step === 0 ? 'hidden' : 'visible' }}
            onClick={() => go(-1)}
          >
            Back
          </button>
          <button
            className="btn btn-primary"
            disabled={!current.valid || saving}
            onClick={isLast ? submit : () => go(1)}
          >
            {isLast ? (saving ? 'Saving…' : 'Verify My Documents') : 'Continue'}
          </button>
        </div>
      </div>
    </div>
  );
}
