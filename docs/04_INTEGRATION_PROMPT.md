You are the lead full-stack engineer for ScholarPath.

Integrate the existing Next.js frontend with the FastAPI backend.

Do not rewrite working functionality unnecessarily.

---

# GOAL

Replace all mock data with real API integration.

---

# IMPLEMENT

Authentication flow:

```
Register
  ↓
Login
  ↓
JWT storage
  ↓
Authenticated API calls
  ↓
Role-based routing
```

---

# STUDENT FLOW

```
Login
  ↓
Complete/Edit Profile
  ↓
Backend stores profile
  ↓
Hard-filter rules engine runs
  ↓
AI Matching Service processes remaining candidates
  ↓
Match records + missing requirements created
  ↓
Frontend refreshes Scholarship Fit Map
  ↓
Match results + evidence displayed
  ↓
Deadline alerts populate the tracker
```

---

# ERROR HANDLING

Implement handling for:

- network errors
- authentication expiration
- API validation errors
- AI matching failures (per-scholarship, not all-or-nothing)
- empty results (no scholarships found for the profile yet)
- loading states

---

# IMPORTANT

Do not show fabricated match results.

If AI matching fails for a scholarship:

Show: "We couldn't assess this scholarship yet — check back shortly."

Do not substitute a guessed or default verdict.

---

# DATA TYPES

Ensure TypeScript interfaces match backend Pydantic schemas exactly (dimension names, verdict enum values, evidence/reason/missing_requirement fields). Avoid duplicated API models. Generate shared API documentation where practical.

---

# FINAL TEST

Test the complete flow:

1. Register a student.
2. Login.
3. Complete a profile: B.Tech, year 2, marks 60-75%, income under 2.5L, category OBC, state Tamil Nadu, rural, documents: Aadhaar + income certificate (no caste certificate).
4. Trigger matching against a scholarship requiring OBC/SC/ST, income under 2.5L, Tamil Nadu residency, and a caste certificate.
5. Verify backend stores the profile.
6. Verify the AI Matching Service returns: ACADEMIC eligible, FINANCIAL eligible, DEMOGRAPHIC eligible, GEOGRAPHIC eligible, DOCUMENTATION partial (missing caste certificate).
7. Verify overall_verdict computes to PARTIAL.
8. Verify evidence text is stored and displayed for every dimension.
9. Verify the missing-requirement checklist shows "Valid caste certificate."
10. Verify the deadline tracker shows this scholarship with correct days remaining.
