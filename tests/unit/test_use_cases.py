from apps.api.application.start_game import StartGameUseCase
from packages.domain.models import GameRound

def test_start_game_use_case():
    use_case = StartGameUseCase()
    player_names = ["Alice", "Bob"]
    stacks = [1000, 1000]
    game = use_case.execute(player_names, stacks, 10, 20)
    
    assert len(game.players) == 2
    assert game.players[0].name == "Alice"
    assert game.small_blind == 10
    assert game.big_blind == 20
    assert game.round == GameRound.PRE_FLOP
    print("StartGame use case test passed!")

def test_start_game_manual_blinds():
    use_case = StartGameUseCase()
    player_names = ["Alice", "Bob", "Charlie"]
    stacks = [1000, 1000, 1000]
    # Alice (0) is Dealer, Bob (1) is SB, Charlie (2) is BB by default.
    # We want Charlie (2) as SB and Alice (0) as BB.
    game = use_case.execute(player_names, stacks, 10, 20, dealer_index=1, sb_index=2, bb_index=0)
    
    assert game.players[2].current_bet == 10 # Charlie is SB
    assert game.players[0].current_bet == 20 # Alice is BB
    assert game.current_player_index == 1 # After BB (0) is 1
    print("Manual blind assignment test passed!")

if __name__ == "__main__":
    test_start_game_use_case()
    test_start_game_manual_blinds()
