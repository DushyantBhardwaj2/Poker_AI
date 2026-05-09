from typing import List, Dict, Tuple
from packages.domain.models import GameState, Player, Pot
from packages.domain.hand_evaluator import HandEvaluator, HandValue

class ShowdownUseCase:
    def execute(self, state: GameState) -> Tuple[GameState, Dict]:
        # 1. Determine all pots based on contributions
        # Standard side pot logic
        pots = self._calculate_pots(state.players)
        
        results = []
        
        # 2. Evaluate hands for all non-folded players
        player_hand_values = {}
        for i, player in enumerate(state.players):
            if not player.is_folded:
                all_cards = player.hole_cards + state.community_cards
                if len(all_cards) >= 5:
                    hand_value = HandEvaluator.evaluate_7_cards(all_cards) if len(all_cards) >= 5 else None
                    player_hand_values[i] = hand_value
                else:
                    player_hand_values[i] = None

        # 3. Distribute each pot
        for pot_idx, pot in enumerate(pots):
            # Only non-folded players who are eligible can win this pot
            eligible_winners = [idx for idx in pot.eligible_player_indices if not state.players[idx].is_folded]
            
            if not eligible_winners:
                # Standard rule: the last remaining player wins everything.
                remaining_players = [i for i, p in enumerate(state.players) if not p.is_folded]
                if remaining_players:
                    winners = [remaining_players[0]]
                else:
                    continue 
            else:
                # Find winners for this specific pot
                best_value = None
                winners = []
                
                # If only one eligible winner (e.g. others folded), they win automatically
                if len(eligible_winners) == 1:
                    winners = [eligible_winners[0]]
                else:
                    for idx in eligible_winners:
                        hand_value = player_hand_values.get(idx)
                        if hand_value is None:
                            # If we can't evaluate, and there are multiple players, this is an error state
                            # but for now let's just pick one or handle it gracefully
                            if not winners: winners = [idx]
                            continue

                        if best_value is None or hand_value > best_value:
                            best_value = hand_value
                            winners = [idx]
                        elif hand_value == best_value:
                            winners.append(idx)
            
            # Divide pot using integer arithmetic on cents to avoid rounding errors
            # Distribute remainder to first winner (standard casino rule)
            amount_cents = int(round(pot.amount * 100))
            win_cents = amount_cents // len(winners)
            remainder_cents = amount_cents % len(winners)
            win_amount = win_cents / 100.0
            remainder = remainder_cents / 100.0
            for w_idx in winners:
                state.players[w_idx].stack += win_amount
            # Give remainder to the first winner (deterministic, no lost chips)
            if remainder > 0 and winners:
                state.players[winners[0]].stack += remainder
            
            results.append({
                "pot_index": pot_idx,
                "amount": pot.amount,
                "winners": [state.players[w_idx].name for w_idx in winners],
                "hand_rank": player_hand_values[winners[0]].rank.name if winners and player_hand_values.get(winners[0]) else "N/A"
            })
            
        state.pot = 0
        state.pots = []
        
        return state, {
            "pots_results": results,
            "total_pot": sum(p.amount for p in pots)
        }

    def _calculate_pots(self, players: List[Player]) -> List[Pot]:
        # Get all unique contribution amounts from ALL players (even folded)
        contributions = [p.total_contributed for p in players if p.total_contributed > 0]
        if not contributions:
            return []
            
        unique_amounts = sorted(list(set(contributions)))
        
        pots = []
        prev_amount = 0
        for amount in unique_amounts:
            current_pot_chunk = amount - prev_amount
            # Who is eligible for this chunk? 
            # Only those who contributed at least 'amount' AND have not folded?
            # No, eligibility is based on contribution. Folding removes them from winning,
            # but their money stays in.
            eligible_players = [i for i, p in enumerate(players) if p.total_contributed >= amount]
            
            # Total chips in this pot chunk
            total_chunk_amount = 0
            for p in players:
                # Every player contributes at most (amount - prev_amount) to this pot chunk
                total_chunk_amount += min(max(p.total_contributed - prev_amount, 0), current_pot_chunk)
            
            if total_chunk_amount > 0:
                pots.append(Pot(amount=total_chunk_amount, eligible_player_indices=eligible_players))
            
            prev_amount = amount
            
        return pots
