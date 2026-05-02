from typing import List
from packages.domain.models import GameState, Player, GameRound, Pot
from packages.domain.deck import Deck

class StartGameUseCase:
    def execute(self, player_names: List[str], initial_stacks: List[float], small_blind: float, big_blind: float) -> GameState:
        deck = Deck()
        players = []
        for name, stack in zip(player_names, initial_stacks):
            # Do NOT deal cards automatically for live analysis
            players.append(Player(name=name, stack=stack, hole_cards=[]))
        
        # Initial blinds
        sb_idx = 1 % len(players)
        bb_idx = 2 % len(players)
        
        players[sb_idx].stack -= small_blind
        players[sb_idx].current_bet = small_blind
        players[sb_idx].total_contributed = small_blind
        
        players[bb_idx].stack -= big_blind
        players[bb_idx].current_bet = big_blind
        players[bb_idx].total_contributed = big_blind
        
        return GameState(
            players=players,
            small_blind=small_blind,
            big_blind=big_blind,
            pots=[Pot(amount=small_blind + big_blind, eligible_player_indices=list(range(len(players))))],
            pot=small_blind + big_blind,
            current_bet=big_blind,
            last_raise_amount=big_blind,
            round=GameRound.PRE_FLOP,
            current_player_index=(3 % len(players)),
            dealer_index=0
        )
