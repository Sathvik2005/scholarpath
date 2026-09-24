from datetime import datetime, timedelta

from app.core.database import SessionLocal, engine, Base
from app.models.models import Scholarship

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    # Upsert on every start so demo deadlines stay relative to today.

    now = datetime.utcnow()

    scholarships = [
        Scholarship(
            id="sch_001",
            name="Post-Matric Scholarship for OBC Students",
            provider="Ministry of Social Justice and Empowerment",
            provider_type="government",
            eligibility_criteria_text=(
                "Open to OBC students enrolled in undergraduate or postgraduate programs. "
                "Household income must not exceed Rs 2,50,000 per annum. A valid OBC caste "
                "certificate is required. Open to residents of all states."
            ),
            structured_criteria={
                "categories": ["OBC"],
                "max_income_bracket": "under_2.5L",
                "academic_text": "Open to OBC students enrolled in undergraduate or postgraduate programs.",
                "financial_text": "Household income must not exceed Rs 2,50,000 per annum.",
                "demographic_text": "A valid OBC caste certificate is required.",
                "geographic_text": "Open to residents of all states.",
            },
            required_documents=["OBC_certificate", "income_certificate", "aadhaar"],
            deadline=now + timedelta(days=9),
            amount="Up to ₹20,000/year",
            source_url="https://scholarships.gov.in",
        ),
        Scholarship(
            id="sch_002",
            name="Tamil Nadu State Merit-cum-Means Scholarship",
            provider="Government of Tamil Nadu",
            provider_type="state",
            eligibility_criteria_text=(
                "Available to students residing in Tamil Nadu and enrolled in B.Tech or B.Sc "
                "programs. Household income must not exceed Rs 2,50,000 per annum. No caste "
                "restriction."
            ),
            structured_criteria={
                "states": ["Tamil Nadu"],
                "courses": ["B.Tech", "B.Sc"],
                "max_income_bracket": "under_2.5L",
                "academic_text": "Enrolled in B.Tech or B.Sc programs.",
                "financial_text": "Household income must not exceed Rs 2,50,000 per annum.",
                "geographic_text": "Available to students residing in Tamil Nadu.",
            },
            required_documents=["income_certificate", "aadhaar", "bonafide_certificate"],
            deadline=now + timedelta(days=21),
            amount="₹15,000/year",
            source_url="https://tnscholarship.tn.gov.in",
        ),
        Scholarship(
            id="sch_003",
            name="Reliance Foundation Undergraduate Scholarship",
            provider="Reliance Foundation",
            provider_type="private",
            eligibility_criteria_text=(
                "Open to undergraduate students across all courses and states. Household income "
                "must not exceed Rs 5,00,000 per annum. No category restriction."
            ),
            structured_criteria={
                "max_income_bracket": "2.5L_5L",
                "financial_text": "Household income must not exceed Rs 5,00,000 per annum.",
            },
            required_documents=["income_certificate", "aadhaar", "bank_passbook"],
            deadline=now + timedelta(days=45),
            amount="Up to ₹2,00,000 total",
            source_url="https://www.reliancefoundation.org/scholarships",
        ),
        Scholarship(
            id="sch_004",
            name="Top Class Education Scheme for SC Students",
            provider="Ministry of Social Justice and Empowerment",
            provider_type="government",
            eligibility_criteria_text=(
                "Open exclusively to SC students admitted to notified premier institutions for "
                "undergraduate or postgraduate courses. Household income must not exceed Rs "
                "6,00,000 per annum. A valid SC caste certificate is required."
            ),
            structured_criteria={
                "categories": ["SC"],
                "max_income_bracket": "above_5L",
                "demographic_text": "A valid SC caste certificate is required.",
                "financial_text": "Household income must not exceed Rs 6,00,000 per annum.",
            },
            required_documents=["SC_certificate", "income_certificate", "admission_letter"],
            deadline=now + timedelta(days=5),
            amount="Full tuition + maintenance allowance",
            source_url="https://scholarships.gov.in",
        ),
        Scholarship(
            id="sch_005",
            name="Rural Girl Child STEM Scholarship",
            provider="SNS Educational Trust",
            provider_type="institutional",
            eligibility_criteria_text=(
                "Open to female students from rural areas enrolled in STEM undergraduate "
                "programs. No income restriction. Open to all states."
            ),
            structured_criteria={
                "genders": ["female"],
                "area_types": ["rural"],
                "academic_text": "Enrolled in STEM undergraduate programs.",
                "demographic_text": "Open to female students from rural areas.",
                "geographic_text": "Open to female students from rural areas.",
            },
            required_documents=["aadhaar", "bonafide_certificate"],
            deadline=now + timedelta(days=60),
            amount="₹10,000/year",
            source_url="https://snscet.org/scholarships",
        ),
    ]

    for s in scholarships:
        db.merge(s)
    db.commit()
    db.close()


if __name__ == "__main__":
    seed()
