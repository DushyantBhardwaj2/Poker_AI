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
            except:
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
                    except: pass
        return hole_cards

    def _extract_street_actions(self, hand, players, starting_stacks) -> List[Dict[str, Any]]:
        actions = []
        try:
            for _, (state, action) in enumerate(hand.state_actions):
                if state is None or state.actor_index is None or action is None:
                    continue
                action_str = str(action).strip()
                parts = action_str.split()
                if len(parts) < 2: continue
                code = parts[1].lower()
                if not ('b' in code or 'r' in code): continue
                
                actor_index = state.actor_index
                street_index = state.street_index
                current_pot = sum(p.amount for p in state.pots) if state.pots else 0
                board_cards = [str(card) for card in state.board_cards] if state.board_cards else []
                
                # Parse amount
                bet_amount = 0.0
                for token in reversed(parts[2:]):
                    try:
                        bet_amount = float(token)
                        break
                    except: continue
                
                if bet_amount <= 0: continue
                
                actions.append({
                    'player_id': players[actor_index],
                    'street': int(street_index),
                    'pot_before': float(current_pot),
                    'bet_amount': float(bet_amount),
                    'board_cards': board_cards,
                    'starting_stack': float(starting_stacks[actor_index]) if actor_index < len(starting_stacks) else 0.0
                })
        except: pass
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
