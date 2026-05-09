from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asgi_correlation_id import CorrelationIdMiddleware
from apps.api.interfaces.game_controller import router as game_router
from apps.api.interfaces.ai_controller import router as ai_router
from apps.api.interfaces.stats_controller import router as stats_router
from apps.api.infrastructure.logger import setup_logging, get_logger
from packages.domain.database import Base, engine, SessionLocal
from sqlalchemy import text
import os

# Initialize structured logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="PokerSense AI API")

# Add Correlation ID Middleware
app.add_middleware(CorrelationIdMiddleware)

@app.on_event("startup")
def on_startup():
    # Create tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully")
    except Exception as e:
        logger.error("Error creating database tables", error=str(e))

    # Run migrations for missing columns
    _run_column_migrations()


def _run_column_migrations():
    """Add missing columns to existing tables"""
    from packages.domain.database import is_sqlite
    db = SessionLocal()
    try:
        if is_sqlite:
            # SQLite: use PRAGMA to check columns
            result = db.execute(text("PRAGMA table_info(game_sessions)"))
            columns = [row[1] for row in result.fetchall()]

            if 'total_winnings' not in columns:
                db.execute(text("ALTER TABLE game_sessions ADD COLUMN total_winnings FLOAT DEFAULT 0.0"))
                logger.info("Added total_winnings column to game_sessions")

            if 'ended_at' not in columns:
                db.execute(text("ALTER TABLE game_sessions ADD COLUMN ended_at TIMESTAMP"))
                logger.info("Added ended_at column to game_sessions")
        else:
            # PostgreSQL: try adding columns directly, ignore if already exist
            try:
                db.execute(text("ALTER TABLE game_sessions ADD COLUMN total_winnings FLOAT DEFAULT 0.0"))
                logger.info("Added total_winnings column to game_sessions")
            except Exception as e:
                db.rollback()
                if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("total_winnings column already exists")
                else:
                    logger.warning(f"Could not add total_winnings: {e}")

            try:
                db.execute(text("ALTER TABLE game_sessions ADD COLUMN ended_at TIMESTAMPTZ"))
                logger.info("Added ended_at column to game_sessions")
            except Exception as e:
                db.rollback()
                if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("ended_at column already exists")
                else:
                    logger.warning(f"Could not add ended_at: {e}")

        db.commit()
        logger.info("Column migrations completed")
    except Exception as e:
        logger.error(f"Column migration failed: {e}")
        db.rollback()
    finally:
        db.close()

# Configure CORS for production
origins = []
origins_raw = os.getenv("ALLOWED_ORIGINS", "")
if origins_raw:
    # Handle multiple origins, whitespace, and trailing slashes
    origins = [o.strip().rstrip('/') for o in origins_raw.split(",") if o.strip()]

# Always include common local development origins for ease of use
dev_origins = [
    "http://localhost:3000",
    "http://localhost:4231",
    "http://localhost:4321",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:4231",
    "http://127.0.0.1:4321",
    "http://127.0.0.1:5173",
    "https://poker-ai-black.vercel.app",
]
for origin in dev_origins:
    if origin not in origins:
        origins.append(origin)

# If "*" is in origins, we must set allow_credentials=False
allow_all = "*" in origins
if allow_all:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        # Allow Vercel preview deployments
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "X-User-Id"],
    )

# Health check endpoint for deployment
@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(game_router, prefix="/api/v1/game", tags=["game"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(stats_router, prefix="/api/v1/stats", tags=["stats"])

@app.get("/")
def root():
    return {"message": "Welcome to PokerSense AI API"}
