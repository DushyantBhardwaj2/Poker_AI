import unittest
from packages.domain.models import GameState, Player, Card, Rank, Suit, Pot
from apps.api.application.showdown import ShowdownUseCase

class TestShowdown(unittest.TestCase):
    def setUp(self):
        self.showdown_use_case = ShowdownUseCase()

    def test_simple_showdown(self):
        players = [
            Player(name="Alice", stack=0, hole_cards=[
                Card(rank=Rank.ACE, suit=Suit.SPADES),
                Card(rank=Rank.ACE, suit=Suit.HEARTS)
            ], total_contributed=100),
            Player(name="Bob", stack=0, hole_cards=[
                Card(rank=Rank.KING, suit=Suit.SPADES),
                Card(rank=Rank.KING, suit=Suit.HEARTS)
            ], total_contributed=100)
        ]
        community_cards = [
            Card(rank=Rank.TWO, suit=Suit.CLUBS),
            Card(rank=Rank.THREE, suit=Suit.DIAMONDS),
            Card(rank=Rank.FOUR, suit=Suit.SPADES),
            Card(rank=Rank.FIVE, suit=Suit.HEARTS),
            Card(rank=Rank.SEVEN, suit=Suit.CLUBS)
        ]
        state = GameState(
            players=players,
            community_cards=community_cards,
            pot=200,
            small_blind=10,
            big_blind=20
        )
        
        result = self.showdown_use_case.execute(state)
        
        self.assertEqual(result["pots_results"][0]["winners"], ["Alice"])
        self.assertEqual(state.players[0].stack, 200)

    def test_side_pot_showdown(self):
        # Alice is all-in for 100
        # Bob and Charlie both call 200
        players = [
            Player(name="Alice", stack=0, hole_cards=[
                Card(rank=Rank.ACE, suit=Suit.SPADES),
                Card(rank=Rank.ACE, suit=Suit.HEARTS)
            ], total_contributed=100),
            Player(name="Bob", stack=0, hole_cards=[
                Card(rank=Rank.KING, suit=Suit.SPADES),
                Card(rank=Rank.KING, suit=Suit.HEARTS)
            ], total_contributed=200),
            Player(name="Charlie", stack=0, hole_cards=[
                Card(rank=Rank.QUEEN, suit=Suit.SPADES),
                Card(rank=Rank.QUEEN, suit=Suit.HEARTS)
            ], total_contributed=200)
        ]
        community_cards = [
            Card(rank=Rank.TWO, suit=Suit.CLUBS),
            Card(rank=Rank.THREE, suit=Suit.DIAMONDS),
            Card(rank=Rank.FOUR, suit=Suit.SPADES),
            Card(rank=Rank.FIVE, suit=Suit.HEARTS),
            Card(rank=Rank.SEVEN, suit=Suit.CLUBS)
        ]
        state = GameState(
            players=players,
            community_cards=community_cards,
            pot=500,
            small_blind=10,
            big_blind=20
        )
        
        result = self.showdown_use_case.execute(state)
        
        # Pot 0: 300 (Alice vs Bob vs Charlie). Alice wins with Aces.
        # Pot 1: 200 (Bob vs Charlie). Bob wins with Kings.
        
        self.assertEqual(len(result["pots_results"]), 2)
        self.assertEqual(result["pots_results"][0]["amount"], 300)
        self.assertEqual(result["pots_results"][0]["winners"], ["Alice"])
        
        self.assertEqual(result["pots_results"][1]["amount"], 200)
        self.assertEqual(result["pots_results"][1]["winners"], ["Bob"])
        
        self.assertEqual(state.players[0].stack, 300)
        self.assertEqual(state.players[1].stack, 200)
        self.assertEqual(state.players[2].stack, 0)

if __name__ == '__main__':
    unittest.main()
