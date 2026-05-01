from packages.domain.models import Card, Rank, Suit, Player, GameState, GameRound

def test_card_creation():
    card = Card(rank=Rank.ACE, suit=Suit.SPADES)
    assert str(card) == "As"

def test_game_state_initialization():
    players = [
        Player(name="Alice", stack=1000),
        Player(name="Bob", stack=1000)
    ]
    game = GameState(
        players=players,
        small_blind=10,
        big_blind=20
    )
    assert len(game.players) == 2
    assert game.small_blind == 10
    assert game.round == GameRound.PRE_FLOP

if __name__ == "__main__":
    test_card_creation()
    test_game_state_initialization()
    print("Domain model tests passed!")
