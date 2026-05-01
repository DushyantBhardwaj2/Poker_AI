from typing import List, Dict, Tuple
from packages.domain.models import GameState, Player, Pot
from packages.domain.hand_evaluator import HandEvaluator, HandValue

class ShowdownUseCase:
    def execute(self, state: GameState) -> Dict:
        # 1. Determine all pots based on contributions
        # Standard side pot logic
        pots = self._calculate_pots(state.players)
        
        results = []
        
        # 2. Evaluate hands for all non-folded players
        player_hand_values = {}
        for i, player in enumerate(state.players):
            if not player.is_folded:
                # In a real game, if community cards are missing, we should handle that.
                # Assuming 5 community cards are present for showdown.
                hand_value = HandEvaluator.evaluate_7_cards(player.hole_cards + state.community_cards)
                player_hand_values[i] = hand_value

        # 3. Distribute each pot
        for pot_idx, pot in enumerate(pots):
            # Only non-folded players who are eligible can win this pot
            eligible_winners = [idx for idx in pot.eligible_player_indices if not state.players[idx].is_folded]
            
            if not eligible_winners:
                # If everyone eligible folded (shouldn't happen in standard poker as the last one wins)
                # but let's handle it by giving it to the last folder? No, the pot should have been closed.
                # Standard rule: the last remaining player wins everything.
                # If everyone in a side pot folded, it goes to the remaining player.
                remaining_players = [i for i, p in enumerate(state.players) if not p.is_folded]
                if remaining_players:
                    winners = [remaining_players[0]]
                    best_value = player_hand_values.get(winners[0])
                else:
                    continue # No one to give it to?
            else:
                # Find winners for this specific pot
                best_value = None
                winners = []
                
                for idx in eligible_winners:
                    hand_value = player_hand_values[idx]
                    if best_value is None or hand_value > best_value:
                        best_value = hand_value
                        winners = [idx]
                    elif hand_value == best_value:
                        winners.append(idx)
            
            # Divide pot
            win_amount = pot.amount / len(winners)
            for w_idx in winners:
                state.players[w_idx].stack += win_amount
            
            results.append({
                "pot_index": pot_idx,
                "amount": pot.amount,
                "winners": [state.players[w_idx].name for w_idx in winners],
                "hand_rank": best_value.rank.name if best_value else "N/A"
            })
            
        state.pot = 0
        state.pots = []
        
        return {
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
