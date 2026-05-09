import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Neon Serverless-specific configuration for cold start handling
    # pool_pre_ping: Tests connection before use (catches dead connections after idle)
    # pool_size + max_overflow: Limits connections to avoid overwhelming serverless
    # pool_recycle: Recycles connections before Neon closes them (~300s idle)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=3,
        pool_recycle=280,  # Recycle before Neon's 5-min idle timeout
        pool_timeout=30   # Wait up to 30s for connection
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
