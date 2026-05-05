import os
import sys
import pytest
import uuid
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.getcwd())

from apps.api.interfaces.main import app
from packages.domain.models import GameRound, ActionType, PlayerStatus
from packages.domain.database import SessionLocal
from packages.domain.db_models import User

client = TestClient(app)

def test_complete_game_path():
    """
    Simulates a full game path via stateless API endpoints:
    Start -> Pre-flop Action -> Flop -> Showdown
    """
    user_id = str(uuid.uuid4())
    headers = {"X-User-Id": user_id}

    # Pre-register user to avoid FK error
    db = SessionLocal()
    try:
        new_user = User(user_id=user_id, email=f"test-{user_id[:8]}@example.com")
        db.add(new_user)
        db.commit()
    finally:
        db.close()

    # 1. Start Game
    print("\n[Step 1] Starting Game...")
    setup_payload = {
        "player_names": ["You", "Whale", "Nit"],
        "initial_stacks": [1000, 1000, 1000],
        "small_blind": 5,
        "big_blind": 10,
        "dealer_index": 0
    }
    response = client.post("/api/v1/game/start", json=setup_payload, headers=headers)
    assert response.status_code == 200
    state = response.json()
    
    # Pre-flop action starts after BB
    # D=0, SB=1, BB=2. UTG is index 0.
    curr_idx = state["current_player_index"]
    assert state["round"] == "pre-flop"
    print(f"Current Player Index: {curr_idx} (You)")

    # 2. Action: You (index 0) Raises to 30
    action_payload = {
        "state": state,
        "action": {
            "player_index": curr_idx,
            "action_type": "raise",
            "amount": 30
        }
    }
    response = client.post("/api/v1/game/action", json=action_payload, headers=headers)
    if response.status_code != 200:
        print(f"Action Error: {response.json()}")
    assert response.status_code == 200
    state = response.json()
    assert state["current_bet"] == 30
    assert state["players"][0]["stack"] == 970

    # 3. Action: Whale (index 1) Calls 30
    curr_idx = state["current_player_index"]
    assert curr_idx == 1
    action_payload = {
        "state": state,
        "action": {
            "player_index": curr_idx,
            "action_type": "call",
            "amount": 0
        }
    }
    response = client.post("/api/v1/game/action", json=action_payload, headers=headers)
    state = response.json()

    # 4. Action: Nit (index 2) Folds
    curr_idx = state["current_player_index"]
    assert curr_idx == 2
    action_payload = {
        "state": state,
        "action": {
            "player_index": curr_idx,
            "action_type": "fold",
            "amount": 0
        }
    }

    response = client.post("/api/v1/game/action", json=action_payload, headers=headers)
    state = response.json()
    
    # Round should advance to FLOP
    assert state["round"] == "flop"
    print("Round advanced to FLOP")

    # 5. Flop Action: Check-Check
    # First actor on flop is SB (index 1).
    for i in [1, 0]:
        curr_idx = state["current_player_index"]
        assert curr_idx == i
        action_payload = {
            "state": state,
            "action": {
                "player_index": curr_idx,
                "action_type": "check",
                "amount": 0
            }
        }
        response = client.post("/api/v1/game/action", json=action_payload, headers=headers)
        state = response.json()
    
    assert state["round"] == "turn"
    print("Round advanced to TURN")

    # 6. AI Analysis on Turn
    # You have A-A. Flop was A-K-J.
    state["players"][0]["hole_cards"] = [
        {"rank": "A", "suit": "s"}, {"rank": "A", "suit": "h"}
    ]
    state["community_cards"] = [
        {"rank": "A", "suit": "d"}, {"rank": "K", "suit": "c"}, {"rank": "J", "suit": "h"}
    ]
    
    analysis_payload = {
        "state": state,
        "history": [], # Simplified for test
        "opponent_name": "Whale",
        "hole_cards": [{"rank": "A", "suit": "s"}, {"rank": "A", "suit": "h"}],
        "num_simulations": 100
    }
    response = client.post("/api/v1/ai/analyze-full", json=analysis_payload, headers=headers)
    assert response.status_code == 200
    analysis = response.json()
    print(f"AI Advice: {analysis['advice']['action']}")
    assert "win_analysis" in analysis

    # 7. Showdown
    showdown_payload = {
        "state": state,
        "bluffer_names": ["Whale"]
    }
    response = client.post("/api/v1/game/showdown", json=showdown_payload, headers=headers)
    assert response.status_code == 200
    showdown_data = response.json()
    assert "result" in showdown_data
    print("Showdown completed successfully")

if __name__ == "__main__":
    test_complete_game_path()
