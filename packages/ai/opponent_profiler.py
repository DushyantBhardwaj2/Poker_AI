from typing import Dict

class OpponentProfiler:
    @staticmethod
    def profile(vpip: float, pfr: float) -> Dict[str, str]:
        """
        Classifies an opponent based on VPIP (Voluntarily Put In Pot) and PFR (Preflop Raise).
        
        Args:
            vpip: The percentage of hands the player voluntarily plays preflop (0.0 to 1.0).
            pfr: The percentage of hands the player raises preflop (0.0 to 1.0).
            
        Returns:
            A dictionary with the player's classification.
        """
        # Ensure percentages are valid
        vpip = max(0.0, min(1.0, vpip))
        pfr = max(0.0, min(vpip, pfr)) # PFR cannot be greater than VPIP
        
        play_style = "Tight" if vpip < 0.20 else "Loose"
        
        # Aggression is relative to how many hands they play
        # If they raise more than half the time they play a hand, they are aggressive.
        aggression_ratio = pfr / vpip if vpip > 0 else 0
        aggression_style = "Passive" if aggression_ratio < 0.40 else "Aggressive"
        
        classification = f"{play_style}-{aggression_style}"
        
        description = ""
        if classification == "Tight-Aggressive":
            description = "TAG (Tight-Aggressive): Plays few hands but plays them aggressively. Respect their raises."
        elif classification == "Tight-Passive":
            description = "Nit (Tight-Passive): Only plays premium hands and rarely raises. Easy to bluff, but fold to their bets."
        elif classification == "Loose-Aggressive":
            description = "LAG (Loose-Aggressive): Plays many hands aggressively. Puts a lot of pressure, often bluffs."
        elif classification == "Loose-Passive":
            description = "Calling Station (Loose-Passive): Plays many hands but mostly calls. Do not bluff them; bet your strong hands for value."
            
        return {
            "vpip": vpip,
            "pfr": pfr,
            "classification": classification,
            "description": description
        }
