# ScholarPath

An explainable scholarship-matching platform: students build a profile, get
matched against a scholarship database, see exactly *why* they're eligible
(or what's missing), verify their documents, and track deadlines.

Built for ZERO ORIGIN Round 1. It implements the full loop described in
`docs/00_PROJECT_CONTEXT.md` and runs with **no API keys** — matching and
document verification are deterministic rule-based engines.

## Structure

```
backend/     FastAPI + SQLite: profiles, scholarships, matching engine,
             document classify -> extract -> validate pipeline
web/         React (Vite) frontend: landing + 3D Fit Map, profile builder,
             document verification, matches, deadlines
api/         Vercel serverless entry point (imports backend/)
vercel.json  Vercel build + routing config
docs/        Blueprint prompts for the full production build
```

## Running locally

**1. Backend** (Python 3.10+)

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate    macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8321
```

Seeds 5 sample scholarships (government, state, private, institutional) on
startup, with deadlines relative to today. API docs: http://127.0.0.1:8321/docs

**2. Frontend** (Node 18+)

```bash
cd web
npm install
npm run dev
```

Open http://localhost:5173. On localhost the app talks to
`http://127.0.0.1:8321`; set `VITE_API_URL` to point it elsewhere. When
deployed, it uses same-origin paths.

## Deploying to Vercel

Import the repo in Vercel with the **root directory left as the repo root**.
`vercel.json` builds `web/` and serves the FastAPI app as a Python function
at `api/index.py`, with the API paths (`/profile`, `/matches`, ...) rewritten
to it.

Caveat: Vercel's filesystem is ephemeral, so SQLite lives in `/tmp` and
resets on cold starts — fine for a demo, not for real use. For durability,
point `DATABASE_URL` in `backend/app/core/database.py` at Vercel Postgres or
Neon.

## How it works

**Matching** (`backend/app/services/matching_service.py`) scores every
scholarship on six dimensions — Academic, Financial, Demographic,
Geographic, Documentation, Deadline — each with a verdict, the evidence
quoted from the scholarship's criteria, a reason, and any missing
requirement. The overall verdict is the worst dimension.

**Document verification** (`backend/app/services/document_pipeline_service.py`):

```
UPLOAD -> CLASSIFICATION -> EXTRACTION -> VALIDATION -> DECISION
```

- Classification guesses the document type from its text. A document whose
  detected type differs from the declared type is rejected.
- Extraction pulls fields per type (name, income, category, ...) with a
  confidence per field.
- Validation cross-checks against the profile: name match, income within
  the declared bracket, certificate category equal to the declared category.
  Problems are **HARD_STOP** (reject) or **ADVISORY** (needs review).
- Only **VERIFIED** documents count toward a scholarship's Documentation
  dimension.

Text files and text-layer PDFs are read directly; scanned images have no OCR
yet and go to NEEDS_REVIEW.

## Demo script

1. **Build Profile** with the defaults (Priya Kumar, OBC, rural Tamil Nadu,
   B.Tech, income under ₹2.5L).
2. **Documents** — upload `.txt` files. A matching income certificate:

   ```
   INCOME CERTIFICATE
   Name: Priya Kumar
   Annual Income: Rs 2,00,000
   Issued on 01/08/2026 by Tehsildar
   ```

   lands on **VERIFIED**. Change the name, or put the income above 2,50,000,
   and it is **REJECTED** with the exact mismatch named.
3. **My Matches** — the OBC scholarship is **PARTIAL** until the required
   documents are verified, then flips to **ELIGIBLE**. The SC-only
   scholarship shows **NOT ELIGIBLE** with the reason.
4. **Deadlines** — eligible and partial scholarships, soonest first.

## Known limitations

- One shared demo profile, no authentication — every visitor shares state.
- CORS is open (`*`); restrict it before real use.
- No automated tests yet.

## Path to Round 2

- Swap the rule-based matcher for the LLM-backed version in
  `docs/03_AI_ENGINE_PROMPT.md`, so scholarships can be added from raw
  eligibility text.
- Real OCR + AI classification for scanned documents.
- Real authentication and a hosted database.
- A larger, curated scholarship database.
