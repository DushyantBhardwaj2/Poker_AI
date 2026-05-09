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
            pass # Skipping SQLite dynamic migrations for brevity since prod is Postgres
        else:
            # PostgreSQL: try adding columns directly, ignore if already exist
            
            # game_sessions
            _add_pg_column_safe(db, "game_sessions", "total_winnings", "FLOAT DEFAULT 0.0")
            _add_pg_column_safe(db, "game_sessions", "ended_at", "TIMESTAMPTZ")
            
            # hand_history
            _add_pg_column_safe(db, "hand_history", "tactical_data", "JSONB")
            _add_pg_column_safe(db, "hand_history", "leak_detected", "BOOLEAN DEFAULT FALSE")
            _add_pg_column_safe(db, "hand_history", "leak_description", "TEXT")
            
            # opponents
            _add_pg_column_safe(db, "opponents", "notes", "TEXT DEFAULT ''")
            _add_pg_column_safe(db, "opponents", "playstyle_archetype", "TEXT DEFAULT 'Unknown'")
            _add_pg_column_safe(db, "opponents", "last_seen", "TIMESTAMPTZ DEFAULT NOW()")
            
            # opponent_stats
            _add_pg_column_safe(db, "opponent_stats", "last_hand_timestamp", "TIMESTAMPTZ")
            _add_pg_column_safe(db, "opponent_stats", "session_features", "JSONB DEFAULT '{\"hands_played\": 0, \"vpip_count\": 0, \"pfr_count\": 0, \"session_bets\": 0.0, \"session_calls\": 0.0, \"cbet_count\": 0, \"three_bet_count\": 0, \"recent_history\": []}'::jsonb")
            _add_pg_column_safe(db, "opponent_stats", "reliability_score", "TEXT DEFAULT 'Low'")
            _add_pg_column_safe(db, "opponent_stats", "behavioral_description", "TEXT DEFAULT 'Unknown'")

        db.commit()
        logger.info("Column migrations completed")
    except Exception as e:
        logger.error(f"Column migration failed: {e}")
        db.rollback()
    finally:
        db.close()

def _add_pg_column_safe(db, table, column, definition):
    try:
        db.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
        logger.info(f"Added {column} column to {table}")
    except Exception as e:
        db.rollback()
        if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
            pass # logger.info(f"{column} column already exists in {table}")
        else:
            logger.warning(f"Could not add {column} to {table}: {e}")

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
