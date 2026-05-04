import pandas as pd
from pathlib import Path
import pokerkit
import logging
import time
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PlayerStatCollector:
    def __init__(self, data_dir: str = "./poker-hand-histories"):
        self.data_dir = Path(data_dir)
        self.stats = defaultdict(lambda: {"hands": 0, "vpip_count": 0, "pfr_count": 0})

    def process_all_files(self):
        phh_files = sorted(self.data_dir.rglob("*.phh"))
        total_files = len(phh_files)
        logger.info(f"Found {total_files} files to process for stats")
        
        start_time = time.time()
        for idx, p in enumerate(phh_files, 1):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    content = f.read()
                hand_histories = pokerkit.HandHistory.loads(content)
                if not isinstance(hand_histories, list):
                    hand_histories = [hand_histories]
                
                for hand in hand_histories:
                    if hand.variant != "NT": # NLHE only
                        continue
                    self._process_hand(hand)
            except Exception as e:
                logger.debug(f"Error processing {p.name}: {e}")

            if idx % 1000 == 0 or idx == total_files:
                elapsed = time.time() - start_time
                logger.info(f"[{idx}/{total_files}] Processed {len(self.stats)} players | {elapsed:.1f}s")

    def _process_hand(self, hand):
        players = hand.players
        vpip_players = set()
        pfr_players = set()
        
        # Track who is in the hand
        for p in players:
            self.stats[p]["hands"] += 1
            
        # Analyze pre-flop actions
        # street_index 0 is pre-flop
        for state, action in hand.state_actions:
            if state is None or state.street_index != 0:
                continue
            
            if action is None or not isinstance(action, str):
                continue
                
            parts = action.split()
            if len(parts) < 2:
                continue
                
            # parts look like: ['p1', 'f'], ['p2', 'cc'], ['p3', 'cbr', '100']
            actor_key = parts[0]
            if not actor_key.startswith('p'):
                continue
                
            try:
                actor_idx = int(actor_key[1:]) - 1
                if actor_idx < 0 or actor_idx >= len(players):
                    continue
                player_name = players[actor_idx]
            except:
                continue
                
            action_code = parts[1].lower()
            
            # VPIP: Voluntarily put money in (Call, Bet, Raise)
            # cc = call, cbr = call/bet/raise
            if action_code in {'cc', 'cbr'} or 'b' in action_code or 'r' in action_code:
                vpip_players.add(player_name)
                
            # PFR: Pre-flop raise
            if 'r' in action_code or (action_code == 'cbr' and len(parts) > 2):
                # Note: 'cbr' can be a raise. In PHH, 'cbr' is generic for aggressive actions.
                # If it's the first aggressive action beyond the big blind, it's a raise.
                pfr_players.add(player_name)
        
        for p in vpip_players:
            self.stats[p]["vpip_count"] += 1
        for p in pfr_players:
            self.stats[p]["pfr_count"] += 1

    def save_stats(self, output_path: str = "parsed_output/player_stats.parquet"):
        data = []
        for p, s in self.stats.items():
            if s["hands"] > 0:
                data.append({
                    "player_id": p,
                    "hands_played": s["hands"],
                    "vpip": s["vpip_count"] / s["hands"],
                    "pfr": s["pfr_count"] / s["hands"]
                })
        
        df = pd.DataFrame(data)
        df.to_parquet(output_path)
        logger.info(f"Saved stats for {len(df)} players to {output_path}")
        return df

if __name__ == "__main__":
    collector = PlayerStatCollector()
    collector.process_all_files()
    collector.save_stats()
