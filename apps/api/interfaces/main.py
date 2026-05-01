from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.interfaces.game_controller import router as game_router
from apps.api.interfaces.ai_controller import router as ai_router
from apps.api.interfaces.stats_controller import router as stats_router
from packages.domain.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PokerSense AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_router, prefix="/api/v1/game", tags=["game"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(stats_router, prefix="/api/v1/stats", tags=["stats"])

@app.get("/")
def root():
    return {"message": "Welcome to PokerSense AI API"}
