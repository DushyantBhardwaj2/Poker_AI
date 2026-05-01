from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from packages.domain.models import Card
from packages.ai.win_probability import WinProbabilityCalculator
from packages.ai.move_recommender import MoveRecommender
from packages.ai.opponent_profiler import OpponentProfiler

router = APIRouter()

class WinProbRequest(BaseModel):
    hole_cards: List[Card]
    community_cards: List[Card] = []
    num_opponents: int
    num_simulations: int = 1000

class MoveRecRequest(BaseModel):
    win_probability: float
    pot_size: float
    call_amount: float
    player_stack: float

class ProfileRequest(BaseModel):
    vpip: float
    pfr: float

@router.post("/win-probability")
async def get_win_probability(request: WinProbRequest):
    try:
        result = WinProbabilityCalculator.calculate(
            request.hole_cards,
            request.community_cards,
            request.num_opponents,
            request.num_simulations
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/recommend-move")
async def get_move_recommendation(request: MoveRecRequest):
    try:
        result = MoveRecommender.recommend(
            request.win_probability,
            request.pot_size,
            request.call_amount,
            request.player_stack
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/profile-opponent")
async def profile_opponent(request: ProfileRequest):
    try:
        result = OpponentProfiler.profile(request.vpip, request.pfr)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
