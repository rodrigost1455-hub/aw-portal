from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Support DATABASE_URL env var (set to /tmp/aw_portal.db on Vercel)
_db_url = os.environ.get("DATABASE_URL")
if not _db_url:
    _base = os.path.dirname(os.path.abspath(__file__))
    _db_url = f"sqlite:///{os.path.join(_base, 'aw_portal.db')}"

SQLALCHEMY_DATABASE_URL = _db_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
