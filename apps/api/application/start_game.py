from typing import List
from packages.domain.models import GameState, Player, GameRound, Pot, PlayerStatus
from packages.domain.deck import Deck

class StartGameUseCase:
    def execute(self, player_names: List[str], initial_stacks: List[float], small_blind: float, big_blind: float, dealer_index: int = 0, sb_index: int = -1, bb_index: int = -1) -> GameState:
        deck = Deck()
        players = []
        for name, stack in zip(player_names, initial_stacks):
            # Do NOT deal cards automatically for live analysis
            players.append(Player(name=name, stack=stack, hole_cards=[], status=PlayerStatus.ACTIVE))
        
        # Initial blinds
        num_players = len(players)
        dealer_idx = dealer_index % num_players
        
        if sb_index != -1 and bb_index != -1:
            sb_idx = sb_index % num_players
            bb_idx = bb_index % num_players
            # Start player is usually after BB
            current_player_idx = (bb_idx + 1) % num_players
        elif num_players == 2:
            sb_idx = dealer_idx
            bb_idx = (dealer_idx + 1) % num_players
            current_player_idx = sb_idx # SB acts first pre-flop in heads-up
        else:
            sb_idx = (dealer_idx + 1) % num_players
            bb_idx = (dealer_idx + 2) % num_players
            current_player_idx = (dealer_idx + 3) % num_players
        
        # Ensure we don't pick someone out of bounds
        sb_idx = sb_idx % num_players
        bb_idx = bb_idx % num_players
        
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
            pots=[Pot(amount=small_blind + big_blind, eligible_player_indices=list(range(num_players)))],
            pot=small_blind + big_blind,
            current_bet=big_blind,
            last_raise_amount=big_blind,
            round=GameRound.PRE_FLOP,
            current_player_index=current_player_idx,
            dealer_index=dealer_idx
        )
