// Local dev talks to the backend on :8321 (override with VITE_API_URL).
// Deployed anywhere else (e.g. Vercel) it uses same-origin relative paths --
// see vercel.json for how those get routed to the serverless API function.
const isLocal = ['localhost', '127.0.0.1'].includes(location.hostname);
export const API = import.meta.env.VITE_API_URL ?? (isLocal ? 'http://127.0.0.1:8321' : '');

async function request(path, options) {
  const res = await fetch(`${API}${path}`, options);
  if (!res.ok) throw new Error(`${options?.method || 'GET'} ${path} failed (${res.status})`);
  return res.json();
}

export const api = {
  saveProfile: (payload) =>
    request('/profile/me', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  runMatches: () => request('/matches/run', { method: 'POST' }),
  matches: () => request('/matches'),
  deadlines: () => request('/deadlines'),
  documents: () => request('/documents'),
  uploadDocument: (declaredType, file) => {
    const form = new FormData();
    form.append('declared_type', declaredType);
    form.append('file', file);
    return request('/documents/upload', { method: 'POST', body: form });
  },
  deleteDocument: (id) => request(`/documents/${id}`, { method: 'DELETE' }),
};

export const label = (s) => String(s ?? '').replace(/_/g, ' ');
