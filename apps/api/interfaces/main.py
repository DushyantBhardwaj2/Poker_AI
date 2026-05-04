from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.interfaces.game_controller import router as game_router
from apps.api.interfaces.ai_controller import router as ai_router
from apps.api.interfaces.stats_controller import router as stats_router
from packages.domain.database import Base, engine
import os

app = FastAPI(title="PokerSense AI API")

@app.on_event("startup")
def on_startup():
    # Create tables
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error creating database tables: {e}")

# Configure CORS for production
origins = []
origins_raw = os.getenv("ALLOWED_ORIGINS", "")
if origins_raw:
    # Handle multiple origins, whitespace, and trailing slashes
    origins = [o.strip().rstrip('/') for o in origins_raw.split(",") if o.strip()]

# Always include common local development origins for ease of use
dev_origins = [
    "http://localhost:3000",
    "http://localhost:4321",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
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
