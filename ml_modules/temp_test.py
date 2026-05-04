import sys
import os

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.models.inference_api import BluffPredictor

predictor = BluffPredictor()

test_cases = [
    {
        'name': "Case 1: Maniac Massive Overbet on extremely dry board (Classic Bluff)",
        'state': {
            'street': 3, 
            'bet_amount': 5000,
            'pot_before': 500, 
            'starting_stack': 10000,
            'board_cards': ['[2s]', '[7h]', '[3c]', '[3d]', '[8c]'], 
            'vpip': 0.85, 
            'pfr': 0.60,
            'prev_street_dryness': 0.9,
            'prev_street_max_bet': 0, 
            'prev_action_bet_size': 0.0
        }
    },
    {
        'name': "Case 2: Turn weak probe by high VPIP player",
        'state': {
            'street': 2,
            'bet_amount': 100,
            'pot_before': 1000,
            'starting_stack': 5000,
            'board_cards': ['[As]', '[Ks]', '[2c]', '[2d]'],
            'vpip': 0.65,
            'pfr': 0.20,
            'prev_street_dryness': 0.5,
            'prev_street_max_bet': 0,
            'prev_action_bet_size': 0.0
        }
    },
    {
        'name': "Case 3: Extreme Bet Spike on River by LAG (Loose Aggressive)",
        'state': {
            'street': 3,
            'bet_amount': 4000,
            'pot_before': 400,
            'starting_stack': 5000,
            'board_cards': ['[2c]', '[2d]', '[2h]', '[3s]', '[4c]'],
            'vpip': 0.55,
            'pfr': 0.45,
            'prev_street_dryness': 0.8,
            'prev_street_max_bet': 10,
            'prev_action_bet_size': 0.05
        }
    }
]

for tc in test_cases:
    print(f"\n--- {tc['name']} ---")
    features = predictor._engineer_features(tc['state'])
    print("Engineered Features:")
    for col in features.columns:
        print(f"  {col}: {features[col].iloc[0]}")
    result = predictor.predict_bluff(tc['state'])
    print(result)
