from packages.domain.models import GameState, Action, ActionType, Player, GameRound

class ProcessActionUseCase:
    def execute(self, state: GameState, action: Action) -> GameState:
        # 1. Validate player
        if action.player_index != state.current_player_index:
            raise ValueError(f"Not this player's turn. Expected {state.current_player_index}, got {action.player_index}")

        player = state.players[action.player_index]
        if player.is_folded or player.is_all_in:
             raise ValueError("Player cannot act (folded or all-in)")

        # 2. Process Action
        if action.action_type == ActionType.FOLD:
            player.is_folded = True
            player.has_acted = True
        
        elif action.action_type == ActionType.CHECK:
            if player.current_bet < state.current_bet:
                raise ValueError("Cannot check when there is a bet to call")
            player.has_acted = True

        elif action.action_type == ActionType.CALL:
            if state.round == GameRound.PRE_FLOP:
                player.vpip_this_hand = True
            
            call_amount = state.current_bet - player.current_bet
            if call_amount >= player.stack:
                # Go all in
                actual_call = player.stack
                player.current_bet += actual_call
                player.total_contributed += actual_call
                state.pot += actual_call
                player.stack = 0
                player.is_all_in = True
            else:
                player.current_bet += call_amount
                player.total_contributed += call_amount
                state.pot += call_amount
                player.stack -= call_amount
            player.has_acted = True

        elif action.action_type == ActionType.RAISE:
            if state.round == GameRound.PRE_FLOP:
                player.vpip_this_hand = True
                player.pfr_this_hand = True
                
            # action.amount is the TOTAL bet this player wants to have in front of them
            # Minimum raise check
            added_amount = action.amount - state.current_bet
            if added_amount < state.last_raise_amount and action.amount < (player.stack + player.current_bet):
                 # Allow if it's an all-in that is less than min raise? 
                 # For now, let's be strict or at least update last_raise if it's a full raise
                 pass
            
            total_to_subtract = action.amount - player.current_bet
            if total_to_subtract >= player.stack:
                # All-in raise
                actual_subtract = player.stack
                new_total_bet = player.current_bet + actual_subtract
                player.total_contributed += actual_subtract
                state.pot += actual_subtract
                player.stack = 0
                player.is_all_in = True
                
                if new_total_bet > state.current_bet:
                    diff = new_total_bet - state.current_bet
                    if diff > state.last_raise_amount:
                        state.last_raise_amount = diff
                    state.current_bet = new_total_bet
                player.current_bet = new_total_bet
            else:
                state.pot += total_to_subtract
                player.total_contributed += total_to_subtract
                player.stack -= total_to_subtract
                
                diff = action.amount - state.current_bet
                state.last_raise_amount = diff
                state.current_bet = action.amount
                player.current_bet = action.amount

            # Reset has_acted for others because someone raised
            for i, p in enumerate(state.players):
                if i != action.player_index and not p.is_folded and not p.is_all_in:
                    p.has_acted = False
            player.has_acted = True

        # 3. Move to next player
        state.current_player_index = self._get_next_player_index(state)

        # 4. Check if round finished
        if self._is_round_finished(state):
            self._advance_round(state)

        return state

    def _get_next_player_index(self, state: GameState) -> int:
        num_players = len(state.players)
        for i in range(1, num_players + 1):
            idx = (state.current_player_index + i) % num_players
            p = state.players[idx]
            if not p.is_folded and not p.is_all_in:
                return idx
        return state.current_player_index

    def _is_round_finished(self, state: GameState) -> bool:
        active_players = [p for p in state.players if not p.is_folded and not p.is_all_in]
        
        # If only one active player remains, the round is effectively over (everyone else folded)
        if len(active_players) <= 1:
            # Special case: if there are all-in players, we might need to continue rounds 
            # but without betting. For now, let's just check if everyone has acted.
            pass

        for p in state.players:
            if p.is_folded or p.is_all_in:
                continue
            if not p.has_acted or p.current_bet < state.current_bet:
                return False
        return True

    def _advance_round(self, state: GameState):
        # Reset player bets for the new round
        for p in state.players:
            p.current_bet = 0.0
            p.has_acted = False
        
        state.current_bet = 0.0
        state.last_raise_amount = state.big_blind
        
        rounds = list(GameRound)
        current_idx = rounds.index(state.round)
        if current_idx < len(rounds) - 1:
            state.round = rounds[current_idx + 1]
        
        # Reset current player to the first one after dealer
        num_players = len(state.players)
        idx = (state.dealer_index + 1) % num_players
        p = state.players[idx]
        if p.is_folded or p.is_all_in:
            state.current_player_index = idx
            state.current_player_index = self._get_next_player_index(state)
        else:
            state.current_player_index = idx
