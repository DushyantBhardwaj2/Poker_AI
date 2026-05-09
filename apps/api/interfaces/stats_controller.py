import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from packages.domain.database import get_db
from packages.domain.stats_repository import StatsRepository
from apps.api.infrastructure.auth import get_current_user_id

router = APIRouter()


# Request/Response Models
class UpdateStatsRequest(BaseModel):
    player_name: str
    vpip_this_hand: bool
    pfr_this_hand: bool
    is_bluff: bool = False
    made_cbet: bool = False
    cbet_succeeded: bool = False
    made_three_bet: bool = False
    three_bet_succeeded: bool = False
    fold_to_river: bool = False
    called_showdown: bool = False
    won_showdown: bool = False
    bet_amount: float = 0
    call_amount: float = 0


class InitializePlayerRequest(BaseModel):
    player_name: str
    active_player_names: Optional[List[str]] = None


class UpdateNotesRequest(BaseModel):
    player_name: str
    notes: str


# Endpoints
@router.get("/")
def get_all_stats(user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get all opponent stats with enhanced Phase 3 metrics"""
    repo = StatsRepository(db)
    try:
        return repo.get_all_stats(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
def get_recent_opponents(
    limit: int = 10,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get list of most recently played opponents"""
    repo = StatsRepository(db)
    try:
        return repo.get_recent_opponents(user_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/player/{player_name}")
def get_opponent_profile(
    player_name: str,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get detailed profile for a single opponent including session vs baseline"""
    repo = StatsRepository(db)
    try:
        profile = repo.get_opponent_profile(user_id, player_name)
        if not profile:
            raise HTTPException(status_code=404, detail="Opponent not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update_stats")
def update_player_stats(
    request: UpdateStatsRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update player stats after a hand (Phase 3 enhanced tracking)"""
    repo = StatsRepository(db)
    try:
        stats = repo.update_player_stats(
            user_id=user_id,
            name=request.player_name,
            vpip_this_hand=request.vpip_this_hand,
            pfr_this_hand=request.pfr_this_hand,
            is_bluff=request.is_bluff,
            made_cbet=request.made_cbet,
            cbet_succeeded=request.cbet_succeeded,
            made_three_bet=request.made_three_bet,
            three_bet_succeeded=request.three_bet_succeeded,
            fold_to_river=request.fold_to_river,
            called_showdown=request.called_showdown,
            won_showdown=request.won_showdown,
            bet_amount=request.bet_amount,
            call_amount=request.call_amount
        )
        return {"status": "success", "hands_played": stats.hands_played}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notes")
def update_opponent_notes(
    request: UpdateNotesRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update notes for an opponent"""
    repo = StatsRepository(db)
    try:
        success = repo.update_opponent_notes(user_id, request.player_name, request.notes)
        if not success:
            raise HTTPException(status_code=404, detail="Opponent not found")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize_player")
def initialize_player(
    request: InitializePlayerRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Initialize a new opponent with table-averaged baseline stats"""
    repo = StatsRepository(db)
    try:
        opponent = repo.get_or_create_opponent(
            user_id=user_id,
            player_name=request.player_name,
            active_table_names=request.active_player_names
        )
        return {
            "status": "success",
            "player_name": opponent.player_name,
            "hands_played": opponent.stats.hands_played if opponent.stats else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset_session")
def reset_session_stats(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Reset session-only stats for fresh baseline comparison"""
    repo = StatsRepository(db)
    try:
        repo.reset_session_stats(user_id)
        return {"status": "success", "message": "Session stats reset for baseline comparison"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Phase 6: Session Analytics & Post-Game Review ---

class RecordHandResultRequest(BaseModel):
    hand_id: Optional[str] = None
    session_id: Optional[str] = None
    result: str  # win, loss, tie
    amount_won: float = 0
    street: str
    action_count: int = 0
    duration_seconds: int = 0
    pot_size: float = 0
    your_cards: Optional[List[dict]] = None
    community_cards: Optional[List[dict]] = None
    tactical_data: Optional[dict] = None


@router.post("/hand_result")
def record_hand_result(
    request: RecordHandResultRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Record the result of a hand for session analytics and leak detection"""
    repo = StatsRepository(db)
    try:
        # Get or create session
        session_id = uuid.UUID(request.session_id) if request.session_id else None
        if not session_id:
            # Create a new session if none provided
            session = repo.create_session(user_id, "Quick Session")
            session_id = session.session_id

        hand = repo.record_hand_result(
            user_id=user_id,
            session_id=session_id,
            street=request.street,
            pot_size=request.pot_size,
            your_cards=request.your_cards,
            community_cards=request.community_cards,
            result=request.result,
            amount_won=request.amount_won,
            action_count=request.action_count,
            duration_seconds=request.duration_seconds,
            tactical_data=request.tactical_data
        )
        return {"status": "success", "hand_id": str(hand.hand_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def get_hand_history(
    limit: int = 50,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get hand history across all sessions"""
    repo = StatsRepository(db)
    try:
        return repo.get_hand_history(user_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/analytics")
def get_session_analytics(
    session_id: str,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get comprehensive session analytics"""
    repo = StatsRepository(db)
    try:
        if session_id == "latest":
            return repo.get_session_analytics(user_id, None)
        session_uuid = uuid.UUID(session_id)
        return repo.get_session_analytics(user_id, session_uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/latest/analytics")
def get_latest_session_analytics(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get analytics for the most recent session"""
    repo = StatsRepository(db)
    try:
        return repo.get_session_analytics(user_id, None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/end")
def end_session(
    session_id: str,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Mark a session as ended"""
    repo = StatsRepository(db)
    try:
        session_uuid = uuid.UUID(session_id)
        success = repo.end_session(user_id, session_uuid)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "success", "message": f"Session {session_id} ended"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))