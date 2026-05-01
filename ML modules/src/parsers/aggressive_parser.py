"""
Aggressive Dataset Parser

Parses a large subset (1000 files) of handhq data to provide deep learning data.
"""

import logging
from pathlib import Path
import pandas as pd
import time
from data_loader import PHHParser
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AggressiveParser:
    def __init__(self, limit=1000):
        self.data_dir = Path("./poker-hand-histories/data/handhq")
        self.output_dir = Path("./parsed_output")
        self.output_dir.mkdir(exist_ok=True)
        self.limit = limit
        
    def run(self):
        logger.info(f"Discovering files in {self.data_dir}...")
        all_files = list(self.data_dir.rglob("*.phhs"))
        logger.info(f"Found {len(all_files)} files.")
        
        if len(all_files) > self.limit:
            logger.info(f"Sampling {self.limit} files...")
            random.seed(42)
            all_files = random.sample(all_files, self.limit)
            
        parser = PHHParser()
        records = []
        start_time = time.time()
        
        for idx, p in enumerate(all_files, 1):
            try:
                file_recs = list(parser.parse_phh_file(str(p)))
                if file_recs:
                    records.extend(file_recs)
            except Exception as e:
                logger.warning(f"Error parsing {p.name}: {e}")
            
            if idx % 50 == 0 or idx == len(all_files):
                elapsed = time.time() - start_time
                rate = idx / elapsed
                eta = (len(all_files) - idx) / rate
                logger.info(f"[{idx}/{len(all_files)}] Total Records: {len(records)} | ETA: {eta:.0f}s")
                
        if not records:
            logger.error("No records parsed.")
            return
            
        df = pd.DataFrame(records)
        output_path = self.output_dir / "parsed_hands_aggressive.parquet"
        df.to_parquet(output_path)
        logger.info(f"Saved {len(df)} records to {output_path}")
        
        # Also need to update player stats for these players
        return df

if __name__ == "__main__":
    ap = AggressiveParser(limit=50) # Increasing depth for better precision
    ap.run()
