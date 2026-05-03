import os
import sys
import uuid
import numpy as np
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from packages.domain.database import engine
from packages.domain.models import GameState, Player, Card, Rank, Suit, GameRound, ActionRecord, ActionType
from packages.ai.bluff_detector import BluffDetector
from packages.ai.feature_mapper import FeatureMapper
from packages.domain.stats_repository import StatsRepository
from packages.domain.db_models import User

def test_inference():
    load_dotenv()
    
    # 1. Mock Game State
    # Scenario: River Overbet by a tight player on a dry board
    players = [
        Player(name="Admin", stack=4000, hole_cards=[Card(rank=Rank.ACE, suit=Suit.SPADES), Card(rank=Rank.KING, suit=Suit.SPADES)]),
        Player(name="Opponent", stack=3000, hole_cards=[])
    ]
    community = [
        Card(rank=Rank.ACE, suit=Suit.HEARTS),
        Card(rank=Rank.TWO, suit=Suit.DIAMONDS),
        Card(rank=Rank.SEVEN, suit=Suit.CLUBS),
        Card(rank=Rank.QUEEN, suit=Suit.SPADES),
        Card(rank=Rank.THREE, suit=Suit.HEARTS)
    ]
    
    state = GameState(
        players=players,
        community_cards=community,
        pot=2500, # Large pot
        round=GameRound.RIVER,
        small_blind=10,
        big_blind=20,
        current_player_index=1
    )
    
    history = [
        ActionRecord(player_name="Opponent", action_type=ActionType.RAISE, amount=1500, street=GameRound.RIVER)
    ]
    
    # 2. Setup DB connection for real stats lookup test
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        user = db.query(User).filter(User.email == "admin@pokersense.ai").first()
        if not user:
             print("Please run verify_db.py first")
             return
             
        repo = StatsRepository(db)
        opp = repo.get_or_create_opponent(user.user_id, "Opponent_Test_Inference")
        
        # 3. Map GameState to LiveGameState
        # Mocking vpip/pfr for the mapper test
        vpip = 0.15
        pfr = 0.12
        live_state = FeatureMapper.map_to_live_state(state, history, {"vpip": vpip, "pfr": pfr})
        print(f"Mapped Live State: {live_state.model_dump()}")
        
        # 4. Run Detector
        print("\nLoading model and predicting...")
        detector = BluffDetector()
        result = detector.predict(live_state)
        
        print("\n--- Bluff Detection Result ---")
        print(f"Opponent: Opponent_Test_Inference")
        print(f"Probability: {result['bluff_probability']:.2%}")
        print(f"Is Bluff: {result['is_bluff']}")
        print(f"Confidence (Threshold): {result['threshold']}")
        
        # 5. Test another scenario: Maniac on Wet Board
        print("\n--- Testing Scenario: Maniac on Wet Board ---")
        maniac_vpip = 0.75
        maniac_pfr = 0.60
        wet_community = [
            Card(rank=Rank.EIGHT, suit=Suit.SPADES),
            Card(rank=Rank.SEVEN, suit=Suit.SPADES),
            Card(rank=Rank.SIX, suit=Suit.SPADES),
            Card(rank=Rank.FIVE, suit=Suit.CLUBS),
            Card(rank=Rank.TWO, suit=Suit.HEARTS)
        ]
        state.community_cards = wet_community
        
        live_state_2 = FeatureMapper.map_to_live_state(state, history, {"vpip": maniac_vpip, "pfr": maniac_pfr})
        result_2 = detector.predict(live_state_2)
        print(f"Maniac Probability: {result_2['bluff_probability']:.2%}")
        print(f"Is Bluff: {result_2['is_bluff']}")

    finally:
        db.close()

if __name__ == "__main__":
    test_inference()
