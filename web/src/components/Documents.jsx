import { useEffect, useRef, useState } from 'react';
import { api, label } from '../api.js';
import { useApi } from '../useApi.js';

const DOC_TYPES = [
  { key: 'aadhaar', label: 'Aadhaar', sub: 'Identity proof' },
  { key: 'income_certificate', label: 'Income Certificate', sub: 'Proves household income bracket' },
  { key: 'OBC_certificate', label: 'OBC Certificate', sub: 'Category proof, if applicable' },
  { key: 'SC_certificate', label: 'SC Certificate', sub: 'Category proof, if applicable' },
  { key: 'bonafide_certificate', label: 'Bonafide Certificate', sub: 'Confirms current enrollment' },
  { key: 'bank_passbook', label: 'Bank Passbook', sub: 'For scholarship disbursal' },
  { key: 'admission_letter', label: 'Admission Letter', sub: 'Confirms course and institution' },
];

const STAGES = ['Uploaded', 'Classified', 'Extracted', 'Validated'];

// The pipeline stepper: a document's journey through classify -> extract ->
// validate -> decide, with the final node colored by the real backend result.
function Pipeline({ stage, status }) {
  const stageClass = (s) => {
    if (!status) return s <= stage ? 'done' : '';
    if (s === 4 && status === 'REJECTED') return 'rejected';
    if (s === 4 && status === 'NEEDS_REVIEW') return 'review';
    return 'done';
  };
  return (
    <div className="pipeline">
      {STAGES.map((name, i) => (
        <div key={name} className={`stage ${stageClass(i + 1)}`}>
          <div className="node">{i + 1}</div>
          <div className="label">{name}</div>
        </div>
      ))}
    </div>
  );
}

function DocResult({ result }) {
  const cls = result.classification || {};
  return (
    <div className="doc-result">
      <span className={`doc-status-pill ${result.status}`}>{label(result.status)}</span>
      <div className="classification-note">
        Classified as <strong>{cls.predicted_type}</strong> ({Math.round((cls.confidence || 0) * 100)}% confidence).{' '}
        {cls.reasoning}
      </div>
      <div className="extracted-fields">
        {Object.entries(result.extracted_fields || {}).map(([k, v]) => (
          <div className="extracted-field" key={k}>
            <div className="k">{label(k)}</div>
            <div className={`v ${v.value ? '' : 'empty'}`}>{v.value || 'not found'}</div>
          </div>
        ))}
      </div>
      {(result.validation_findings || []).map((f, i) => (
        <div className={`finding ${f.severity}`} key={i}>
          <span className="tag">{label(f.severity)}</span> {f.message}
        </div>
      ))}
    </div>
  );
}

function DocTypeCard({ type, docs, onChanged }) {
  // null | { stage: 1..4, result?, error? }
  const [progress, setProgress] = useState(null);
  const timers = useRef([]);

  useEffect(() => () => timers.current.forEach(clearTimeout), []);

  const later = (ms, fn) => timers.current.push(setTimeout(fn, ms));

  async function handleUpload(e) {
    const file = e.target.files[0];
    e.target.value = ''; // allow re-uploading the same file
    if (!file) return;

    // Brief staged animation so the pipeline reads as a real process, then
    // show the real backend result.
    setProgress({ stage: 1 });
    later(300, () => setProgress((p) => (p && !p.result ? { stage: 2 } : p)));
    later(650, () => setProgress((p) => (p && !p.result ? { stage: 3 } : p)));

    try {
      const result = await api.uploadDocument(type.key, file);
      await api.runMatches();
      later(900, () => {
        setProgress({ stage: 4, result });
        onChanged();
      });
    } catch {
      later(700, () => setProgress({ stage: 0, error: true }));
    }
  }

  async function handleDelete(id) {
    try {
      await api.deleteDocument(id);
      await api.runMatches();
    } catch {
      /* the reload below shows the real state either way */
    }
    setProgress(null);
    onChanged();
  }

  return (
    <div className="doc-type-card">
      <div className="doc-type-head">
        <div>
          <div className="doc-type-name">{type.label}</div>
          <div className="doc-type-sub">{type.sub}</div>
        </div>
        <label className="upload-btn">
          Upload
          <input type="file" style={{ display: 'none' }} accept=".txt,.pdf" onChange={handleUpload} />
        </label>
      </div>

      {docs.length > 0 && (
        <div className="doc-uploaded-list">
          {docs.map((d) => (
            <span className={`doc-chip ${d.status}`} key={d.id}>
              {d.file_name}{' '}
              <span className="x" role="button" aria-label={`Remove ${d.file_name}`} onClick={() => handleDelete(d.id)}>
                ✕
              </span>
            </span>
          ))}
        </div>
      )}

      {progress?.error && (
        <div className="finding HARD_STOP">
          <span className="tag">Error</span> Could not reach the ScholarPath API to process this document.
        </div>
      )}
      {progress && !progress.error && (
        <>
          <Pipeline stage={progress.stage} status={progress.result?.status} />
          {progress.result && <DocResult result={progress.result} />}
        </>
      )}
    </div>
  );
}

export default function Documents() {
  const { status, data, reload } = useApi(api.documents);

  const byType = {};
  (data || []).forEach((d) => {
    (byType[d.declared_type] ||= []).push(d);
  });

  return (
    <div className="container" style={{ maxWidth: 720 }}>
      <h2 style={{ fontSize: 28, margin: '0 0 6px' }}>Verify Your Documents</h2>
      <p style={{ color: 'var(--muted)', margin: '0 0 30px', fontSize: 14.5 }}>
        Upload a document and watch it move through the same pipeline a reviewer would use: classify what it is,
        extract the key details, and validate them against your profile — before it ever counts toward a scholarship
        match.
      </p>
      {status === 'error' ? (
        <div className="empty-state">Could not reach the ScholarPath API.</div>
      ) : (
        DOC_TYPES.map((t) => <DocTypeCard key={t.key} type={t} docs={byType[t.key] || []} onChanged={reload} />)
      )}
    </div>
  );
}
