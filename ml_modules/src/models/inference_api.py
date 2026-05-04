import joblib
import pandas as pd
import numpy as np
import os
from src.utils.config_loader import load_config
from src.features.analyze_dryness import calculate_dryness

class BluffPredictor:
    """
    Inference wrapper for the PokerSense Bluff Detection model.
    Handles real-time feature engineering and high-precision thresholding.
    """
    def __init__(self, model_version='v3'):
        self.config = load_config()
        model_dir = self.config['paths']['models']
        
        # Load the Ground Truth calibrated model
        model_path = os.path.join(model_dir, 'bluff_detector_showdown_v3.joblib')
        if not os.path.exists(model_path):
            # Fallback to standard v3 if showdown-specific not found
            model_path = os.path.join(model_dir, 'bluff_detector_v3.joblib')
            
        self.model = joblib.load(model_path)
        
        # Performance metadata (from calibration step)
        self.precision_map = {
            1: 0.54, # Flop
            2: 0.71, # Turn
            3: 0.93  # River
        }
        self.base_threshold = 0.4
        
        self.feature_names = [
            'street', 'rel_bet_size', 'bet_spike', 'dryness', 'dryness_delta', 
            'bet_bin', 'vpip', 'pfr', 'spr', 'bet_size_diff', 
            'is_monotonic', 'range_miss', 'dryness_bet_interaction', 
            'vpip_bet_interaction', 'tightness_bet_interaction', 'agg_profile'
        ]

    def _engineer_features(self, state):
        """
        Calculates v3 features from a raw game state dictionary.
        
        state = {
            'street': int,
            'bet_amount': float,
            'pot_before': float,
            'starting_stack': float,
            'board_cards': list,
            'vpip': float,
            'pfr': float,
            'prev_street_dryness': float (default 1.0),
            'prev_street_max_bet': float (default 0.0),
            'prev_action_bet_size': float (relative, default 0.0)
        }
        """
        # Basic features
        street = state['street']
        rel_bet_size = state['bet_amount'] / (state['pot_before'] + 1e-6)
        dryness = calculate_dryness(state['board_cards'])
        vpip = state.get('vpip', 0.25)
        pfr = state.get('pfr', 0.18)
        
        # Derived v3 features
        dryness_delta = dryness - state.get('prev_street_dryness', dryness) if street > 1 else 0.0
        
        prev_max = state.get('prev_street_max_bet', 0.0)
        bet_spike = state['bet_amount'] / prev_max if prev_max > 0 else 1.0
        
        prev_rel = state.get('prev_action_bet_size', 0.0)
        bet_size_diff = rel_bet_size - prev_rel
        is_monotonic = int(rel_bet_size >= prev_rel * 0.9)
        
        spr = state['starting_stack'] / (state['pot_before'] + 1e-6)
        agg_profile = vpip / (pfr + 0.01)
        
        # Interaction terms
        dryness_bet_interaction = dryness * rel_bet_size
        vpip_bet_interaction = vpip * rel_bet_size
        tightness_bet_interaction = (1 - vpip) * rel_bet_size
        
        # Range Miss Heuristic (matching engineer_features_v3.py)
        range_miss = vpip * (dryness + np.clip(dryness_delta, 0, 1)) * np.log1p(np.clip(bet_spike, 0, 20)) * (2 - is_monotonic)
        
        # Semantic Binning
        bet_bin = 0
        if rel_bet_size >= 0.1: bet_bin = 1
        if rel_bet_size >= 0.4: bet_bin = 2
        if rel_bet_size >= 0.65: bet_bin = 3
        if rel_bet_size >= 1.1: bet_bin = 4
        
        feat_dict = {
            'street': street,
            'rel_bet_size': np.clip(rel_bet_size, 0, 10),
            'bet_spike': np.clip(bet_spike, 0, 20),
            'dryness': dryness,
            'dryness_delta': np.clip(dryness_delta, -1, 1),
            'bet_bin': bet_bin,
            'vpip': vpip,
            'pfr': pfr,
            'spr': np.clip(spr, 0, 100),
            'bet_size_diff': bet_size_diff,
            'is_monotonic': is_monotonic,
            'range_miss': range_miss,
            'dryness_bet_interaction': dryness_bet_interaction,
            'vpip_bet_interaction': vpip_bet_interaction,
            'tightness_bet_interaction': tightness_bet_interaction,
            'agg_profile': agg_profile
        }
        
        return pd.DataFrame([feat_dict])[self.feature_names]

    def predict_bluff(self, state):
        """
        Returns a dictionary with probability, detection, and confidence.
        """
        X = self._engineer_features(state)
        
        # Predict using the classifier (returns probability of class 1)
        prob = float(self.model.predict_proba(X)[0, 1])
        
        street = state['street']
        # Detection based on calibrated threshold
        is_bluff = prob >= self.base_threshold
        
        # Precision estimate based on calibration data
        precision = self.precision_map.get(street, 0.50)
        
        return {
            'bluff_probability': prob,
            'is_bluff_detected': bool(is_bluff),
            'expected_precision': precision if is_bluff else 0.0,
            'confidence_level': 'High' if precision > 0.8 else 'Medium' if precision > 0.6 else 'Low'
        }

if __name__ == "__main__":
    # Test prediction
    predictor = BluffPredictor()
    test_state = {
        'street': 3, # River
        'bet_amount': 1500,
        'pot_before': 1000, # Overbet
        'starting_stack': 5000,
        'board_cards': ['[As]', '[Ks]', '[Qc]', '[2d]', '[3h]'], # Very dry
        'vpip': 0.15, # Tight player
        'pfr': 0.12,
        'prev_street_dryness': 0.9,
        'prev_street_max_bet': 200, # Huge spike
        'prev_action_bet_size': 0.2
    }
    
    result = predictor.predict_bluff(test_state)
    print("\nTest Prediction (River Overbet by Tight Player):")
    print(result)

    maniac_state = {
        'street': 3, # River
        'bet_amount': 2000,
        'pot_before': 1000, # 2x Pot Overbet
        'starting_stack': 5000,
        'board_cards': ['[8s]', '[7s]', '[6s]', '[5c]', '[2h]'], # Wet Board
        'vpip': 0.75, # Maniac
        'pfr': 0.60,
        'prev_street_dryness': 0.1,
        'prev_street_max_bet': 100, # 10x Spike
        'prev_action_bet_size': 0.1
    }
    
    result2 = predictor.predict_bluff(maniac_state)
    print("\nTest Prediction (River Overbet by Maniac):")
    print(result2)

    flop_state = {
        'street': 1, # Flop
        'bet_amount': 75,
        'pot_before': 100, # 3/4 Pot
        'starting_stack': 5000,
        'board_cards': ['[8s]', '[7s]', '[2c]'], # Semi-Wet
        'vpip': 0.35, # Aggressive
        'pfr': 0.28,
        'prev_street_dryness': 1.0,
        'prev_street_max_bet': 20,
        'prev_action_bet_size': 0.0
    }
    
    result3 = predictor.predict_bluff(flop_state)
    print("\nTest Prediction (Flop C-Bet by Aggressive Player):")
    print(result3)
