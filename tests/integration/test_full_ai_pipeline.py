import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

from packages.domain.models import GameState, Player, Card, Rank, Suit, GameRound, ActionRecord, ActionType
from packages.ai.feature_mapper import FeatureMapper
from packages.ai.bluff_detector import BluffDetector
from packages.ai.win_probability import WinProbabilityCalculator
from packages.ai.smart_advisor import SmartAdvisor

def test_full_pipeline():
    load_dotenv()
    
    # 1. State: User has A-K, Flop is A-7-2. Opponent raises big.
    hole_cards = [Card(rank=Rank.ACE, suit=Suit.SPADES), Card(rank=Rank.KING, suit=Suit.HEARTS)]
    community = [Card(rank=Rank.ACE, suit=Suit.DIAMONDS), Card(rank=Rank.SEVEN, suit=Suit.CLUBS), Card(rank=Rank.TWO, suit=Suit.HEARTS)]
    
    players = [
        Player(name="User", stack=5000, hole_cards=hole_cards),
        Player(name="Opponent", stack=5000)
    ]
    
    state = GameState(
        players=players,
        community_cards=community,
        pot=1000,
        round=GameRound.FLOP,
        current_bet=500,
        current_player_index=0, # User's turn to respond to the 500 bet
        small_blind=10,
        big_blind=20
    )
    
    history = [
        ActionRecord(player_name="Opponent", action_type=ActionType.RAISE, amount=500, street=GameRound.FLOP)
    ]
    
    # 2. Run Pipeline
    print("--- 1. Win Probability (Range-Aware) ---")
    vpip = 0.20 # Tight-Aggressive Opponent
    win_result = WinProbabilityCalculator.calculate(hole_cards, community, 1, 1000, vpip)
    print(f"Win Prob: {win_result['win_probability']:.2%}")
    
    print("\n--- 2. Bluff Detection ---")
    detector = BluffDetector()
    live_state = FeatureMapper.map_to_live_state(state, history, {"vpip": vpip, "pfr": 0.15})
    bluff_result = detector.predict(live_state)
    print(f"Bluff Prob: {bluff_result['bluff_probability']:.2%}")
    
    print("\n--- 3. Smart Advice ---")
    advice = SmartAdvisor.recommend(
        win_result['win_probability'],
        bluff_result['bluff_probability'],
        state.pot,
        500, # Call amount
        5000
    )
    print(f"Advice: {advice['action'].upper()}")
    print(f"Explanation: {advice['explanation']}")
    if "theory_tip" in advice:
        print(f"Theory Tip: {advice['theory_tip']}")

if __name__ == "__main__":
    test_full_pipeline()
