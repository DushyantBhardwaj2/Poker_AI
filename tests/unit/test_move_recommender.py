import unittest
from packages.domain.models import ActionType
from packages.ai.move_recommender import MoveRecommender

class TestMoveRecommender(unittest.TestCase):
    def test_free_check_weak_hand(self):
        # We have a weak hand (20% win prob) and it costs 0 to call
        result = MoveRecommender.recommend(
            win_probability=0.20,
            pot_size=100.0,
            call_amount=0.0,
            player_stack=1000.0
        )
        self.assertEqual(result["action"], ActionType.CHECK.value)
        self.assertEqual(result["ev"], 0.0)

    def test_free_check_strong_hand(self):
        # We have a strong hand (70% win prob) and it costs 0 to call
        result = MoveRecommender.recommend(
            win_probability=0.70,
            pot_size=100.0,
            call_amount=0.0,
            player_stack=1000.0
        )
        self.assertEqual(result["action"], ActionType.RAISE.value)

    def test_positive_ev_call(self):
        # Pot is 100, we need to call 20. Pot odds = 20 / 120 = ~16.6%
        # Our win prob is 25%. This is a profitable call.
        result = MoveRecommender.recommend(
            win_probability=0.25,
            pot_size=100.0,
            call_amount=20.0,
            player_stack=1000.0
        )
        self.assertEqual(result["action"], ActionType.CALL.value)
        self.assertGreater(result["ev"], 0.0)

    def test_negative_ev_fold(self):
        # Pot is 100, we need to call 50. Pot odds = 50 / 150 = ~33.3%
        # Our win prob is 20%. This is unprofitable.
        result = MoveRecommender.recommend(
            win_probability=0.20,
            pot_size=100.0,
            call_amount=50.0,
            player_stack=1000.0
        )
        self.assertEqual(result["action"], ActionType.FOLD.value)
        self.assertLess(result["ev"], 0.0)

    def test_positive_ev_raise(self):
        # Pot is 100, call is 50. Pot odds 33.3%.
        # Win prob is 80%. We should raise for value.
        result = MoveRecommender.recommend(
            win_probability=0.80,
            pot_size=100.0,
            call_amount=50.0,
            player_stack=1000.0
        )
        self.assertEqual(result["action"], ActionType.RAISE.value)
        self.assertGreater(result["ev"], 0.0)

if __name__ == '__main__':
    unittest.main()
