from typing import Dict, Any
from packages.domain.models import ActionType

class MoveRecommender:
    @staticmethod
    def recommend(
        win_probability: float, 
        pot_size: float, 
        call_amount: float, 
        player_stack: float
    ) -> Dict[str, Any]:
        """
        Recommends a poker move based on Expected Value (EV) and Pot Odds.
        
        Args:
            win_probability: The probability of winning the hand (0.0 to 1.0).
            pot_size: The current size of the pot BEFORE the player's call.
            call_amount: The amount the player needs to call to stay in the hand.
            player_stack: The player's remaining chips.
            
        Returns:
            A dictionary with the recommended action, EV, pot odds, and explanation.
        """
        
        # If there's no bet to call, checking is free
        if call_amount == 0:
            if win_probability > 0.6:
                return {
                    "action": ActionType.RAISE.value,
                    "ev": 0.0,
                    "pot_odds": 0.0,
                    "explanation": "You have a strong hand and checking is free, but raising builds the pot."
                }
            else:
                return {
                    "action": ActionType.CHECK.value,
                    "ev": 0.0,
                    "pot_odds": 0.0,
                    "explanation": "Checking is free. You have an average or weak hand."
                }
                
        # Calculate Pot Odds
        # Pot odds = amount to call / (current pot + amount to call)
        # It represents the required win probability to break even.
        total_pot_after_call = pot_size + call_amount
        pot_odds = call_amount / total_pot_after_call
        
        # Calculate Expected Value (EV)
        # EV = (Probability of Winning * Potential Reward) - (Probability of Losing * Cost)
        # Simplified: potential reward = current pot size. Cost = call amount.
        ev = (win_probability * pot_size) - ((1 - win_probability) * call_amount)
        
        action = ActionType.FOLD.value
        explanation = ""
        
        if ev > 0 and win_probability >= pot_odds:
            # Positive Expected Value
            if win_probability > 0.75:
                # Very strong hand, consider raising
                action = ActionType.RAISE.value
                explanation = f"Positive EV ({ev:.2f}) and great win probability ({win_probability:.2%}). You should raise for value."
            else:
                # Good enough to call
                action = ActionType.CALL.value
                explanation = f"Positive EV ({ev:.2f}). Your win probability ({win_probability:.2%}) is higher than the pot odds ({pot_odds:.2%}). Call."
        else:
            # Negative Expected Value
            if win_probability > 0.15 and call_amount < (player_stack * 0.05):
                # Sometimes a small call is okay if the implied odds are good, but strict EV says fold.
                # We'll stick to strict EV for now.
                action = ActionType.FOLD.value
                explanation = f"Negative EV ({ev:.2f}). Win probability ({win_probability:.2%}) is worse than pot odds ({pot_odds:.2%}). Fold."
            else:
                action = ActionType.FOLD.value
                explanation = f"Negative EV ({ev:.2f}). Calling is unprofitable over the long run. Fold."
                
        return {
            "action": action,
            "ev": ev,
            "pot_odds": pot_odds,
            "explanation": explanation
        }
