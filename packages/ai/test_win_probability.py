import unittest
from packages.domain.models import Card, Rank, Suit
from packages.ai.win_probability import WinProbabilityCalculator

class TestWinProbability(unittest.TestCase):
    def test_pocket_aces_preflop(self):
        # Pocket Aces should have a high win probability preflop against 1 opponent
        hole_cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.ACE, suit=Suit.HEARTS)
        ]
        
        # 100 simulations is enough for a quick test
        result = WinProbabilityCalculator.calculate(
            hole_cards=hole_cards,
            community_cards=[],
            num_opponents=1,
            num_simulations=100
        )
        
        self.assertGreater(result["win_probability"], 0.70)
        self.assertLess(result["win_probability"], 1.0)
        self.assertGreaterEqual(result["equity"], result["win_probability"])

    def test_seven_deuce_offsuit_preflop(self):
        # 7-2 offsuit is a very weak hand
        hole_cards = [
            Card(rank=Rank.SEVEN, suit=Suit.SPADES),
            Card(rank=Rank.TWO, suit=Suit.HEARTS)
        ]
        
        result = WinProbabilityCalculator.calculate(
            hole_cards=hole_cards,
            community_cards=[],
            num_opponents=2,
            num_simulations=100
        )
        
        self.assertLess(result["win_probability"], 0.40)

    def test_made_flush_on_turn(self):
        hole_cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.KING, suit=Suit.SPADES)
        ]
        community_cards = [
            Card(rank=Rank.QUEEN, suit=Suit.SPADES),
            Card(rank=Rank.JACK, suit=Suit.SPADES),
            Card(rank=Rank.TWO, suit=Suit.SPADES),
            Card(rank=Rank.FOUR, suit=Suit.HEARTS)
        ]
        
        result = WinProbabilityCalculator.calculate(
            hole_cards=hole_cards,
            community_cards=community_cards,
            num_opponents=1,
            num_simulations=100
        )
        
        # Nut flush on the turn should be 100% win if no straight flush possible, 
        # wait, a straight flush IS possible (10s gives royal flush) but WE hold A-K-Q-J of spades,
        # wait, we need exactly 10s to get Royal Flush, but we already have the nut flush.
        # Actually no one can beat us except if they have the 10s, but we already have AKQJ2 of spades.
        # Oh, if someone has the 10s, they have a straight flush. But no one can have it because we have AK, board has QJ2. 10s gives SF.
        # Actually our hand IS a flush (A high). The board has QJ2s. So we have AKQJ2s.
        # If someone has 10s 9s, they have QJ109s, they don't have A high flush. We do. We have the best flush.
        # So our win rate should be 1.0.
        self.assertGreater(result["win_probability"], 0.90)

if __name__ == '__main__':
    unittest.main()
