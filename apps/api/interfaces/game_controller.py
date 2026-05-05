import uuid
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from packages.domain.models import GameSession, ActionRecord, GameRound, ActionType, Player, Card, GameState, HandRank
from packages.domain.hand_evaluator import HandEvaluator
from packages.domain.database import get_db
from packages.domain.stats_repository import StatsRepository
from apps.api.infrastructure.auth import get_current_user_id

router = APIRouter()

# In-memory store for game sessions
active_sessions: Dict[str, GameSession] = {}

class StartSessionRequest(BaseModel):
    pass

@router.post("/session/start")
async def start_session(user_id: uuid.UUID = Depends(get_current_user_id)):
    session = GameSession(user_id=str(user_id))
    active_sessions[session.session_id] = session
    return {"session_id": session.session_id}

class AddPlayerRequest(BaseModel):
    session_id: str
    player_name: str
    stack: float

@router.post("/session/add_player")
async def add_player(request: AddPlayerRequest, user_id: uuid.UUID = Depends(get_current_user_id)):
    session = active_sessions.get(request.session_id)
    if not session or session.user_id != str(user_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    player = Player(name=request.player_name, stack=request.stack)
    session.players.append(player)
    return {"status": "success", "players": [p.name for p in session.players]}

class DealCardsRequest(BaseModel):
    session_id: str
    player_name: str
    cards: List[Card]

@router.post("/session/deal_cards")
async def deal_cards(request: DealCardsRequest, user_id: uuid.UUID = Depends(get_current_user_id)):
    session = active_sessions.get(request.session_id)
    if not session or session.user_id != str(user_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    for player in session.players:
        if player.name == request.player_name:
            player.hole_cards = request.cards
            return {"status": "success"}
    raise HTTPException(status_code=404, detail="Player not found in session")

class RecordActionRequest(BaseModel):
    session_id: str
    player_name: str
    action_type: ActionType
    amount: float = 0.0

@router.post("/session/record_action")
async def record_action(request: RecordActionRequest, user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    session = active_sessions.get(request.session_id)
    if not session or session.user_id != str(user_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update session state
    action_record = ActionRecord(
        player_name=request.player_name,
        action_type=request.action_type,
        amount=request.amount,
        street=session.current_street
    )
    session.actions_history.append(action_record)
    session.pot_size += request.amount
    
    # Update player state
    player_found = False
    for player in session.players:
        if player.name == request.player_name:
            player_found = True
            if request.action_type in [ActionType.CALL, ActionType.RAISE, ActionType.ALL_IN]:
                if session.current_street == GameRound.PRE_FLOP:
                    if request.action_type in [ActionType.RAISE, ActionType.ALL_IN]:
                        player.pfr_this_hand = True
                    player.vpip_this_hand = True
    
    if not player_found:
        raise HTTPException(status_code=404, detail="Player not found in session")

    # Update ML Features in DB
    repo = StatsRepository(db)
    
    # Track actions directly for features
    opponent = repo.get_or_create_opponent(user_id, request.player_name)
    stats = opponent.stats
    features = dict(stats.dynamic_features) if stats.dynamic_features else {}
    
    # VPIP / PFR logic (updated per action, though typically counted per hand. We do it here per prompt)
    if session.current_street == GameRound.PRE_FLOP:
        if request.action_type in [ActionType.RAISE, ActionType.ALL_IN]:
            features["pfr_count"] = features.get("pfr_count", 0) + 1
            features["vpip_count"] = features.get("vpip_count", 0) + 1
        elif request.action_type == ActionType.CALL:
            features["vpip_count"] = features.get("vpip_count", 0) + 1
    
    # Aggression tracking
    if request.action_type in [ActionType.RAISE, ActionType.ALL_IN]:
        features["aggression_ip"] = features.get("aggression_ip", 0.0) + 1.0
        
    stats.dynamic_features = features
    db.commit()
    
    return {"status": "success", "action": action_record}

class NextStreetRequest(BaseModel):
    session_id: str
    next_street: GameRound

@router.post("/session/next_street")
async def next_street(request: NextStreetRequest, user_id: uuid.UUID = Depends(get_current_user_id)):
    session = active_sessions.get(request.session_id)
    if not session or session.user_id != str(user_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.current_street = request.next_street
    return {"status": "success", "current_street": session.current_street}

class ShowdownPlayerInfo(BaseModel):
    player_name: str
    revealed_cards: List[Card]
    is_winner: bool

class SessionShowdownRequest(BaseModel):
    session_id: str
    players: List[ShowdownPlayerInfo]
    community_cards: List[Card]

@router.post("/session/showdown")
async def session_showdown(request: SessionShowdownRequest, user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    session = active_sessions.get(request.session_id)
    if not session or session.user_id != str(user_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    repo = StatsRepository(db)
    results = []
    
    for p_info in request.players:
        all_cards = p_info.revealed_cards + request.community_cards
        if len(all_cards) >= 5:
            hand_result = HandEvaluator.evaluate_7_cards(all_cards) if len(all_cards) == 7 else HandEvaluator.evaluate_5_cards(all_cards[:5])
        else:
            hand_result = None
            
        # Detect bluff: weak hand + aggressive action -> increment strict_bluff_showdowns
        is_bluff = False
        if hand_result and hand_result.rank.value <= 2: # High Card or Pair
            player_actions = [a for a in session.actions_history if a.player_name == p_info.player_name]
            if player_actions and player_actions[-1].action_type in [ActionType.RAISE, ActionType.ALL_IN]:
                is_bluff = True
                
        # Find player in session to pass vpip/pfr
        vpip = False
        pfr = False
        for p in session.players:
            if p.name == p_info.player_name:
                vpip = p.vpip_this_hand
                pfr = p.pfr_this_hand
                break
                
        repo.update_player_stats(
            user_id=user_id,
            name=p_info.player_name,
            vpip_this_hand=vpip,
            pfr_this_hand=pfr,
            is_bluff=is_bluff
        )
        
        results.append({
            "player_name": p_info.player_name,
            "hand_rank": hand_result.rank.name if hand_result else "Unknown",
            "is_bluff": is_bluff,
            "is_winner": p_info.is_winner
        })
        
    return {"status": "success", "results": results}

# --- Stateless Endpoints for Frontend (`lib/api.ts`) ---

from apps.api.application.start_game import StartGameUseCase
from apps.api.application.process_action import ProcessActionUseCase
from apps.api.application.showdown import ShowdownUseCase
from packages.domain.models import Action

class StatelessStartGameRequest(BaseModel):
    player_names: List[str]
    initial_stacks: List[float]
    small_blind: float
    big_blind: float
    dealer_index: Optional[int] = 0

@router.post("/start")
async def stateless_start_game(request: StatelessStartGameRequest, user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    repo = StatsRepository(db)
    
    # 1. Initialize/Fetch players to trigger cold-start logic if new
    # We pass all player names to allow the repository to calculate table averages
    for name in request.player_names:
        repo.get_or_create_opponent(user_id, name, request.player_names)
        
    use_case = StartGameUseCase()
    state = use_case.execute(
        request.player_names,
        request.initial_stacks,
        request.small_blind,
        request.big_blind,
        request.dealer_index
    )
    return state.dict()

class StatelessProcessActionRequest(BaseModel):
    state: GameState
    action: Action

@router.post("/action")
async def stateless_process_action(request: StatelessProcessActionRequest):
    use_case = ProcessActionUseCase()
    try:
        new_state = use_case.execute(request.state, request.action)
        return new_state.dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class StatelessShowdownRequest(BaseModel):
    state: GameState
    bluffer_names: Optional[List[str]] = Field(default_factory=list)

@router.post("/showdown")
async def stateless_showdown(request: StatelessShowdownRequest, user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    try:
        use_case = ShowdownUseCase()
        new_state, result = use_case.execute(request.state)

        # Update stats in database for ALL players involved in this hand
        repo = StatsRepository(db)

        # Extract winner results to identify potential bluffs if not explicitly provided
        pots_results = result.get("pots_results", [])
        explicit_bluffers = request.bluffer_names or []

        for player in request.state.players:
            # Detect bluff: 
            # 1. Explicitly marked by frontend
            # 2. Or reached showdown with a High Card and was NOT a winner (automatic heuristic)
            is_bluff = player.name in explicit_bluffers

            if not is_bluff:
                # Heuristic: Reached showdown with High Card but lost
                all_cards = player.hole_cards + request.state.community_cards
                if len(all_cards) >= 5:
                    # Best hand from all available cards
                    hand_value = HandEvaluator.evaluate_7_cards(all_cards)
                    was_winner = any(player.name in pr["winners"] for pr in pots_results)
                    if hand_value and hand_value.rank == HandRank.HIGH_CARD and not was_winner:
                        is_bluff = True

            repo.update_player_stats(
                user_id=user_id,
                name=player.name,
                vpip_this_hand=player.vpip_this_hand,
                pfr_this_hand=player.pfr_this_hand,
                is_bluff=is_bluff
            )

        return {"new_state": new_state.dict(), "result": result}
    except Exception as e:
        print(f"Error in showdown: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
