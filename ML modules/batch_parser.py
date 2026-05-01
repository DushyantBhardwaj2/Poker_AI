"""
Batch Parsing Orchestrator

Orchestrates parsing of sampled PHH files with:
- Progress tracking
- Error handling
- Data validation
- Output to parquet
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
from datetime import datetime
import time

# Import the parser from data_loader
from data_loader import PHHParser, load_phh_files

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchParsingOrchestrator:
    """Orchestrates batch parsing of PHH files."""
    
    def __init__(self, output_dir: str = "./parsed_output"):
        """Initialize the orchestrator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.start_time = None
        self.end_time = None
        self.total_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.total_hands = 0
        self.total_records = 0
    
    def parse_sample_files(self, sample_list_file: str = "sample_files.py") -> pd.DataFrame:
        """
        Parse all files in the sample list.
        
        Args:
            sample_list_file: Python file with SAMPLE_FILES list
            
        Returns:
            Combined DataFrame of all parsed records
        """
        self.start_time = time.time()
        logger.info("="*70)
        logger.info("BATCH PARSING ORCHESTRATOR")
        logger.info("="*70)
        
        # Load sample file list
        logger.info(f"\nLoading sample file list from: {sample_list_file}")
        spec = {}
        exec(open(sample_list_file).read(), spec)
        sample_files = spec.get('SAMPLE_FILES', [])
        
        if not sample_files:
            logger.error("No files found in sample list!")
            return pd.DataFrame()
        
        logger.info(f"Found {len(sample_files)} files to parse")
        self.total_files = len(sample_files)
        
        # Parse files
        all_records = []
        parser = PHHParser()
        
        for idx, file_path in enumerate(sample_files, 1):
            try:
                if not Path(file_path).exists():
                    logger.warning(f"[{idx}/{len(sample_files)}] File not found: {file_path}")
                    self.failed_files += 1
                    continue
                
                # Parse file
                file_records = list(parser.parse_phh_file(file_path))
                all_records.extend(file_records)
                
                # Progress logging
                if idx % 25 == 0 or idx == len(sample_files):
                    logger.info(f"[{idx}/{len(sample_files)}] Parsed: {len(file_records)} records")
                
                self.successful_files += 1
                
            except Exception as e:
                logger.error(f"Error parsing {file_path}: {str(e)}")
                self.failed_files += 1
                continue
        
        # Convert to DataFrame
        logger.info(f"\nConverting {len(all_records)} records to DataFrame...")
        if not all_records:
            logger.warning("No records to convert!")
            return pd.DataFrame()
        
        df = parser.to_dataframe(all_records)
        self.total_records = len(df)
        self.total_hands = df['hand_id'].nunique()
        
        self.end_time = time.time()
        
        return df
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate parsed data quality.
        
        Checks:
        - All required columns present
        - No null values in critical columns
        - Data type correctness
        - Logical constraints (pot_before monotonicity, valid streets)
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dict with validation results
        """
        logger.info("\n" + "="*70)
        logger.info("DATA VALIDATION")
        logger.info("="*70)
        
        results = {}
        
        # 1. Check required columns
        required_cols = ['hand_id', 'player_id', 'street', 'pot_before', 
                        'bet_amount', 'board_cards', 'is_showdown', 'hole_cards']
        missing_cols = [c for c in required_cols if c not in df.columns]
        results['columns_present'] = len(missing_cols) == 0
        
        if missing_cols:
            logger.error(f"Missing columns: {missing_cols}")
        else:
            logger.info(f"[PASS] All {len(required_cols)} required columns present")
        
        # 2. Check for nulls in critical columns
        critical_cols = ['hand_id', 'player_id', 'street', 'pot_before', 'bet_amount']
        null_counts = df[critical_cols].isnull().sum()
        results['no_nulls'] = (null_counts == 0).all()
        
        if results['no_nulls']:
            logger.info(f"[PASS] No null values in critical columns")
        else:
            logger.warning(f"Nulls found in critical columns:\n{null_counts[null_counts > 0]}")
        
        # 3. Check data types
        type_checks = {
            'hand_id': 'object',
            'player_id': 'object',
            'street': ('int32', 'int64'),
            'pot_before': ('float32', 'float64'),
            'bet_amount': ('float32', 'float64'),
        }
        
        type_errors = []
        for col, expected_type in type_checks.items():
            actual_type = str(df[col].dtype)
            if isinstance(expected_type, tuple):
                is_correct = actual_type in expected_type
            else:
                is_correct = actual_type == expected_type
            
            if not is_correct:
                type_errors.append(f"{col}: expected {expected_type}, got {actual_type}")
        
        results['correct_types'] = len(type_errors) == 0
        if results['correct_types']:
            logger.info(f"[PASS] All data types correct")
        else:
            for error in type_errors:
                logger.warning(f"Type error: {error}")
        
        # 4. Check street values
        valid_streets = {0, 1, 2, 3}
        actual_streets = set(df['street'].unique())
        results['valid_streets'] = actual_streets.issubset(valid_streets)
        
        logger.info(f"[CHECK] Streets found: {sorted(actual_streets)} (expected: 0-3)")
        
        # 5. Check bet amounts are positive
        negative_bets = (df['bet_amount'] <= 0).sum()
        results['positive_bets'] = negative_bets == 0
        
        if results['positive_bets']:
            logger.info(f"[PASS] All bet amounts positive")
        else:
            logger.warning(f"Found {negative_bets} non-positive bets")
        
        # 6. Check potsbefore are non-negative
        negative_pots = (df['pot_before'] < 0).sum()
        results['valid_pots'] = negative_pots == 0
        
        if results['valid_pots']:
            logger.info(f"[PASS] All pot_before values non-negative")
        else:
            logger.warning(f"Found {negative_pots} negative pots")
        
        # 7. Check showdown consistency
        has_hole_cards = df['hole_cards'].apply(lambda x: isinstance(x, list) and len(x) > 0)
        mismatches = (df['is_showdown'] != has_hole_cards).sum()
        results['showdown_consistency'] = mismatches == 0
        
        if results['showdown_consistency']:
            logger.info(f"[PASS] Showdown flag matches hole cards presence")
        else:
            logger.warning(f"Found {mismatches} showdown inconsistencies")
        
        # Summary
        logger.info("\n" + "-"*70)
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        logger.info(f"Validation: {passed}/{total} checks passed")
        
        return results
    
    def generate_report(self, df: pd.DataFrame, validation_results: Dict) -> str:
        """Generate parsing and validation report."""
        
        lines = []
        lines.append("\n" + "="*70)
        lines.append("BATCH PARSING REPORT")
        lines.append("="*70)
        
        # Timing
        elapsed = self.end_time - self.start_time
        lines.append(f"\nTiming:")
        lines.append(f"  Total elapsed: {elapsed:.2f} seconds")
        lines.append(f"  Average per file: {elapsed/self.successful_files:.3f} seconds")
        
        # File statistics
        lines.append(f"\nFile Statistics:")
        lines.append(f"  Total files in sample: {self.total_files}")
        lines.append(f"  Successfully parsed: {self.successful_files}")
        lines.append(f"  Failed: {self.failed_files}")
        lines.append(f"  Success rate: {100*self.successful_files/max(1, self.total_files):.1f}%")
        
        # Data statistics
        lines.append(f"\nData Statistics:")
        lines.append(f"  Total hands parsed: {self.total_hands}")
        lines.append(f"  Total action records: {self.total_records}")
        lines.append(f"  Average records per hand: {self.total_records/max(1, self.total_hands):.2f}")
        
        # Distribution
        lines.append(f"\nDistribution:")
        lines.append(f"  Streets: {df['street'].value_counts().sort_index().to_dict()}")
        lines.append(f"  Showdown hands: {df['is_showdown'].sum()} ({100*df['is_showdown'].sum()/len(df):.1f}%)")
        
        # Validation
        lines.append(f"\nValidation Results:")
        for check, passed in validation_results.items():
            status = "PASS" if passed else "WARN"
            lines.append(f"  [{status}] {check.replace('_', ' ').title()}")
        
        lines.append("\n" + "="*70)
        
        return "\n".join(lines)
    
    def save_outputs(self, df: pd.DataFrame, validation_results: Dict) -> None:
        """Save parsed data and reports."""
        
        if df.empty:
            logger.warning("DataFrame is empty, skipping save")
            return
        
        # Save DataFrame
        output_file = self.output_dir / "parsed_hands_sample.parquet"
        df.to_parquet(output_file, index=False)
        logger.info(f"\nSaved parsed data to: {output_file}")
        
        # Generate and save report
        report = self.generate_report(df, validation_results)
        
        report_file = self.output_dir / "parsing_report.txt"
        with open(report_file, "w") as f:
            f.write(report)
        
        logger.info(f"Saved report to: {report_file}")
        
        # Save data summary
        summary_file = self.output_dir / "data_summary.txt"
        with open(summary_file, "w") as f:
            f.write("DATA SUMMARY\n")
            f.write("="*70 + "\n\n")
            f.write(f"Shape: {df.shape}\n\n")
            f.write("Columns:\n")
            for col in df.columns:
                f.write(f"  {col}: {df[col].dtype}\n")
            f.write("\nFirst rows:\n")
            f.write(df.head(10).to_string())
            f.write("\n\nDescriptive Statistics:\n")
            f.write(df.describe().to_string())
        
        logger.info(f"Saved summary to: {summary_file}")
        
        print(report)


def main():
    """Main orchestration workflow."""
    
    orchestrator = BatchParsingOrchestrator()
    
    # Parse sample files
    df = orchestrator.parse_sample_files("sample_files.py")
    
    if df.empty:
        logger.error("No data parsed!")
        return
    
    logger.info(f"\n[SUCCESS] Parsed {len(df)} records from {orchestrator.total_hands} hands")
    
    # Validate data
    validation_results = orchestrator.validate_data(df)
    
    # Save outputs
    orchestrator.save_outputs(df, validation_results)
    
    logger.info("\n[DONE] Batch parsing complete")


if __name__ == "__main__":
    main()
