You are a senior backend engineer building a scholarship-matching prototype.

Build the backend for ScholarPath.

ScholarPath matches students to scholarships they are eligible for, explains eligibility, flags missing requirements, and tracks deadlines.

It does NOT submit applications on the student's behalf and does NOT predict selection odds — only eligibility.

---

# TECH STACK

Use:

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- JWT authentication
- pytest

Use clean architecture.

---

# PROJECT STRUCTURE

```
app/
  main.py

  api/
    auth.py
    profile.py
    scholarships.py
    matches.py
    deadlines.py

  core/
    config.py
    security.py

  models/
    user.py
    student_profile.py
    scholarship.py
    eligibility_rule.py
    match.py
    missing_requirement.py
    deadline_alert.py

  schemas/
    auth.py
    profile.py
    scholarship.py
    match.py

  services/
    matching_service.py
    eligibility_rules_service.py
    ai_matching_service.py
    deadline_service.py

  repositories/

  tests/
```

---

# USER ROLES

STUDENT
COUNSELOR   # stretch goal
ADMIN

Implement role-based authorization.

---

# CORE DATABASE MODELS

## User
id, email, password_hash, role, created_at

## StudentProfile
id, user_id
academic: course, year_level, marks_band
financial: income_bracket
demographic: category, gender, disability_status, minority_status (all nullable/optional)
geographic: state, area_type (rural/urban), institution_type
documents_available: list of document types the student has on hand

Avoid collecting unnecessary personal data — brackets and categories, not exact figures or ID numbers, wherever the matching logic allows it.

## Scholarship
id, name, provider, provider_type (government/state/private/institutional)
eligibility_criteria_text (raw published text — the source of truth for evidence)
structured_criteria (parsed hard-filter fields: min/max income, allowed categories, states, course levels, etc.)
required_documents (list)
deadline
amount
source_url

## EligibilityRule
id, scholarship_id, field, operator, value
(used by the hard-filter rules engine before AI ranking)

## Match
id, student_id, scholarship_id
dimension_results: JSON — one entry per dimension (ACADEMIC, FINANCIAL, DEMOGRAPHIC, GEOGRAPHIC, DOCUMENTATION, DEADLINE), each with:
  verdict: ELIGIBLE | PARTIAL | NOT_ELIGIBLE
  evidence: exact quoted clause from eligibility_criteria_text
  reason: short plain-language explanation
overall_verdict: ELIGIBLE | PARTIAL | NOT_ELIGIBLE
created_at, updated_at

## MissingRequirement
id, match_id, requirement_description, is_resolved

## DeadlineAlert
id, student_id, scholarship_id, alert_date, sent (bool)

---

# API ENDPOINTS

```
POST /auth/register
POST /auth/login

GET  /profile/me
PUT  /profile/me

GET  /scholarships
GET  /scholarships/{id}

POST /matches/run          # re-run matching for the current student
GET  /matches              # ranked list of matches
GET  /matches/{id}         # full dimension breakdown + evidence

GET  /deadlines
```

---

# MATCHING PROCESS

When a student's profile is created or updated:

1. Validate profile data.
2. Run the **hard-filter rules engine** against `EligibilityRule` for every scholarship — this removes clear disqualifiers cheaply (e.g. wrong state, income far outside bracket) without needing the AI.
3. For remaining candidate scholarships, send the profile + the scholarship's `eligibility_criteria_text` to the AI Matching Service.
4. Parse the AI's structured response into per-dimension verdicts with evidence.
5. Store the `Match` record and any `MissingRequirement` entries.
6. Compute `overall_verdict` from the dimension results (all ELIGIBLE → ELIGIBLE; any PARTIAL and no NOT_ELIGIBLE → PARTIAL; any NOT_ELIGIBLE → NOT_ELIGIBLE).
7. Create or update `DeadlineAlert` entries for ELIGIBLE and PARTIAL matches.

---

# IMPORTANT AI RULE

The AI must return structured JSON. Example:

```json
{
  "dimensions": [
    {
      "dimension": "FINANCIAL",
      "verdict": "ELIGIBLE",
      "evidence": "Household income must not exceed Rs 2,50,000 per annum",
      "reason": "Student's declared income bracket falls within this limit."
    },
    {
      "dimension": "DOCUMENTATION",
      "verdict": "PARTIAL",
      "evidence": "A valid caste certificate must be submitted",
      "reason": "Student has not indicated having a caste certificate on hand.",
      "missing_requirement": "Valid caste certificate"
    }
  ],
  "summary": "neutral one-line summary"
}
```

Never accept free-form AI output directly. Validate every AI response using Pydantic. If validation fails, retry once, then mark the match as UNSURE rather than fabricating a verdict.

---

# AI SAFETY LAYER

Create a safety filter. Reject or flag any AI output that:

- Predicts selection odds or competitive outcome ("you will likely win this")
- Guarantees an outcome
- Fabricates an eligibility criterion not present in `eligibility_criteria_text`
- Omits evidence for a verdict

The system may only classify **eligibility against published criteria**, never selection likelihood.

---

# EXPLAINABILITY

Every `Match` dimension result must answer WHY, with evidence quoted from the scholarship's actual text. Never generate a hidden black-box score. If the AI cannot find sufficient evidence in the criteria text to support a verdict, that dimension is marked UNSURE, not guessed.

---

# SECURITY

For prototype:

- password hashing
- JWT authentication
- role-based access
- input validation
- rate limiting
- audit logging

Never log passwords, JWT tokens, or unnecessary personal data. Use environment variables. Provide `.env.example`.

---

# TESTING

Write tests for:

- authentication and authorization
- profile creation/update
- hard-filter rules engine correctness
- AI response validation (schema conformance)
- overall-verdict computation from dimension results
- deadline alert generation
- role permissions

---

# DOCUMENTATION

Create `README.md`, `ARCHITECTURE.md`, `API.md` covering setup, database, environment variables, API documentation, security model, and AI safety limitations.

Do not claim data-protection compliance (e.g. GDPR/DPDP) unless the implementation genuinely meets the requirements.

Finish with a working backend that can run locally using Docker Compose.
