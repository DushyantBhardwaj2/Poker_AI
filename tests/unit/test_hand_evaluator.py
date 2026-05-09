import unittest
from packages.domain.models import Card, Rank, Suit, HandRank
from packages.domain.hand_evaluator import HandEvaluator, HandValue

class TestHandEvaluator(unittest.TestCase):
    def test_high_card(self):
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.JACK, suit=Suit.HEARTS),
            Card(rank=Rank.EIGHT, suit=Suit.CLUBS),
            Card(rank=Rank.FIVE, suit=Suit.DIAMONDS),
            Card(rank=Rank.TWO, suit=Suit.SPADES)
        ]
        value = HandEvaluator.evaluate_5_cards(cards)
        self.assertEqual(value.rank, HandRank.HIGH_CARD)
        self.assertEqual(value.values, [14, 11, 8, 5, 2])

    def test_pair(self):
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.ACE, suit=Suit.HEARTS),
            Card(rank=Rank.EIGHT, suit=Suit.CLUBS),
            Card(rank=Rank.FIVE, suit=Suit.DIAMONDS),
            Card(rank=Rank.TWO, suit=Suit.SPADES)
        ]
        value = HandEvaluator.evaluate_5_cards(cards)
        self.assertEqual(value.rank, HandRank.PAIR)
        self.assertEqual(value.values, [14, 8, 5, 2])

    def test_two_pair(self):
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.ACE, suit=Suit.HEARTS),
            Card(rank=Rank.EIGHT, suit=Suit.CLUBS),
            Card(rank=Rank.EIGHT, suit=Suit.DIAMONDS),
            Card(rank=Rank.TWO, suit=Suit.SPADES)
        ]
        value = HandEvaluator.evaluate_5_cards(cards)
        self.assertEqual(value.rank, HandRank.TWO_PAIR)
        self.assertEqual(value.values, [14, 8, 2])

    def test_three_of_a_kind(self):
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.ACE, suit=Suit.HEARTS),
            Card(rank=Rank.ACE, suit=Suit.CLUBS),
            Card(rank=Rank.FIVE, suit=Suit.DIAMONDS),
            Card(rank=Rank.TWO, suit=Suit.SPADES)
        ]
        value = HandEvaluator.evaluate_5_cards(cards)
        self.assertEqual(value.rank, HandRank.THREE_OF_A_KIND)
        self.assertEqual(value.values, [14, 5, 2])

    def test_straight(self):
        cards = [
            Card(rank=Rank.NINE, suit=Suit.SPADES),
            Card(rank=Rank.EIGHT, suit=Suit.HEARTS),
            Card(rank=Rank.SEVEN, suit=Suit.CLUBS),
            Card(rank=Rank.SIX, suit=Suit.DIAMONDS),
            Card(rank=Rank.FIVE, suit=Suit.SPADES)
        ]
        value = HandEvaluator.evaluate_5_cards(cards)
        self.assertEqual(value.rank, HandRank.STRAIGHT)
        self.assertEqual(value.values, [9])

    def test_ace_low_straight(self):
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.TWO, suit=Suit.HEARTS),
            Card(rank=Rank.THREE, suit=Suit.CLUBS),
            Card(rank=Rank.FOUR, suit=Suit.DIAMONDS),
            Card(rank=Rank.FIVE, suit=Suit.SPADES)
        ]
        value = HandEvaluator.evaluate_5_cards(cards)
        self.assertEqual(value.rank, HandRank.STRAIGHT)
        self.assertEqual(value.values, [5])

    def test_flush(self):
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.JACK, suit=Suit.SPADES),
            Card(rank=Rank.EIGHT, suit=Suit.SPADES),
            Card(rank=Rank.FIVE, suit=Suit.SPADES),
            Card(rank=Rank.TWO, suit=Suit.SPADES)
        ]
        value = HandEvaluator.evaluate_5_cards(cards)
        self.assertEqual(value.rank, HandRank.FLUSH)
        self.assertEqual(value.values, [14, 11, 8, 5, 2])

    def test_full_house(self):
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.ACE, suit=Suit.HEARTS),
            Card(rank=Rank.ACE, suit=Suit.CLUBS),
            Card(rank=Rank.EIGHT, suit=Suit.DIAMONDS),
            Card(rank=Rank.EIGHT, suit=Suit.SPADES)
        ]
        value = HandEvaluator.evaluate_5_cards(cards)
        self.assertEqual(value.rank, HandRank.FULL_HOUSE)
        self.assertEqual(value.values, [14, 8])

    def test_four_of_a_kind(self):
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.ACE, suit=Suit.HEARTS),
            Card(rank=Rank.ACE, suit=Suit.CLUBS),
            Card(rank=Rank.ACE, suit=Suit.DIAMONDS),
            Card(rank=Rank.TWO, suit=Suit.SPADES)
        ]
        value = HandEvaluator.evaluate_5_cards(cards)
        self.assertEqual(value.rank, HandRank.FOUR_OF_A_KIND)
        self.assertEqual(value.values, [14, 2])

    def test_straight_flush(self):
        cards = [
            Card(rank=Rank.NINE, suit=Suit.SPADES),
            Card(rank=Rank.EIGHT, suit=Suit.SPADES),
            Card(rank=Rank.SEVEN, suit=Suit.SPADES),
            Card(rank=Rank.SIX, suit=Suit.SPADES),
            Card(rank=Rank.FIVE, suit=Suit.SPADES)
        ]
        value = HandEvaluator.evaluate_5_cards(cards)
        self.assertEqual(value.rank, HandRank.STRAIGHT_FLUSH)
        self.assertEqual(value.values, [9])

    def test_royal_flush(self):
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.KING, suit=Suit.SPADES),
            Card(rank=Rank.QUEEN, suit=Suit.SPADES),
            Card(rank=Rank.JACK, suit=Suit.SPADES),
            Card(rank=Rank.TEN, suit=Suit.SPADES)
        ]
        value = HandEvaluator.evaluate_5_cards(cards)
        self.assertEqual(value.rank, HandRank.ROYAL_FLUSH)
        self.assertEqual(value.values, [14])

    def test_evaluate_7_cards(self):
        # Best hand should be a Full House (Aces full of Eights)
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.ACE, suit=Suit.HEARTS),
            Card(rank=Rank.ACE, suit=Suit.CLUBS),
            Card(rank=Rank.EIGHT, suit=Suit.DIAMONDS),
            Card(rank=Rank.EIGHT, suit=Suit.SPADES),
            Card(rank=Rank.TWO, suit=Suit.CLUBS),
            Card(rank=Rank.THREE, suit=Suit.DIAMONDS)
        ]
        value = HandEvaluator.evaluate_7_cards(cards)
        self.assertEqual(value.rank, HandRank.FULL_HOUSE)
        self.assertEqual(value.values, [14, 8])

if __name__ == '__main__':
    unittest.main()
