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

        # We hold the nut flush: A-K-Q-J-2 of spades. A straight flush needs the
        # ten of spades plus a second spade, and the only spades left are the ten
        # and the nine, so the one hand that beats us is exactly Ts9s. It should
        # lose almost never, not never.
        self.assertGreater(result["win_probability"], 0.90)


class TestWinProbabilityValidation(unittest.TestCase):
    """The invalid inputs that used to return a number instead of raising.

    num_simulations=0 divided by zero, and a negative count made range() empty,
    so wins/num_simulations returned -0.0 and the caller got a confident
    win_probability of -0.0 with no error anywhere.
    """

    HOLE = [
        Card(rank=Rank.ACE, suit=Suit.SPADES),
        Card(rank=Rank.KING, suit=Suit.SPADES),
    ]

    def calculate(self, **overrides):
        kwargs = dict(
            hole_cards=self.HOLE,
            community_cards=[],
            num_opponents=1,
            num_simulations=10,
        )
        kwargs.update(overrides)
        return WinProbabilityCalculator.calculate(**kwargs)

    def test_zero_simulations_is_rejected(self):
        with self.assertRaises(ValueError):
            self.calculate(num_simulations=0)

    def test_negative_simulations_is_rejected(self):
        with self.assertRaises(ValueError):
            self.calculate(num_simulations=-5)

    def test_float_simulations_is_rejected(self):
        # range() would raise TypeError from deep inside the loop instead.
        with self.assertRaises(ValueError):
            self.calculate(num_simulations=1000.0)

    def test_simulation_count_is_capped(self):
        cap = WinProbabilityCalculator.MAX_SIMULATIONS
        with self.assertRaises(ValueError):
            self.calculate(num_simulations=cap + 1)

    def test_opponent_count_is_bounded_by_the_deck(self):
        # 2 hole + 5 board + 2 per opponent has to fit in 52. Past that the deal
        # ran off the end of the deck and still returned a probability.
        with self.assertRaises(ValueError):
            self.calculate(num_opponents=25)

    def test_zero_opponents_is_rejected(self):
        with self.assertRaises(ValueError):
            self.calculate(num_opponents=0)

    def test_wrong_number_of_hole_cards_is_rejected(self):
        with self.assertRaises(ValueError):
            self.calculate(hole_cards=self.HOLE[:1])


if __name__ == '__main__':
    unittest.main()
