from typing import List, Dict
from packages.domain.models import GameState, ActionRecord, GameRound, LiveGameState, ActionType
from .utils import calculate_dryness

class FeatureMapper:
    @staticmethod
    def map_to_live_state(
        state: GameState, 
        history: List[ActionRecord], 
        opponent_stats: Dict
    ) -> LiveGameState:
        """
        Maps current GameState and Action history to the LiveGameState needed for ML.
        
        opponent_stats: { 'vpip': float, 'pfr': float }
        """
        round_map = {
            GameRound.FLOP: 1,
            GameRound.TURN: 2,
            GameRound.RIVER: 3,
            GameRound.PRE_FLOP: 0,
            GameRound.SHOWDOWN: 4
        }
        
        street = round_map.get(state.round, 1)
        board_cards = [str(c) for c in state.community_cards]
        
        # 1. Analyze the last aggressive action in history
        last_bet_amount = 0.0
        last_action_street = state.round
        
        aggressive_actions = [a for a in history if a.action_type in [ActionType.RAISE, ActionType.CALL, ActionType.ALL_IN]]
        
        if aggressive_actions:
            last_action = aggressive_actions[-1]
            last_bet_amount = last_action.amount
            last_action_street = last_action.street
        
        # 2. Pot Before
        # The ML model expects pot_before to be the pot size BEFORE the current bet was placed.
        pot_before = state.pot - last_bet_amount if state.pot > last_bet_amount else state.pot
        
        # 3. Temporal Features (Dryness Delta)
        prev_street_dryness = 1.0
        if street > 1:
            if street == 2: # Currently Turn, prev was Flop
                prev_board = board_cards[:3]
            elif street == 3: # Currently River, prev was Turn
                prev_board = board_cards[:4]
            else:
                prev_board = []
            prev_street_dryness = calculate_dryness(prev_board)

        # 4. Max bet on previous street (for Bet Spike)
        prev_street_max_bet = 0.0
        prev_round = None
        if state.round == GameRound.TURN: prev_round = GameRound.FLOP
        elif state.round == GameRound.RIVER: prev_round = GameRound.TURN
        
        if prev_round:
            prev_street_actions = [a.amount for a in history if a.street == prev_round]
            if prev_street_actions:
                prev_street_max_bet = max(prev_street_actions)

        # 5. Previous action's relative bet size (same hand, previous action)
        prev_action_rel_bet_size = 0.0
        if len(aggressive_actions) >= 2:
            # Approximating previous pot - this is a simplification
            # Ideally we'd have the exact pot size for every action record
            prev_action_rel_bet_size = aggressive_actions[-2].amount / (pot_before + 1e-6)

        # 6. Active player profile
        # We assume the opponent_stats passed in are for the player who made the last_action
        vpip = opponent_stats.get('vpip', 0.25)
        pfr = opponent_stats.get('pfr', 0.18)
        
        # Starting stack for the hand
        # We'll use the current stack + total contributed as a proxy
        active_player = state.players[state.current_player_index] # This might not be the correct player if turn changed
        # Better: find the player by name from last_action
        if aggressive_actions:
            player_name = aggressive_actions[-1].player_name
            for p in state.players:
                if p.name == player_name:
                    active_player = p
                    break

        starting_stack = active_player.stack + active_player.total_contributed
        
        bb = getattr(state, 'big_blind', 1.0)
        if not bb or bb <= 0:
            bb = 1.0
            
        return LiveGameState(
            street=street,
            bet_amount=last_bet_amount / bb,
            pot_before=pot_before / bb,
            starting_stack=starting_stack / bb,
            board_cards=board_cards,
            vpip=vpip,
            pfr=pfr,
            prev_street_dryness=prev_street_dryness,
            prev_street_max_bet=prev_street_max_bet / bb,
            prev_action_bet_size=prev_action_rel_bet_size
        )
