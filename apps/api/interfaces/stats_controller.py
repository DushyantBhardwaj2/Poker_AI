from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from packages.domain.database import get_db
from packages.domain.stats_repository import StatsRepository
from packages.ai.opponent_profiler import OpponentProfiler

router = APIRouter()

@router.get("/")
def get_all_stats(db: Session = Depends(get_db)):
    repo = StatsRepository(db)
    try:
        stats = repo.get_all_stats()
        # Enrich with AI profile
        for name, stat in stats.items():
            profile = OpponentProfiler.profile(stat["vpip"], stat["pfr"])
            stat["classification"] = profile["classification"]
            stat["description"] = profile["description"]
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
