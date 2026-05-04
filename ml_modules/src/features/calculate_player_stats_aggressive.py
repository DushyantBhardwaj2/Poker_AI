"""
Aggressive Player Stat Collector
Processes a large number of handhq files to get robust VPIP/PFR stats.
"""

import pandas as pd
from pathlib import Path
import pokerkit
import logging
import time
from collections import defaultdict
import random
import re
import os

# Absolute imports
from src.utils.config_loader import get_data_path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AggressiveStatCollector:
    def __init__(self, limit=2000):
        # Use config loader for paths
        raw_base = get_data_path("raw_hand_histories")
        if not raw_base:
            raw_base = "data/raw/poker-hand-histories"
            
        self.data_dir = Path(raw_base) / "data/handhq"
        
        output_path = get_data_path("player_stats_aggressive")
        if not output_path:
            output_path = "data/interim/player_stats_aggressive.parquet"
            
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.limit = limit
        self.stats = defaultdict(lambda: {"hands": 0, "vpip_count": 0, "pfr_count": 0})

    def process_files(self):
        logger.info(f"Scanning for .phhs files in {self.data_dir}...")
        if not self.data_dir.exists():
            logger.error(f"Data directory {self.data_dir} does not exist.")
            return None
            
        all_files = list(self.data_dir.rglob("*.phhs"))
        logger.info(f"Found {len(all_files)} files.")
        
        if len(all_files) > self.limit:
            random.seed(42)
            all_files = random.sample(all_files, self.limit)
            
        total_files = len(all_files)
        logger.info(f"Processing {total_files} files for stats")
        
        start_time = time.time()
        for idx, p in enumerate(all_files, 1):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Fast split for .phhs
                if re.search(r'^\[\d+\]', content, re.MULTILINE):
                    hand_contents = re.split(r'^\[\d+\]', content, flags=re.MULTILINE)
                    hand_contents = [h.strip() for h in hand_contents if h.strip()]
                else:
                    hand_contents = [content]

                for hand_text in hand_contents:
                    try:
                        hand = pokerkit.HandHistory.loads(hand_text)
                        if hand.variant != "NT": continue
                        self._process_hand(hand)
                    except: continue
                    
            except Exception as e:
                logger.debug(f"Error processing {p.name}: {e}")

            if idx % 100 == 0 or idx == total_files:
                elapsed = time.time() - start_time
                rate = idx / elapsed
                eta = (total_files - idx) / rate if rate > 0 else 0
                logger.info(f"[{idx}/{total_files}] Players: {len(self.stats)} | ETA: {eta:.0f}s")

    def _process_hand(self, hand):
        players = hand.players
        vpip_players = set()
        pfr_players = set()
        
        for p in players:
            self.stats[p]["hands"] += 1
            
        for state, action in hand.state_actions:
            if state is None or state.street_index != 0: continue
            action_str = str(action).strip()
            parts = action_str.split()
            if len(parts) < 2: continue
            
            # actor key is the first part usually 'p1', 'p2', etc.
            actor_key = parts[0]
            if not actor_key.startswith('p'): continue
            
            try:
                actor_idx = int(actor_key[1:]) - 1
                if 0 <= actor_idx < len(players):
                    p_name = players[actor_idx]
                    code = parts[1].lower()
                    if 'b' in code or 'r' in code or 'cc' in code or 'cbr' in code:
                        vpip_players.add(p_name)
                    if 'r' in code or (code == 'cbr' and len(parts) > 2):
                        pfr_players.add(p_name)
            except: pass
        
        for p in vpip_players:
            self.stats[p]["vpip_count"] += 1
        for p in pfr_players:
            self.stats[p]["pfr_count"] += 1

    def save_stats(self):
        data = []
        for p, s in self.stats.items():
            if s["hands"] >= 5: # Minimum 5 hands for a profile
                data.append({
                    "player_id": p,
                    "hands_played": s["hands"],
                    "vpip": s["vpip_count"] / s["hands"],
                    "pfr": s["pfr_count"] / s["hands"]
                })
        
        if not data:
            logger.warning("No player stats collected (with >= 5 hands).")
            return None
            
        df = pd.DataFrame(data)
        df.to_parquet(self.output_path)
        logger.info(f"Saved stats for {len(df)} players to {self.output_path}")
        return df

def run_profiling(limit=2000):
    """Entry point for the pipeline."""
    collector = AggressiveStatCollector(limit=limit)
    collector.process_files()
    return collector.save_stats()

if __name__ == "__main__":
    # For standalone testing
    run_profiling(limit=50)
