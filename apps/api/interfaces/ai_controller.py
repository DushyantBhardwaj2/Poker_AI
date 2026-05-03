import uuid
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from packages.domain.models import Card, GameState, ActionRecord
from packages.ai.win_probability import WinProbabilityCalculator
from packages.ai.move_recommender import MoveRecommender
from packages.ai.opponent_profiler import OpponentProfiler
from packages.ai.feature_mapper import FeatureMapper
from packages.ai.bluff_detector import BluffDetector
from packages.domain.stats_repository import StatsRepository
from packages.domain.database import get_db

router = APIRouter()

# Global detector instance
_bluff_detector = None

def get_bluff_detector():
    global _bluff_detector
    if _bluff_detector is None:
        _bluff_detector = BluffDetector()
    return _bluff_detector

def get_user_id(x_user_id: str = Header(..., alias="X-User-Id", description="User ID for multi-tenant isolation")):
    try:
        uuid.UUID(x_user_id)
        return x_user_id
    except ValueError:
        return "4895a071-3647-4e88-9c45-9e0e247946db"

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

class AnalyzeBluffRequest(BaseModel):
    state: GameState
    history: List[ActionRecord]
    opponent_name: str

class AnalyzeFullRequest(BaseModel):
    state: GameState
    history: List[ActionRecord]
    opponent_name: str
    hole_cards: List[Card]
    num_simulations: int = 1000

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

@router.post("/analyze-bluff")
async def analyze_bluff(
    request: AnalyzeBluffRequest, 
    user_id: str = Header(..., alias="X-User-Id"), 
    db: Session = Depends(get_db),
    detector: BluffDetector = Depends(get_bluff_detector)
):
    try:
        # 1. Fetch Opponent Stats from DB
        repo = StatsRepository(db)
        opponent = repo.get_or_create_opponent(uuid.UUID(user_id), request.opponent_name)
        stats = opponent.stats
        
        features = stats.dynamic_features if stats else {}
        hands = stats.hands_played if stats else 0
        
        vpip = features.get("vpip_count", 0) / hands if hands > 0 else 0.25
        pfr = features.get("pfr_count", 0) / hands if hands > 0 else 0.18
        
        opponent_profile = {
            "vpip": vpip,
            "pfr": pfr
        }
        
        # 2. Map GameState to LiveGameState
        live_state = FeatureMapper.map_to_live_state(
            request.state,
            request.history,
            opponent_profile
        )
        
        # 3. Predict
        prediction = detector.predict(live_state)
        
        return {
            "opponent_name": request.opponent_name,
            "opponent_stats": opponent_profile,
            "prediction": prediction
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from packages.ai.smart_advisor import SmartAdvisor

@router.post("/analyze-full")
async def analyze_full(
    request: AnalyzeFullRequest,
    user_id: str = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db),
    detector: BluffDetector = Depends(get_bluff_detector)
):
    try:
        # 1. Win Probability (Math)
        win_prob_result = WinProbabilityCalculator.calculate(
            request.hole_cards,
            request.state.community_cards,
            len(request.state.players) - 1,
            request.num_simulations
        )
        win_prob = win_prob_result["win_probability"]
        
        # 2. Bluff Analysis (Behavior)
        repo = StatsRepository(db)
        opponent = repo.get_or_create_opponent(uuid.UUID(user_id), request.opponent_name)
        stats = opponent.stats
        features = stats.dynamic_features if stats else {}
        hands = stats.hands_played if stats else 0
        vpip = features.get("vpip_count", 0) / hands if hands > 0 else 0.25
        pfr = features.get("pfr_count", 0) / hands if hands > 0 else 0.18
        opponent_profile = {"vpip": vpip, "pfr": pfr}
        
        live_state = FeatureMapper.map_to_live_state(request.state, request.history, opponent_profile)
        bluff_result = detector.predict(live_state)
        
        # 3. Decision Logic (Synthesis)
        # Determine player context
        active_player = request.state.players[request.state.current_player_index]
        call_amount = request.state.current_bet - active_player.current_bet
        
        advice = SmartAdvisor.recommend(
            win_probability=win_prob,
            bluff_probability=bluff_result["bluff_probability"],
            pot_size=request.state.pot,
            call_amount=call_amount,
            player_stack=active_player.stack
        )
        
        return {
            "win_analysis": win_prob_result,
            "bluff_analysis": bluff_result,
            "advice": advice,
            "opponent_profile": OpponentProfiler.profile(vpip, pfr)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
