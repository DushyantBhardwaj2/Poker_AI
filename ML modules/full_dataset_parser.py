"""
Full Dataset Parsing Orchestrator

Parses all PHH files under `poker-hand-histories/` using the existing `PHHParser` from `data_loader.py`.
Outputs:
 - parsed_output/parsed_hands_full.parquet
 - parsed_output/parsing_report_full.txt
 - parsed_output/data_summary_full.txt

Run as: python full_dataset_parser.py
"""

import logging
from pathlib import Path
import pandas as pd
import time
from data_loader import PHHParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FullDatasetParsingOrchestrator:
    def __init__(self, data_dir: str = "./poker-hand-histories", output_dir: str = "./parsed_output"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.start_time = None
        self.end_time = None
        self.total_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.total_hands = 0
        self.total_records = 0
        self.failed_files_list = []

    def discover_all_files(self):
        logger.info(f"Scanning for .phh and .phhs files under: {self.data_dir}")
        phh_files = sorted(list(self.data_dir.rglob("*.phh")) + list(self.data_dir.rglob("*.phhs")))
        logger.info(f"Found {len(phh_files)} files")
        return phh_files

    def parse_all_files(self):
        self.start_time = time.time()
        logger.info("=" * 60)
        logger.info("FULL DATASET PARSING")
        logger.info("=" * 60)

        all_files = self.discover_all_files()
        if not all_files:
            logger.error("No PHH files found; aborting.")
            return pd.DataFrame()

        self.total_files = len(all_files)
        parser = PHHParser()
        records = []
        hands_seen = set()

        for idx, p in enumerate(all_files, 1):
            try:
                file_recs = list(parser.parse_phh_file(str(p)))
                if file_recs:
                    records.extend(file_recs)
                    for r in file_recs:
                        hands_seen.add(r.get('hand_id'))
                self.successful_files += 1
            except Exception as e:
                logger.warning(f"Error parsing {p.name}: {e}")
                self.failed_files += 1
                self.failed_files_list.append(str(p))

            if idx % 500 == 0 or idx == self.total_files:
                elapsed = time.time() - self.start_time
                rate = idx / elapsed if elapsed > 0 else 0
                remaining = (self.total_files - idx) / rate if rate > 0 else 0
                logger.info(f"[{idx}/{self.total_files}] Records: {len(records)} | Hands: {len(hands_seen)} | ETA: {remaining:.0f}s")

        if not records:
            logger.error("No records parsed from full dataset")
            return pd.DataFrame()

        df = pd.DataFrame(records)
        self.total_records = len(df)
        self.total_hands = len(hands_seen)
        logger.info(f"Parsing complete: {self.total_records} records from {self.total_hands} hands")
        return df

    def save_outputs(self, df: pd.DataFrame):
        parquet_file = self.output_dir / "parsed_hands_full.parquet"
        df.to_parquet(parquet_file)
        logger.info(f"Saved parquet: {parquet_file}")

        # report
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time if self.start_time else 0
        report_lines = []
        report_lines.append("FULL DATASET PARSING REPORT")
        report_lines.append(f"Execution time: {elapsed:.1f}s")
        report_lines.append(f"Files discovered: {self.total_files}")
        report_lines.append(f"Successfully parsed: {self.successful_files}")
        report_lines.append(f"Failed files: {self.failed_files}")
        report_lines.append(f"Total records: {self.total_records}")
        report_lines.append(f"Total hands: {self.total_hands}")

        report_file = self.output_dir / "parsing_report_full.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        logger.info(f"Saved report: {report_file}")

        summary_file = self.output_dir / "data_summary_full.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"Total records: {self.total_records}\nTotal hands: {self.total_hands}\n")
        logger.info(f"Saved summary: {summary_file}")


def main():
    orch = FullDatasetParsingOrchestrator()
    df = orch.parse_all_files()
    if df.empty:
        logger.error("No data parsed; exiting")
        return
    orch.save_outputs(df)
    logger.info("Full dataset parsing finished.")


if __name__ == '__main__':
    main()
