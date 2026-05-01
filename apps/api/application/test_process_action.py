import unittest
from packages.domain.models import GameState, Player, Action, ActionType, GameRound
from apps.api.application.start_game import StartGameUseCase
from apps.api.application.process_action import ProcessActionUseCase

class TestProcessAction(unittest.TestCase):
    def setUp(self):
        self.start_use_case = StartGameUseCase()
        self.process_use_case = ProcessActionUseCase()
        self.state = self.start_use_case.execute(
            ["Alice", "Bob", "Charlie", "David"],
            [1000, 1000, 1000, 1000],
            10,
            20
        )

    def test_initial_state(self):
        # Alice (0), Bob (1, SB), Charlie (2, BB), David (3, Current)
        self.assertEqual(self.state.current_player_index, 3)
        self.assertEqual(self.state.pot, 30)
        self.assertEqual(self.state.current_bet, 20)
        self.assertEqual(self.state.players[1].current_bet, 10)
        self.assertEqual(self.state.players[2].current_bet, 20)

    def test_david_calls(self):
        action = Action(player_index=3, action_type=ActionType.CALL)
        new_state = self.process_use_case.execute(self.state, action)
        
        self.assertEqual(new_state.players[3].stack, 980)
        self.assertEqual(new_state.players[3].current_bet, 20)
        self.assertEqual(new_state.pot, 50)
        self.assertEqual(new_state.current_player_index, 0)

    def test_full_round_preflop(self):
        # 3 calls
        self.state = self.process_use_case.execute(self.state, Action(player_index=3, action_type=ActionType.CALL))
        # 0 calls
        self.state = self.process_use_case.execute(self.state, Action(player_index=0, action_type=ActionType.CALL))
        # 1 calls (SB needs to add 10)
        self.state = self.process_use_case.execute(self.state, Action(player_index=1, action_type=ActionType.CALL))
        
        self.assertEqual(self.state.players[1].current_bet, 20)
        self.assertEqual(self.state.current_player_index, 2) # BB turn
        
        # 2 checks (BB can check if no one raised)
        self.state = self.process_use_case.execute(self.state, Action(player_index=2, action_type=ActionType.CHECK))
        
        # Round should advance to FLOP
        self.assertEqual(self.state.round, GameRound.FLOP)
        self.assertEqual(self.state.current_bet, 0)
        self.assertEqual(self.state.players[0].current_bet, 0)
        self.assertEqual(self.state.current_player_index, 1) # SB is first to act on flop

    def test_david_raises(self):
        # David raises to 100
        action = Action(player_index=3, action_type=ActionType.RAISE, amount=100)
        new_state = self.process_use_case.execute(self.state, action)
        
        self.assertEqual(new_state.current_bet, 100)
        self.assertEqual(new_state.last_raise_amount, 80) # 100 - 20
        self.assertEqual(new_state.players[3].current_bet, 100)
        self.assertEqual(new_state.players[3].stack, 900)
        self.assertEqual(new_state.pot, 130) # 10(SB) + 20(BB) + 100(David)

if __name__ == '__main__':
    unittest.main()
