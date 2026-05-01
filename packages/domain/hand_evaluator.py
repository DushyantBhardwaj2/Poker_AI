from typing import List, Tuple, Dict
from collections import Counter
from .models import Card, HandRank, Rank, Suit

RANK_VALUE = {
    Rank.TWO: 2, Rank.THREE: 3, Rank.FOUR: 4, Rank.FIVE: 5,
    Rank.SIX: 6, Rank.SEVEN: 7, Rank.EIGHT: 8, Rank.NINE: 9,
    Rank.TEN: 10, Rank.JACK: 11, Rank.QUEEN: 12, Rank.KING: 13,
    Rank.ACE: 14
}

class HandValue:
    def __init__(self, rank: HandRank, values: List[int]):
        self.rank = rank
        self.values = values

    def __gt__(self, other):
        if self.rank != other.rank:
            return self.rank > other.rank
        return self.values > other.values

    def __lt__(self, other):
        if self.rank != other.rank:
            return self.rank < other.rank
        return self.values < other.values

    def __eq__(self, other):
        return self.rank == other.rank and self.values == other.values

    def __repr__(self):
        return f"HandValue(rank={self.rank.name}, values={self.values})"

class HandEvaluator:
    @staticmethod
    def evaluate_7_cards(cards: List[Card]) -> HandValue:
        """Evaluates the best 5-card hand from a pool of 7 cards."""
        from itertools import combinations
        best_hand = None
        
        # In a real game, 7 cards are provided. We check all combinations of 5.
        # While there are more efficient algorithms, combinations is fine for 7 cards.
        for combo in combinations(cards, 5):
            current_value = HandEvaluator.evaluate_5_cards(list(combo))
            if best_hand is None or current_value > best_hand:
                best_hand = current_value
        
        return best_hand

    @staticmethod
    def evaluate_5_cards(cards: List[Card]) -> HandValue:
        """Evaluates a 5-card hand."""
        ranks = sorted([RANK_VALUE[c.rank] for c in cards], reverse=True)
        suits = [c.suit for c in cards]
        rank_counts = Counter(ranks)
        counts = sorted(rank_counts.values(), reverse=True)
        
        is_flush = len(set(suits)) == 1
        
        # Check for straight
        is_straight = False
        straight_high_card = -1
        
        # Normal straight
        unique_ranks = sorted(list(set(ranks)), reverse=True)
        if len(unique_ranks) == 5:
            if unique_ranks[0] - unique_ranks[4] == 4:
                is_straight = True
                straight_high_card = unique_ranks[0]
            # Special case: A-2-3-4-5 straight
            elif unique_ranks == [14, 5, 4, 3, 2]:
                is_straight = True
                straight_high_card = 5
        
        # Royal Flush / Straight Flush
        if is_flush and is_straight:
            if straight_high_card == 14:
                return HandValue(HandRank.ROYAL_FLUSH, [14])
            return HandValue(HandRank.STRAIGHT_FLUSH, [straight_high_card])
        
        # Four of a kind
        if counts[0] == 4:
            quad_rank = [r for r, c in rank_counts.items() if c == 4][0]
            kicker = [r for r, c in rank_counts.items() if c == 1][0]
            return HandValue(HandRank.FOUR_OF_A_KIND, [quad_rank, kicker])
        
        # Full house
        if counts[0] == 3 and counts[1] == 2:
            trips_rank = [r for r, c in rank_counts.items() if c == 3][0]
            pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
            return HandValue(HandRank.FULL_HOUSE, [trips_rank, pair_rank])
        
        # Flush
        if is_flush:
            return HandValue(HandRank.FLUSH, ranks)
        
        # Straight
        if is_straight:
            return HandValue(HandRank.STRAIGHT, [straight_high_card])
        
        # Three of a kind
        if counts[0] == 3:
            trips_rank = [r for r, c in rank_counts.items() if c == 3][0]
            kickers = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
            return HandValue(HandRank.THREE_OF_A_KIND, [trips_rank] + kickers)
        
        # Two pair
        if counts[0] == 2 and counts[1] == 2:
            pairs = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
            kicker = [r for r, c in rank_counts.items() if c == 1][0]
            return HandValue(HandRank.TWO_PAIR, pairs + [kicker])
        
        # Pair
        if counts[0] == 2:
            pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
            kickers = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
            return HandValue(HandRank.PAIR, [pair_rank] + kickers)
        
        # High card
        return HandValue(HandRank.HIGH_CARD, ranks)
