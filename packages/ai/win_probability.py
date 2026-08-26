import random
from typing import List, Dict
from packages.domain.models import Card, Rank, Suit
from packages.domain.deck import Deck
from packages.domain.hand_evaluator import HandEvaluator, RANK_VALUE

class WinProbabilityCalculator:
    # Pre-calculated order of starting hand strengths (approximate)
    # Pairs, then high-low suited, then high-low offsuit
    HAND_STRENGTH_ORDER = [
        "AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "AKs", "AQs", "AJs", "AKo",
        "66", "ATs", "AQo", "KQs", "55", "AJo", "KJs", "44", "ATo", "QJs", "33",
        "KJo", "22", "KTs", "QTs", "JTs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s",
        "A3s", "A2s", "K9s", "Q9s", "J9s", "T9s", "A9o", "KTo", "QTo", "JTo"
    ]

    # A simulation costs about 0.25ms, so this ceiling is roughly 2.5 seconds of
    # CPU. /win-probability is unauthenticated, and without a ceiling one request
    # asking for ten million rollouts occupies the whole container for an hour.
    MAX_SIMULATIONS = 10_000

    # 2 hole cards + 5 board + 2 per opponent has to fit in 52, and a table with
    # more than ten seats is not a poker table. Past that the deck runs out
    # mid-deal and the opponents share cards, which produced a plausible-looking
    # number rather than an error.
    MAX_OPPONENTS = 9

    @staticmethod
    def calculate(
        hole_cards: List[Card],
        community_cards: List[Card],
        num_opponents: int,
        num_simulations: int = 1000,
        opponent_vpip: float = 1.0
    ) -> Dict[str, float]:
        """
        Estimates the probability of winning a hand using Range-Aware Monte Carlo simulation.
        """
        if len(hole_cards) != 2:
            raise ValueError("Must provide exactly 2 hole cards")

        # Validated here rather than only at the API boundary, because the failures
        # are silent. A negative count makes range() empty, so every rate divides
        # 0 by a negative number and the caller gets win_probability: -0.0 with no
        # indication anything went wrong. Zero divides by zero.
        if not isinstance(num_simulations, int) or isinstance(num_simulations, bool):
            raise ValueError("num_simulations must be an integer")
        if not 1 <= num_simulations <= WinProbabilityCalculator.MAX_SIMULATIONS:
            raise ValueError(
                f"num_simulations must be between 1 and "
                f"{WinProbabilityCalculator.MAX_SIMULATIONS}, got {num_simulations}"
            )
        if not 1 <= num_opponents <= WinProbabilityCalculator.MAX_OPPONENTS:
            raise ValueError(
                f"num_opponents must be between 1 and "
                f"{WinProbabilityCalculator.MAX_OPPONENTS}, got {num_opponents}"
            )

        wins = 0
        ties = 0
        losses = 0

        known_cards_str = [str(c) for c in hole_cards + community_cards]

        # Pre-filter deck for speed
        all_deck = [Card(rank=r, suit=s) for r in Rank for s in Suit]
        base_sim_deck = [c for c in all_deck if str(c) not in known_cards_str]

        for _ in range(num_simulations):
            sim_deck = base_sim_deck.copy()
            random.shuffle(sim_deck)
            
            # Deal remaining community cards
            needed_community = 5 - len(community_cards)
            sim_community = community_cards + sim_deck[:needed_community]
            sim_deck = sim_deck[needed_community:]
            
            # Deal opponent hole cards
            opponent_hands = []
            for _ in range(num_opponents):
                # Simple Range Awareness: 
                # If vpip is low, we occasionally 're-draw' if the hand is too weak.
                # This is a fast approximation of Gaussian range sampling.
                opp_hand = sim_deck[:2]
                if opponent_vpip < 0.5 and random.random() > 0.2:
                    # Check if hand is "decent" (contains at least one high card or pair)
                    ranks = [RANK_VALUE[c.rank] for c in opp_hand]
                    is_pair = ranks[0] == ranks[1]
                    high_card = max(ranks) >= 10 # T or better
                    
                    # If it's a tight player and they have a garbage hand, 
                    # we re-draw once to bias towards their actual range.
                    if not (is_pair or high_card):
                        # Swap these cards with others in the deck
                        sim_deck = sim_deck[2:] + opp_hand
                        opp_hand = sim_deck[:2]
                
                opponent_hands.append(opp_hand)
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
        equity = win_rate + (tie_rate / (num_opponents + 1))
        
        return {
            "win_probability": win_rate,
            "tie_probability": tie_rate,
            "equity": equity,
            "simulations": num_simulations,
            "range_applied": opponent_vpip < 1.0
        }
