import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
import app.models.user
import app.models.refresh_token
import app.models.audit_log
import app.models.document
import app.models.processing_job
import app.models.deed


from app.utils.paths import BACKEND_DIR

raw_db_url = os.getenv("DATABASE_URL", "sqlite:///./plotproof.db")
if raw_db_url in ("sqlite:///./plotproof.db", "sqlite:///plotproof.db"):
    db_file = (BACKEND_DIR / "plotproof.db").as_posix()
    DATABASE_URL = f"sqlite:///{db_file}"
else:
    DATABASE_URL = raw_db_url


# Handle SQLite vs PostgreSQL arguments
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
