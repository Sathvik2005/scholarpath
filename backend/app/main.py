from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.api import profile, scholarships, matches, deadlines, documents
from app import seed as seed_module

Base.metadata.create_all(bind=engine)
seed_module.seed()

app = FastAPI(title="ScholarPath API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo only -- restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router)
app.include_router(scholarships.router)
app.include_router(matches.router)
app.include_router(deadlines.router)
app.include_router(documents.router)


@app.get("/health")
def health():
    return {"status": "ok"}
