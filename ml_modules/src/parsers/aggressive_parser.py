"""
Aggressive Dataset Parser

Parses a large subset (1000 files) of handhq data to provide deep learning data.
"""

import logging
from pathlib import Path
import pandas as pd
import time
import random
import os

# Absolute imports
from src.parsers.data_loader import PHHParser
from src.utils.config_loader import get_data_path, load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AggressiveParser:
    def __init__(self, limit=1000):
        # Use config loader for paths
        raw_base = get_data_path("raw_hand_histories")
        if not raw_base:
            raw_base = "data/raw/poker-hand-histories"
            
        self.data_dir = Path(raw_base) / "data/handhq"
        
        output_path = get_data_path("parsed_aggressive")
        if not output_path:
            output_path = "data/interim/parsed_hands_aggressive.parquet"
            
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.limit = limit
        
    def run(self):
        logger.info(f"Discovering files in {self.data_dir}...")
        if not self.data_dir.exists():
            logger.error(f"Data directory {self.data_dir} does not exist.")
            return None
            
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
            
            if idx % 10 == 0 or idx == len(all_files):
                elapsed = time.time() - start_time
                rate = idx / elapsed
                eta = (len(all_files) - idx) / rate if rate > 0 else 0
                logger.info(f"[{idx}/{len(all_files)}] Total Records: {len(records)} | ETA: {eta:.0f}s")
                
        if not records:
            logger.error("No records parsed.")
            return None
            
        df = pd.DataFrame(records)
        df.to_parquet(self.output_path)
        logger.info(f"Saved {len(df)} records to {self.output_path}")
        
        return df

def run_ingestion(limit=1000):
    """Entry point for the pipeline."""
    parser = AggressiveParser(limit=limit)
    return parser.run()

if __name__ == "__main__":
    # For standalone testing
    run_ingestion(limit=50)
