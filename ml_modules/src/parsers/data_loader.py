"""
PHH (Poker Hand History) Parser & Loader

Parses poker hand history files using pokerkit library.
Filters for NLHE hands and extracts action sequences per Data Contract 2.1.
"""

import os
import re
import logging
from pathlib import Path
from typing import Generator, List, Dict, Any, Optional
import pandas as pd
import pokerkit
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PHHParser:
    """Parses Poker Hand History files using pokerkit."""
    
    VARIANT_NLHE = "NT"
    
    def __init__(self, failed_log_path: str = "failed_parses.log"):
        self.failed_log_path = failed_log_path
        self.failed_count = 0
        self.parsed_count = 0
        self.skipped_variant_count = 0
        
    def log_failed_parse(self, filename: str, error: str) -> None:
        self.failed_count += 1
        log_entry = f"{filename}: {error}"
        with open(self.failed_log_path, 'a') as f:
            f.write(log_entry + "\n")
        logger.warning(f"Failed to parse {filename}: {error}")
    
    def extract_hand_id(self, file_path: str, hand_index: int) -> str:
        path = Path(file_path)
        parts = list(path.with_suffix('').parts)
        if 'poker-hand-histories' in parts:
            start_index = parts.index('poker-hand-histories') + 1
            parts = parts[start_index:]
        base_name = "_".join(parts)
        return f"{base_name}_{hand_index:06d}"

    def parse_phh_file(self, file_path: str) -> Generator[Dict[str, Any], None, None]:
        filename = Path(file_path).name
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.log_failed_parse(filename, f"File read error: {str(e)}")
            return
            
        # Detect multi-hand format (e.g. [1], [2], ...)
        if re.search(r'^\[\d+\]', content, re.MULTILINE):
            hand_contents = re.split(r'^\[\d+\]', content, flags=re.MULTILINE)
            hand_contents = [h.strip() for h in hand_contents if h.strip()]
        else:
            hand_contents = [content]
        
        for hand_idx, hand_text in enumerate(hand_contents):
            try:
                hand = pokerkit.HandHistory.loads(hand_text)
                if hand.variant != self.VARIANT_NLHE:
                    self.skipped_variant_count += 1
                    continue
                
                hand_id = self.extract_hand_id(file_path, hand_idx)
                is_showdown = self._is_showdown(hand)
                hole_cards_dict = self._get_hole_cards(hand) if is_showdown else {}
                
                starting_stacks = hand.starting_stacks
                actions_by_street = self._extract_street_actions(hand, hand.players, starting_stacks)
                
                for action_data in actions_by_street:
                    action_data['hand_id'] = hand_id
                    action_data['is_showdown'] = is_showdown
                    player_id = action_data.get('player_id')
                    if is_showdown and player_id in hole_cards_dict:
                        action_data['hole_cards'] = hole_cards_dict[player_id]
                    else:
                        action_data['hole_cards'] = []
                    yield action_data
                self.parsed_count += 1
            except Exception as e:
                logger.error(f"Error parsing hand {hand_idx} in {filename}: {e}")
                continue

    def _is_showdown(self, hand) -> bool:
        for _, action in hand.state_actions:
            if action and (str(action).split()[1].lower() == 'sm' or str(action).split()[1].lower() == 'dh'):
                if '????' not in str(action):
                    return True
        return False

    def _get_hole_cards(self, hand) -> Dict[str, List[str]]:
        hole_cards = {}
        for _, action in hand.state_actions:
            if not action: continue
            parts = str(action).split()
            if len(parts) < 3: continue
            code = parts[1].lower()
            if code in ('dh', 'sm'):
                p_key = parts[2] if code == 'dh' else parts[0]
                c_str = parts[3] if code == 'dh' else parts[2]
                if p_key.startswith('p') and c_str and '?' not in c_str:
                    try:
                        p_idx = int(p_key[1:]) - 1
                        if 0 <= p_idx < len(hand.players):
                            p_name = hand.players[p_idx]
                            hole_cards[p_name] = [c_str[i:i+2] for i in range(0, len(c_str), 2)]
                    except Exception: pass
        return hole_cards

    # Codes that represent a player putting money in voluntarily and for value or
    # as a bluff. PHH spells all three as 'cbr' (complete, bet, or raise); 'cc'
    # is check/call, 'f' is fold, 'sm' is show/muck. Dealer actions ('d dh',
    # 'd db') are excluded structurally, because the actor has to be a 'pN' token.
    AGGRESSIVE_CODES = frozenset({'cbr'})

    @staticmethod
    def _actor_index_from_action(token: str, player_count: int) -> Optional[int]:
        """Resolve the 'p4' in 'p4 cbr 170000' to an index into hand.players.

        The action string is the authority on who acted. See
        _extract_street_actions for why this is not taken from the state.
        """
        if not token.startswith('p'):
            return None
        try:
            index = int(token[1:]) - 1
        except ValueError:
            return None
        return index if 0 <= index < player_count else None

    def _extract_street_actions(self, hand, players, starting_stacks) -> List[Dict[str, Any]]:
        """Pull out every bet and raise, with the pot it was facing.

        pokerkit pairs each action with the state *after* that action has been
        applied, so two things that look available on the state are not:

        `state.actor_index` is whoever is due to act next, not the player who
        made this action. Attributing by it shifted every aggressive action onto
        the following player, and because hole cards are joined back on
        player_id, it also handed each bet the wrong player's cards. In the
        five-handed example hand used by scripts/inspect_dataset.py, four river
        and turn barrels made by a player holding 6d5h on JcTs2dAsQs (a stone
        bluff) were recorded against the player holding Js8h (top pair). The
        showdown labels are derived from exactly that pairing, so the mistake did
        not just add noise, it inverted the thing the model is trying to learn.

        `state.pots` only counts chips already gathered into the pot. Money still
        sitting in front of players lives in `state.bets` until the street
        closes, so on any street with outstanding action - every 3-bet, every
        raise facing a bet - the collected total understates what the aggressor
        was actually pricing against. Reconstructing it needs the bets too,
        minus this action's own contribution, since the state already includes it.
        """
        actions = []
        try:
            for state, action in hand.state_actions:
                if state is None or action is None:
                    continue
                parts = str(action).strip().split()
                if len(parts) < 3:
                    continue
                if parts[1].lower() not in self.AGGRESSIVE_CODES:
                    continue

                actor_index = self._actor_index_from_action(parts[0], len(players))
                if actor_index is None:
                    continue
                if state.street_index is None:
                    continue

                # Parse amount
                bet_amount = 0.0
                for token in reversed(parts[2:]):
                    try:
                        bet_amount = float(token)
                        break
                    except Exception: continue

                if bet_amount <= 0: continue

                collected = sum(p.amount for p in state.pots) if state.pots else 0
                outstanding = sum(state.bets) if getattr(state, 'bets', None) else 0
                # bet_amount is the total this player is in for on this street, and
                # it is already inside `outstanding`, so remove it to get the pot as
                # the player saw it. Clamped because a malformed amount should not
                # produce a negative pot.
                pot_before = max(0.0, float(collected + outstanding) - bet_amount)

                board_cards = [str(card) for card in state.board_cards] if state.board_cards else []

                actions.append({
                    'player_id': players[actor_index],
                    'street': int(state.street_index),
                    'pot_before': pot_before,
                    'bet_amount': float(bet_amount),
                    'board_cards': board_cards,
                    'starting_stack': float(starting_stacks[actor_index]) if actor_index < len(starting_stacks) else 0.0
                })
        except Exception as e:
            logger.error(f"Error extracting street actions: {e}")
        return actions

    def parse_directory(self, directory: str, pattern: str = "*.phh", limit: Optional[int] = None):
        path = Path(directory)
        files = sorted(path.glob(pattern))
        if limit: files = files[:limit]
        for file_path in files:
            yield from self.parse_phh_file(str(file_path))

    def to_dataframe(self, records: List[Dict[str, Any]]) -> pd.DataFrame:
        df = pd.DataFrame(records)
        if not df.empty:
            df['street'] = df['street'].astype('int32')
            df['pot_before'] = df['pot_before'].astype('float64')
            df['bet_amount'] = df['bet_amount'].astype('float64')
        return df

if __name__ == "__main__":
    parser = PHHParser()
    recs = list(parser.parse_phh_file(r"poker-hand-histories\data\handhq\ABS-2009-07-01_2009-07-23_1000NLH_OBFU\10\abs NLH handhq_1-OBFUSCATED.phhs"))
    print(f"Parsed {len(recs)} records")
