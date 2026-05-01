from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from apps.api.application.start_game import StartGameUseCase
from apps.api.application.process_action import ProcessActionUseCase
from packages.domain.models import GameState, Action, ActionType, Card
from packages.domain.hand_evaluator import HandEvaluator
from apps.api.application.showdown import ShowdownUseCase
from packages.domain.database import get_db
from packages.domain.stats_repository import StatsRepository

router = APIRouter()

class StartGameRequest(BaseModel):
    player_names: List[str]
    initial_stacks: List[float]
    small_blind: float
    big_blind: float

class ActionRequest(BaseModel):
    state: GameState
    action: Action

class EvaluateRequest(BaseModel):
    cards: List[Card]

class ShowdownRequest(BaseModel):
    state: GameState

@router.post("/start")
async def start_game(request: StartGameRequest):
    use_case = StartGameUseCase()
    try:
        game_state = use_case.execute(
            request.player_names,
            request.initial_stacks,
            request.small_blind,
            request.big_blind
        )
        return game_state
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/action")
async def process_action(request: ActionRequest):
    use_case = ProcessActionUseCase()
    try:
        new_state = use_case.execute(request.state, request.action)
        return new_state
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/showdown")
async def showdown(request: ShowdownRequest, db: Session = Depends(get_db)):
    use_case = ShowdownUseCase()
    try:
        result = use_case.execute(request.state)
        
        # Record stats for all players
        repo = StatsRepository(db)
        for player in request.state.players:
            repo.update_player_stats(
                name=player.name,
                vpip_this_hand=player.vpip_this_hand,
                pfr_this_hand=player.pfr_this_hand
            )
            
        return {
            "new_state": request.state,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/evaluate")
async def evaluate_hand(request: EvaluateRequest):
    try:
        if len(request.cards) == 5:
            result = HandEvaluator.evaluate_5_cards(request.cards)
        elif len(request.cards) == 7:
            result = HandEvaluator.evaluate_7_cards(request.cards)
        else:
            raise ValueError("Must provide 5 or 7 cards")
        
        return {
            "rank": result.rank.name,
            "rank_value": result.rank.value,
            "tie_break_values": result.values
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
