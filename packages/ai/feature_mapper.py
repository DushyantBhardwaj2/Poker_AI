from typing import List, Dict, Optional
from packages.domain.models import GameState, ActionRecord, GameRound, LiveGameState, ActionType
from .utils import calculate_dryness

class FeatureMapper:
    @staticmethod
    def map_to_live_state(
        state: GameState, 
        history: List[ActionRecord], 
        opponent_stats: Dict,
        opponent_name: Optional[str] = None
    ) -> LiveGameState:
        """
        Maps current GameState and Action history to the LiveGameState needed for ML.
        
        opponent_stats: { 'vpip': float, 'pfr': float }
        opponent_name: if provided, only considers actions by this player as the
                       current bet action. Falls back safely when not given.
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
        current_street = state.round

        # ---- Build candidate action lists for the CURRENT-STREET bet action ----
        # Start with all current-street actions, optionally filtered by opponent
        current_street_candidates = [
            a for a in history if a.street == current_street
        ]
        if opponent_name:
            current_street_candidates = [
                a for a in current_street_candidates if a.player_name == opponent_name
            ]

        # Primary aggressive actions on current street: RAISE and ALL_IN
        primary_current = [
            a for a in current_street_candidates
            if a.action_type in (ActionType.RAISE, ActionType.ALL_IN)
        ]
        # Broader committed actions on current street: include CALL
        committed_current = [
            a for a in current_street_candidates
            if a.action_type in (ActionType.RAISE, ActionType.CALL, ActionType.ALL_IN)
        ]

        # ---- Select the action that defines the current bet ----
        last_bet_amount = 0.0
        last_action_street = current_street
        selected_action = None

        if primary_current:
            selected_action = primary_current[-1]
        elif committed_current:
            selected_action = committed_current[-1]

        if selected_action:
            last_bet_amount = selected_action.amount
            last_action_street = selected_action.street

        # ---- Whole-hand committed actions (for aggregate temporal features) ----
        all_committed_actions = [
            a for a in history
            if a.action_type in (ActionType.RAISE, ActionType.CALL, ActionType.ALL_IN)
        ]

        # 2. Pot Before
        pot_before = state.pot - last_bet_amount if state.pot > last_bet_amount else state.pot

        # 3. Temporal Features (Dryness Delta)
        prev_street_dryness = 1.0
        if street > 1:
            if street == 2:
                prev_board = board_cards[:3]
            elif street == 3:
                prev_board = board_cards[:4]
            else:
                prev_board = []
            prev_street_dryness = calculate_dryness(prev_board)

        # 4. Max bet on previous street (for Bet Spike)
        prev_street_max_bet = 0.0
        prev_round = None
        if state.round == GameRound.TURN:
            prev_round = GameRound.FLOP
        elif state.round == GameRound.RIVER:
            prev_round = GameRound.TURN

        if prev_round:
            prev_street_amounts = [a.amount for a in history if a.street == prev_round]
            if prev_street_amounts:
                prev_street_max_bet = max(prev_street_amounts)

        # 5. Previous action's relative bet size (whole-hand, same-hand)
        prev_action_rel_bet_size = 0.0
        if len(all_committed_actions) >= 2:
            prev_action_rel_bet_size = all_committed_actions[-2].amount / (pot_before + 1e-6)

        # 6. Active player profile
        vpip = opponent_stats.get('vpip', 0.25)
        pfr = opponent_stats.get('pfr', 0.18)

        # Starting stack: use selected action's player when available
        active_player = state.players[state.current_player_index]
        if selected_action:
            for p in state.players:
                if p.name == selected_action.player_name:
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
