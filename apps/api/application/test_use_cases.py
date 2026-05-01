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

if __name__ == "__main__":
    test_start_game_use_case()
