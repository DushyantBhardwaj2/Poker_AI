import uuid
import time
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
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
from apps.api.infrastructure.auth import get_current_user_id
from apps.api.infrastructure.logger import get_logger
import structlog

router = APIRouter()
logger = get_logger(__name__)

# Pipeline timeout configuration (per Section 12: P95 < 500ms target)
PIPELINE_TIMEOUT_MS = 450  # 450ms timeout before fallback
ANALYSIS_TIMEOUT_MS = 200  # 200ms for bluff detection

# Global detector instance
_bluff_detector = None

def get_bluff_detector():
    global _bluff_detector
    if _bluff_detector is None:
        try:
            _bluff_detector = BluffDetector()
        except Exception as e:
            logger.error("Failed to initialize BluffDetector", error=str(e))
            raise HTTPException(status_code=500, detail=f"ML Initialization Error: {str(e)}")
    return _bluff_detector

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
    user_id: uuid.UUID = Depends(get_current_user_id), 
    db: Session = Depends(get_db),
    detector: BluffDetector = Depends(get_bluff_detector)
):
    try:
        # 1. Fetch Opponent Stats from DB
        repo = StatsRepository(db)
        opponent = repo.get_or_create_opponent(user_id, request.opponent_name)
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
from packages.ai.pipeline import run_advisor_pipeline, ValidationError as PipelineValidationError

@router.post("/analyze-full")
@router.post("/analyze-full/")
async def analyze_full(
    request: AnalyzeFullRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    detector: BluffDetector = Depends(get_bluff_detector)
):
    # Bind context to the logger for this request
    log = logger.bind(user_id=str(user_id), opponent_name=request.opponent_name)
    log.info("Starting full analysis", round=request.state.round)

    try:
        # Track timing for performance monitoring
        start_time = time.time()

        # 1. Win Probability (Math)
        win_prob_result = WinProbabilityCalculator.calculate(
            request.hole_cards,
            request.state.community_cards,
            len(request.state.players) - 1,
            request.num_simulations
        )
        win_prob = win_prob_result["win_probability"]

        # 2. Bluff Analysis (Behavior) with timeout
        repo = StatsRepository(db)
        opponent = repo.get_or_create_opponent(user_id, request.opponent_name)
        stats = opponent.stats
        features = stats.dynamic_features if stats else {}
        hands = stats.hands_played if stats else 0
        vpip = features.get("vpip_count", 0) / hands if hands > 0 else 0.25
        pfr = features.get("pfr_count", 0) / hands if hands > 0 else 0.18
        opponent_profile = {"vpip": vpip, "pfr": pfr}

        #Bluff detection with timeout protection (Section 12: Non-Blocking)
        bluff_result = {"bluff_probability": 0.15}  # Default baseline
        try:
            # Check if we're within time budget
            elapsed = (time.time() - start_time) * 1000
            if elapsed < ANALYSIS_TIMEOUT_MS:
                live_state = FeatureMapper.map_to_live_state(request.state, request.history, opponent_profile)
                bluff_result = detector.predict(live_state)
        except Exception as bd_err:
            log.warning("Bluff detection timed out or failed, using baseline", error=str(bd_err))

        # 3. Determine player context
        active_player = request.state.players[request.state.current_player_index]
        call_amount = request.state.current_bet - active_player.current_bet

        # 4. Get opponent profile for archetype
        profile = repo.get_opponent_profile(user_id, request.opponent_name)
        archetype = profile.get("archetype") if profile else "Unknown"

        # 5. Estimate completeness
        completeness = min(1.0, len(request.history) / 10.0) if request.history else 0.5

        # 6. Try Pipeline First with timeout (Primary), Fallback to SmartAdvisor
        pipelineucceeded = False
        pipeline_errors = []
        degrade_mode = False

        try:
            # Check time budget before pipeline
            elapsed = (time.time() - start_time) * 1000
            if elapsed > PIPELINE_TIMEOUT_MS:
                raise PipelineValidationError("Pipeline timeout exceeded")

            # Convert request state to dict format for pipeline
            raw_state_dict = request.state.model_dump() if hasattr(request.state, 'model_dump') else request.state.dict()

            # Run the deterministic pipeline
            advice, pipeline_errors = run_advisor_pipeline(
                raw_state=raw_state_dict,
                history=[h.model_dump() if hasattr(h, 'model_dump') else h.dict() for h in request.history],
                hole_cards=request.hole_cards,
                community_cards=request.state.community_cards,
                win_probability=win_prob,
                pot_size=request.state.pot,
                call_amount=call_amount,
                player_stack=active_player.stack,
                sample_size=hands,
                data_completeness=completeness,
                opponent_archetype=archetype,
                vpip=vpip,
                pfr=pfr
            )
            pipelineucceeded = True
            log.info("Pipeline executed successfully", action=advice.action, errors=pipeline_errors)

        except PipelineValidationError as pe:
            # Pipeline validation failed - fall back to SmartAdvisor
            log.warning("Pipeline validation failed, falling back to SmartAdvisor", error=str(pe))
            pipeline_errors.append(f"Pipeline validation: {str(pe)}")
            degrade_mode = True
            advice = SmartAdvisor.recommend(
                win_probability=win_prob,
                bluff_probability=bluff_result["bluff_probability"],
                pot_size=request.state.pot,
                call_amount=call_amount,
                player_stack=active_player.stack,
                opponent_sample_size=hands,
                data_completeness=completeness,
                opponent_archetype=archetype,
                is_shifting=profile.get("is_shifting", False) if profile else False,
                shift_direction=profile.get("shift_direction", "stable") if profile else "stable"
            )
        except Exception as e:
            # Pipeline execution failed - fall back to SmartAdvisor
            log.warning("Pipeline execution failed, falling back to SmartAdvisor", error=str(e))
            pipeline_errors.append(f"Pipeline error: {str(e)}")
            degrade_mode = True
            advice = SmartAdvisor.recommend(
                win_probability=win_prob,
                bluff_probability=bluff_result["bluff_probability"],
                pot_size=request.state.pot,
                call_amount=call_amount,
                player_stack=active_player.stack,
                opponent_sample_size=hands,
                data_completeness=completeness,
                opponent_archetype=archetype,
                is_shifting=profile.get("is_shifting", False) if profile else False,
                shift_direction=profile.get("shift_direction", "stable") if profile else "stable"
            )

        log.info("Analysis complete", method="pipeline" if pipelineucceeded else "smart_advisor",
                advice=advice.action, confidence=advice.confidence_level)

        return {
            "win_analysis": win_prob_result,
            "bluff_analysis": bluff_result,
            "advice": advice,
            "opponent_profile": profile or opponent_profile,
            "pipeline_used": pipelineucceeded,
            "pipeline_errors": pipeline_errors,
            "degrade_mode": degrade_mode,  # Section 12: Indicates simplified response
            "timing_ms": int((time.time() - start_time) * 1000)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        log.error("Analysis failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
