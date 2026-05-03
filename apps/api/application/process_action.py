from packages.domain.models import GameState, Action, ActionType, Player, GameRound, Pot, PlayerStatus

class ProcessActionUseCase:
    def execute(self, state: GameState, action: Action) -> GameState:
        # 1. Validate player
        if action.player_index != state.current_player_index:
            raise ValueError(f"Not this player's turn. Expected {state.current_player_index}, got {action.player_index}")

        player = state.players[action.player_index]
        if player.status in [PlayerStatus.FOLDED, PlayerStatus.ALL_IN, PlayerStatus.SITTING_OUT]:
             raise ValueError(f"Player cannot act (status: {player.status})")

        # 2. Process Action
        if action.action_type == ActionType.FOLD:
            player.status = PlayerStatus.FOLDED
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
                player.status = PlayerStatus.ALL_IN
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
                
            total_to_subtract = action.amount - player.current_bet
            if total_to_subtract >= player.stack:
                # All-in raise
                actual_subtract = player.stack
                new_total_bet = player.current_bet + actual_subtract
                player.total_contributed += actual_subtract
                state.pot += actual_subtract
                player.stack = 0
                player.status = PlayerStatus.ALL_IN
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
                if i != action.player_index and p.status == PlayerStatus.ACTIVE:
                    p.has_acted = False
            player.has_acted = True

        elif action.action_type == ActionType.ALL_IN:
            if state.round == GameRound.PRE_FLOP:
                player.vpip_this_hand = True
                if player.stack + player.current_bet > state.current_bet:
                    player.pfr_this_hand = True
            
            all_in_amount = player.stack + player.current_bet
            
            if all_in_amount > state.current_bet:
                diff = all_in_amount - state.current_bet
                if diff > state.last_raise_amount:
                    state.last_raise_amount = diff
                state.current_bet = all_in_amount
                # Reset has_acted for others
                for i, p in enumerate(state.players):
                    if i != action.player_index and p.status == PlayerStatus.ACTIVE:
                        p.has_acted = False
            
            state.pot += player.stack
            player.total_contributed += player.stack
            player.stack = 0
            player.current_bet = all_in_amount
            player.status = PlayerStatus.ALL_IN
            player.is_all_in = True
            player.has_acted = True

        # 3. Update side pots display
        state.pots = self._calculate_current_pots(state.players)

        # 4. Move to next player
        state.current_player_index = self._get_next_player_index(state)

        # 5. Check if round finished and advance if needed
        while self._is_round_finished(state) and state.round != GameRound.SHOWDOWN:
            self._advance_round(state)
        
        # 6. Check if hand is over (only one player remains)
        active_players = [p for p in state.players if p.status != PlayerStatus.FOLDED and p.status != PlayerStatus.SITTING_OUT]
        if len(active_players) == 1:
            state.round = GameRound.SHOWDOWN

        return state

    def _calculate_current_pots(self, players: list[Player]) -> list[Pot]:
        contributions = [p.total_contributed for p in players if p.total_contributed > 0]
        if not contributions:
            return [Pot(amount=0, eligible_player_indices=[])]
            
        unique_amounts = sorted(list(set(contributions)))
        pots = []
        prev_amount = 0
        for amount in unique_amounts:
            current_pot_chunk = amount - prev_amount
            eligible_players = [i for i, p in enumerate(players) if p.total_contributed >= amount]
            
            total_chunk_amount = 0
            for p in players:
                total_chunk_amount += min(max(p.total_contributed - prev_amount, 0), current_pot_chunk)
            
            if total_chunk_amount > 0:
                pots.append(Pot(amount=total_chunk_amount, eligible_player_indices=eligible_players))
            prev_amount = amount
            
        return pots if pots else [Pot(amount=0, eligible_player_indices=[])]

    def _get_next_player_index(self, state: GameState) -> int:
        num_players = len(state.players)
        for i in range(1, num_players + 1):
            idx = (state.current_player_index + i) % num_players
            p = state.players[idx]
            if p.status == PlayerStatus.ACTIVE:
                return idx
        return state.current_player_index

    def _is_round_finished(self, state: GameState) -> bool:
        active_players = [p for p in state.players if p.status == PlayerStatus.ACTIVE]
        
        if len(active_players) <= 1:
            return True

        for p in state.players:
            if p.status != PlayerStatus.ACTIVE:
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
        if p.status != PlayerStatus.ACTIVE:
            state.current_player_index = idx
            state.current_player_index = self._get_next_player_index(state)
        else:
            state.current_player_index = idx
