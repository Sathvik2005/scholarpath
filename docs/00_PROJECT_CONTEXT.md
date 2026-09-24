# ScholarPath

*Matching students to the scholarships they actually qualify for — and explaining why.*

## Core Principle

> ScholarPath does not guarantee selection, submit applications on a student's behalf, or replace institutional financial aid counselors. It helps students find scholarships they are eligible for, understand exactly why, see what's missing, and never miss a deadline.

The product identifies fit across:

* 🎓 Academic eligibility (course, year, marks/GPA)
* 💰 Financial eligibility (household income bracket)
* 🧑‍🤝‍🧑 Demographic eligibility (category, gender, disability status, minority status)
* 📍 Geographic eligibility (state, rural/urban, institution type)
* 📄 Documentation readiness (what's required vs. what the student has)
* ⏳ Deadline urgency

The output is a:

## Scholarship Fit Map

```text
Student Profile
       ↓
Profile Builder (one-time + editable)
       ↓
AI + Rules extract eligibility signals per scholarship
       ↓
Fit dimensions identified (Academic / Financial / Demographic / Geographic / Documentation / Deadline)
       ↓
Match Result: ELIGIBLE / PARTIALLY ELIGIBLE / NOT ELIGIBLE
       ↓
Scholarship Fit Map (ranked list with explanations)
       ↓
Missing-requirement checklist
       ↓
Deadline tracker + reminders
```

---

# Core Problem

India has hundreds of government, state, private, and institutional scholarships, but students routinely miss out even when eligible — not because scholarships don't exist, but because:

- They don't know a matching scholarship exists (fragmentation across portals)
- They don't understand *why* they were or weren't shown as eligible (no explainability)
- They lose scholarships to missed deadlines or missing paperwork (no proactive tracking)

A field study found that although 98% of surveyed marginalized students were eligible for a scholarship, over a third never received it — mainly due to procedural delays, paperwork complexity, and lack of awareness, not ineligibility. Government data has also shown declining scholarship beneficiary numbers among SC/OBC/EBC/DNT students despite available funds.

ScholarPath makes eligibility, gaps, and deadlines visible and explainable — before it's too late to act.

---

# Core Concept

**Scholarship Fit Map.** For every scholarship a student could plausibly qualify for, ScholarPath produces a fit assessment across six dimensions, each with a result and a plain-language reason:

1. Academic
2. Financial
3. Demographic
4. Geographic
5. Documentation
6. Deadline

Each dimension resolves to:

- **Eligible**
- **Partially Eligible / Missing Requirement**
- **Not Eligible**

The system must explain WHY. Never produce an eligibility verdict without a stated reason tied to the scholarship's actual published criteria.

---

# Primary Users

## Student

Can:
- Build and edit a profile (academic, financial, demographic, geographic)
- View ranked, explained scholarship matches
- See exactly what's missing for partial matches
- Track deadlines and get reminders
- View match history over time (new scholarships added, status changes)

## Institution / Counselor (stretch goal, not required for MVP)

Can:
- View aggregate eligibility gaps across a cohort of students (e.g. "40 students are one document away from qualifying for X")
- Use this to run targeted document drives

The counselor remains responsible for final application guidance and verification.

---

# Product Principles

1. Student-first
2. Explainable AI — no unexplained verdicts
3. Privacy-first, minimal data collection
4. No guaranteed-outcome claims ("you will get this scholarship" is never said)
5. Clear human oversight for final applications
6. Simple, plain language — no bureaucratic jargon
7. Accessible interface (works for first-generation, low-bandwidth users)
8. Every verdict must show its supporting evidence (the actual eligibility clause matched)
9. Missing-requirement guidance must be specific and actionable

---

# Core User Journey

Student opens ScholarPath.
↓
Builds a profile (academic, financial, demographic, geographic) — one-time, editable.
↓
System runs the profile against the scholarship database.
↓
Hard-filter rules engine removes scholarships with clear disqualifiers.
↓
AI ranks and explains remaining scholarships by fit and deadline proximity.
↓
Scholarship Fit Map is generated — ranked list, each with a verdict + reason.
↓
Missing-requirement checklist shown for partial matches.
↓
Deadlines tracked; reminders sent as dates approach.
↓
Profile changes (e.g. new document uploaded, income certificate added) re-trigger matching.

---

# AI Safety

The AI must never say:

- "You will definitely get this scholarship."
- "You are guaranteed to be selected."
- "Don't bother applying — you have no chance." (final competitive outcome is never claimed; the AI only assesses *eligibility*, not *selection odds*.)

Instead use language such as:

- "You meet the published academic and income criteria for this scholarship."
- "You're eligible except for one requirement: a valid caste certificate."
- "This scholarship's deadline is in 9 days."

---

# Technology Direction

**Frontend:**
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui

**Backend:**
- FastAPI
- Python
- PostgreSQL
- SQLAlchemy

**AI:**
- Structured LLM extraction (eligibility-clause parsing + matching)
- Explainable classification (verdict + evidence, never a bare score)
- Human-readable evidence, always traceable to the scholarship's actual text

**Architecture:**

```
Frontend
   ↓
API
   ↓
Authentication
   ↓
Application Services
   ↓
AI Matching Service
   ↓
Database
```
