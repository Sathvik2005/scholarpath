import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Vercel (and most serverless platforms) only allow writes under /tmp, and
# that /tmp is wiped on every cold start -- so on Vercel this database is
# demo-persistent (survives while the function instance stays warm) but not
# durable storage. Locally it's a normal file next to the app, persisting
# across restarts like any other dev database. See README's "Deploying to
# Vercel" section for the upgrade path to a real hosted database.
if os.environ.get("VERCEL"):
    DATABASE_URL = "sqlite:////tmp/scholarpath.db"
else:
    DATABASE_URL = "sqlite:///./scholarpath.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
