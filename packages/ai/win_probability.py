import random
from typing import List, Dict
from packages.domain.models import Card, Rank, Suit
from packages.domain.deck import Deck
from packages.domain.hand_evaluator import HandEvaluator

class WinProbabilityCalculator:
    @staticmethod
    def calculate(hole_cards: List[Card], community_cards: List[Card], num_opponents: int, num_simulations: int = 1000) -> Dict[str, float]:
        """
        Estimates the probability of winning a hand using Monte Carlo simulation.
        
        Args:
            hole_cards: The 2 cards held by the player.
            community_cards: The currently visible community cards (0 to 5).
            num_opponents: The number of other active players in the hand.
            num_simulations: The number of random games to simulate.
            
        Returns:
            A dictionary containing win, tie, and equity probabilities.
        """
        if len(hole_cards) != 2:
            raise ValueError("Must provide exactly 2 hole cards")
            
        wins = 0
        ties = 0
        losses = 0
        
        known_cards_str = [str(c) for c in hole_cards + community_cards]
        
        for _ in range(num_simulations):
            # Create a full deck and remove known cards
            # We recreate a light-weight deck representation for speed
            deck_cards = [Card(rank=r, suit=s) for r in Rank for s in Suit]
            # Filter out known cards
            sim_deck = [c for c in deck_cards if str(c) not in known_cards_str]
            
            random.shuffle(sim_deck)
            
            # Deal remaining community cards (up to 5)
            needed_community = 5 - len(community_cards)
            sim_community = community_cards + sim_deck[:needed_community]
            sim_deck = sim_deck[needed_community:]
            
            # Deal opponent hole cards
            opponent_hands = []
            for _ in range(num_opponents):
                opponent_hands.append(sim_deck[:2])
                sim_deck = sim_deck[2:]
                
            # Evaluate hands
            my_hand_value = HandEvaluator.evaluate_7_cards(hole_cards + sim_community)
            
            is_win = True
            is_tie = False
            
            for opp_hand in opponent_hands:
                opp_hand_value = HandEvaluator.evaluate_7_cards(opp_hand + sim_community)
                
                if opp_hand_value > my_hand_value:
                    is_win = False
                    is_tie = False
                    break
                elif opp_hand_value == my_hand_value:
                    is_win = False
                    is_tie = True
            
            if is_win:
                wins += 1
            elif is_tie:
                ties += 1
            else:
                losses += 1
                
        win_rate = wins / num_simulations
        tie_rate = ties / num_simulations
        equity = win_rate + (tie_rate / (num_opponents + 1)) # Simplified equity calculation
        
        return {
            "win_probability": win_rate,
            "tie_probability": tie_rate,
            "equity": equity
        }
