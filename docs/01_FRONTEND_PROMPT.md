You are a senior frontend engineer and ed-tech UX designer.

Build the frontend for ScholarPath.

ScholarPath is a platform that matches students to scholarships they are eligible for, explains why, flags missing requirements, and tracks deadlines.

This is NOT an application-submission platform and does NOT guarantee selection outcomes.

---

# TECH STACK

Use:

- Next.js latest stable version
- TypeScript
- Tailwind CSS
- shadcn/ui
- Lucide icons
- React Hook Form
- Zod
- TanStack Query
- Recharts

Use a clean modular architecture.

---

# DESIGN DIRECTION

The product should feel:

- trustworthy
- encouraging (not bureaucratic)
- clear and simple
- accessible to first-generation and low-bandwidth users
- modern but not flashy

Avoid:

- excessive gradients or glassmorphism
- neon colors
- crowded dashboards
- generic AI chatbot aesthetics
- anything that feels like a government form

Prioritize:

- whitespace and hierarchy
- large readable typography
- simple cards
- plain-language explanations over jargon

---

# APPLICATION STRUCTURE

Create:

```
/app
  /(public)
    /page.tsx
    /about
  /(auth)
    /login
    /register
  /(student)
    /dashboard
    /profile
    /matches
    /matches/[id]
    /deadlines
  /(counselor)          # stretch goal, build last
    /dashboard
    /students
```

---

# LANDING PAGE

Create a minimal landing page.

Hero:

"Find every scholarship you actually qualify for."

Subtext:

"ScholarPath matches you to scholarships, explains your eligibility, and tracks every deadline — so you never lose funding to paperwork or missed dates."

CTA: "Build My Profile"
Secondary CTA: "How It Works"

Include sections:

1. The Problem (students eligible but not receiving aid — cite the stat: 98% eligible, 1 in 3 never receive it)
2. The Scholarship Fit Map (visual preview)
3. How It Works (Profile → Match → Explain → Track)
4. Trust/Safety statement (no guaranteed outcomes, your data stays private)

Do not oversell AI or promise results.

---

# STUDENT DASHBOARD

Show:

Greeting: "Hi [Name], here's where you stand."

Primary CTA: "View My Matches" (or "Complete Your Profile" if incomplete)

## ScholarPath Overview

Display counts: Eligible matches / Partial matches (missing something) / Upcoming deadlines (next 14 days)

## Scholarship Fit Map

Signature visualization. For the student's top matches, show a compact grid/list of scholarships, each tagged:

- 🟢 Eligible
- 🟡 Partially Eligible — missing X
- 🔴 Not Eligible (collapsed/hidden by default, expandable)

Clicking a scholarship should show:

- Which dimensions matched (Academic / Financial / Demographic / Geographic / Documentation / Deadline)
- The exact reason for each verdict, quoting the relevant published eligibility clause
- What's missing, if partial
- Deadline and days remaining

Never display a verdict without a reason.

---

# PROFILE BUILDER

Must feel like a short, respectful form — not a bureaucratic one.

Use a stepper, not one giant form:

Step 1 — Academic: course, year/level, marks or GPA band
Step 2 — Financial: household income bracket (ranges, not exact figures required)
Step 3 — Demographic: category, gender, disability status, minority status (all optional/skippable, clearly marked why they're asked)
Step 4 — Geographic: state, rural/urban, institution type
Step 5 — Documents on hand (checklist: caste certificate, income certificate, Aadhaar, bank account, etc.)

Every optional/sensitive field must have a one-line "why we ask" note and a skip option.

---

# MATCH RESULTS PAGE

For a single scholarship, show:

"Your Eligibility" — dimension-by-dimension breakdown with verdict + evidence quote from the scholarship's actual criteria

"What's Missing" — specific, actionable items (e.g. "Upload a valid income certificate dated within the last 6 months")

"Deadline" — countdown + add-to-calendar action

Never provide selection-odds predictions.

---

# DEADLINE TRACKER

Timeline view, soonest first. Highlight anything within 14 days. Allow marking a scholarship as "Applied" / "Not Interested".

---

# COMPONENT ARCHITECTURE

Create reusable components:

```
components/
  ui/
  scholarpath/
    ScholarshipCard
    FitDimensionBadge
    FitMap
    ProfileStepper
    EvidencePanel
    MissingRequirementChecklist
    DeadlineTimeline
    MatchExplanationPanel
```

---

# RESPONSIVENESS

Mobile-first. The profile builder and match results must work exceptionally well on mobile — many target users are mobile-only.

---

# ACCESSIBILITY

Implement:

- keyboard navigation
- semantic HTML
- proper labels
- visible focus states
- sufficient contrast
- screen reader support
- support for slow/low-bandwidth connections (avoid heavy client bundles)

---

# MOCK DATA

Initially create realistic mock data: 15–20 mock scholarships spanning government, state, private, and institutional sources, with varied eligibility criteria, and 2–3 mock student profiles producing different match outcomes (fully eligible, partial, ineligible).

Do not use real student information.

---

# API LAYER

Create:

```
lib/api/
  auth.ts
  profile.ts
  scholarships.ts
  matches.ts
  deadlines.ts
```

Use typed API responses. Prepare for FastAPI backend integration.

---

# QUALITY

Before finishing:

- run TypeScript checks
- remove dead code
- avoid duplicated components
- handle loading, error, and empty states
- Create a README explaining installation, environment variables, architecture, and routes
