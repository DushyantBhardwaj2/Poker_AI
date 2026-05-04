import os
import joblib
import pandas as pd
import numpy as np
import logging
from typing import Optional
from packages.domain.models import LiveGameState
from .utils import calculate_dryness

# Set up logging
logger = logging.getLogger(__name__)

class BluffDetector:
    """
    Real-time bluff detector using the trained XGBoost v3 model.
    """
    def __init__(self, model_path: Optional[str] = None):
        if model_path is None:
            # Resolve default path relative to this file
            # packages/ai/bluff_detector.py -> packages/ai -> packages -> root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            model_path = os.path.join(project_root, "ml_modules", "src", "models", "bluff_detector_showdown_v3.joblib")

        logger.info(f"Loading ML model from: {model_path}")
        if not os.path.exists(model_path):
            error_msg = f"ML model not found at {model_path}. Current working directory: {os.getcwd()}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            self.model = joblib.load(model_path)
            logger.info("Successfully loaded ML model.")
        except Exception as e:
            logger.error(f"Failed to load joblib model: {e}")
            raise

        self.feature_names = [
...
            'bet_bin', 'vpip', 'pfr', 'spr', 'bet_size_diff', 
            'is_monotonic', 'range_miss', 'dryness_bet_interaction', 
            'vpip_bet_interaction', 'tightness_bet_interaction', 'agg_profile'
        ]
        self.threshold = 0.4

    def predict(self, live_state: LiveGameState) -> dict:
        """
        Calculates features and returns bluff probability.
        """
        # 1. Feature Engineering
        street = live_state.street
        rel_bet_size = live_state.bet_amount / (live_state.pot_before + 1e-6)
        
        dryness = calculate_dryness(live_state.board_cards)
        dryness_delta = dryness - live_state.prev_street_dryness if street > 1 else 0.0
        
        prev_max = live_state.prev_street_max_bet
        bet_spike = live_state.bet_amount / prev_max if prev_max > 0 else 1.0
        
        prev_rel = live_state.prev_action_bet_size
        bet_size_diff = rel_bet_size - prev_rel
        is_monotonic = int(rel_bet_size >= prev_rel * 0.9)
        
        spr = live_state.starting_stack / (live_state.pot_before + 1e-6)
        agg_profile = live_state.vpip / (live_state.pfr + 0.01)
        
        # Interaction terms
        dryness_bet_interaction = dryness * rel_bet_size
        vpip_bet_interaction = live_state.vpip * rel_bet_size
        tightness_bet_interaction = (1 - live_state.vpip) * rel_bet_size
        
        # Range Miss Heuristic
        range_miss = live_state.vpip * (dryness + np.clip(dryness_delta, 0, 1)) * np.log1p(np.clip(bet_spike, 0, 20)) * (2 - is_monotonic)
        
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
            'vpip': live_state.vpip,
            'pfr': live_state.pfr,
            'spr': np.clip(spr, 0, 100),
            'bet_size_diff': bet_size_diff,
            'is_monotonic': is_monotonic,
            'range_miss': range_miss,
            'dryness_bet_interaction': dryness_bet_interaction,
            'vpip_bet_interaction': vpip_bet_interaction,
            'tightness_bet_interaction': tightness_bet_interaction,
            'agg_profile': agg_profile
        }
        
        # 2. Inference
        X = pd.DataFrame([feat_dict])[self.feature_names]
        prob = float(self.model.predict_proba(X)[0, 1])
        
        return {
            "bluff_probability": prob,
            "is_bluff": prob >= self.threshold,
            "threshold": self.threshold,
            "street_rank": street,
            "features_snapshot": feat_dict
        }
