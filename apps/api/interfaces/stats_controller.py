import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from packages.domain.database import get_db
from packages.domain.stats_repository import StatsRepository
from packages.ai.opponent_profiler import OpponentProfiler
from packages.domain.db_models import Opponent, OpponentStats
from apps.api.infrastructure.auth import get_current_user_id

router = APIRouter()

@router.get("/")
def get_all_stats(user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    repo = StatsRepository(db)
    try:
        # raw stats from repository
        raw_results = db.query(Opponent, OpponentStats).join(OpponentStats).filter(
            Opponent.user_id == str(user_id)
        ).all()
        
        enriched_stats = {}
        for opp, stats in raw_results:
            hands = stats.hands_played
            features = stats.dynamic_features or {}
            
            vpip_count = features.get("vpip_count", 0)
            pfr_count = features.get("pfr_count", 0)
            bluffs = features.get("strict_bluff_showdowns", 0)
            agg_ip = features.get("aggression_ip", 0.0)
            agg_oop = features.get("aggression_oop", 0.0)
            
            vpip = vpip_count / hands if hands > 0 else 0.0
            pfr = pfr_count / hands if hands > 0 else 0.0
            
            # Step 6: Compute metrics
            aggression_score = (agg_ip + agg_oop) / max(1, hands)
            bluff_frequency = bluffs / max(1, hands)
            
            profile = OpponentProfiler.profile(vpip, pfr)
            
            enriched_stats[opp.player_name] = {
                "hands_played": hands,
                "vpip_percentage": round(vpip * 100, 2),
                "pfr_percentage": round(pfr * 100, 2),
                "aggression_score": round(aggression_score, 2),
                "bluff_frequency": round(bluff_frequency, 2),
                "classification": profile["classification"],
                "description": profile["description"]
            }
        return enriched_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class InitializePlayerRequest(BaseModel):
    player_name: str
    active_player_names: List[str]

@router.post("/initialize_player")
def initialize_player(request: InitializePlayerRequest, user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    repo = StatsRepository(db)
    try:
        # Check if already exists
        opponent = db.query(Opponent).filter(
            Opponent.user_id == str(user_id),
            Opponent.player_name == request.player_name
        ).first()

        if not opponent:
            # Step 7: Cold Start - get table averages
            baseline_features = repo.get_table_averaged_baseline(user_id, request.active_player_names)
            
            opponent = Opponent(user_id=str(user_id), player_name=request.player_name)
            db.add(opponent)
            db.flush()
            
            # Initialize with table averages
            stats = OpponentStats(
                opponent_id=opponent.opponent_id,
                hands_played=1, # Give it 1 hand so math works without zero division
                dynamic_features=baseline_features
            )
            db.add(stats)
            db.commit()
            return {"status": "success", "message": "Player initialized with table baseline", "features": baseline_features}
        else:
            return {"status": "skipped", "message": "Player already exists"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
