from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from backend.config.settings import settings

logger = logging.getLogger("aegisflow.database")

db_url = settings.DATABASE_URL
connect_args = {}

# Handle PostgreSQL connection with fallback to SQLite for development without PostgreSQL running
try:
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    engine = create_engine(db_url, connect_args=connect_args)
    # Test connection
    with engine.connect() as conn:
        pass
except Exception as e:
    logger.info(f"PostgreSQL connection at {db_url} unavailable ({e}). Using local SQLite database (aegisflow.db) for development.")
    fallback_url = "sqlite:///./aegisflow.db"
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
