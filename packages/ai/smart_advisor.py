from typing import Dict, Any
from packages.domain.models import ActionType
from .move_recommender import MoveRecommender

class SmartAdvisor:
    """
    Advanced recommendation engine that synthesizes mathematical probability
    and behavioral bluff detection.
    """
    
    @staticmethod
    def recommend(
        win_probability: float,
        bluff_probability: float,
        pot_size: float,
        call_amount: float,
        player_stack: float
    ) -> Dict[str, Any]:
        """
        Adjusts mathematical recommendations based on the likelihood of an opponent's bluff.
        """
        # 1. Calculate Adjusted Win Probability
        # P(Win) if calling = (P(Win against value) * P(Value)) + (P(Win against bluff) * P(Bluff))
        # We assume 95% win rate if the opponent is confirmed to be bluffing.
        p_bluff = bluff_probability
        p_value = 1.0 - p_bluff
        
        # We assume 'win_probability' is the chance against a standard/value range
        adjusted_win_prob = (win_probability * p_value) + (0.95 * p_bluff)
        adjusted_win_prob = min(0.99, adjusted_win_prob) # Cap for realism
        
        # 2. Get base recommendation from MoveRecommender
        advice = MoveRecommender.recommend(
            adjusted_win_prob,
            pot_size,
            call_amount,
            player_stack
        )
        
        # 3. Enhance Explanation
        bluff_context = ""
        if p_bluff > 0.6:
            bluff_context = f" Opponent is VERY likely to be bluffing ({p_bluff:.1%})."
        elif p_bluff > 0.4:
            bluff_context = f" Opponent may be bluffing ({p_bluff:.1%})."
        elif p_bluff < 0.15:
            bluff_context = f" Opponent is rarely bluffing here ({p_bluff:.1%})."
            
        advice["explanation"] = advice["explanation"] + bluff_context
        advice["adjusted_win_probability"] = adjusted_win_prob
        advice["bluff_probability"] = p_bluff
        
        # 4. Theoretical Injection (Theory of Poker)
        if p_bluff > 0.5 and advice["action"] == "call":
             advice["theory_tip"] = "The Fundamental Theorem of Poker: You gain when your opponent makes a mistake. Their bluff is likely a mistake here."
        elif win_probability < (call_amount / (pot_size + call_amount + 1e-6)):
             advice["theory_tip"] = "Pot Odds: Your mathematical equity is less than the price of the call. This is usually a fold unless you suspect a high bluff frequency."
             
        return advice
