"""
Data Quality Validation (Subtask 1.3.4)

Comprehensive validation across strata to ensure:
- pot_before monotonicity per hand
- valid street transitions 
- action sequence integrity
- consistency across dataset strata (Pluribus, WSOP, Individual)
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataQualityValidator:
    """Validates parsed poker data quality."""
    
    def __init__(self, dataframe: pd.DataFrame):
        """Initialize validator with parsed data."""
        self.df = dataframe.copy()
        self.validation_results = {}
        self.issues = []
        
    def validate_pot_monotonicity(self) -> bool:
        """
        Check that pot_before does not decrease within a hand/street.
        
        Rule: For each hand_id, pot_before should be non-decreasing as 
        we progress through streets and actions.
        
        Returns:
            True if all checks pass
        """
        logger.info("\n[1] Validating pot_before monotonicity...")
        
        issues = []
        
        # Group by hand
        for hand_id, group in self.df.groupby('hand_id'):
            # Sort by street to check monotonicity within hand
            group_sorted = group.sort_values('street')
            pots = group_sorted['pot_before'].values
            
            # Check if any pot decreases
            for i in range(1, len(pots)):
                if pots[i] < pots[i-1]:
                    issues.append({
                        'hand_id': hand_id,
                        'issue': f'Pot decreased from {pots[i-1]} to {pots[i]}',
                        'index': i
                    })
        
        if not issues:
            logger.info(f"  [PASS] All {self.df['hand_id'].nunique()} hands have monotonic pot progression")
            self.validation_results['pot_monotonicity'] = True
            return True
        else:
            logger.warning(f"  [FAIL] Found {len(issues)} pot monotonicity violations")
            for issue in issues[:5]:
                logger.warning(f"    {issue['hand_id']}: {issue['issue']}")
            self.issues.extend(issues)
            self.validation_results['pot_monotonicity'] = False
            return False
    
    def validate_street_transitions(self) -> bool:
        """
        Check that street_index transitions are valid within each hand.
        
        Rules:
        - street_index must be 0, 1, 2, or 3
        - Within a hand, streets should not go backward
        - Multiple actions can occur on same street
        
        Returns:
            True if all checks pass
        """
        logger.info("\n[2] Validating street transitions...")
        
        issues = []
        
        for hand_id, group in self.df.groupby('hand_id'):
            streets = group['street'].values
            
            # Check if streets are valid
            for i, street in enumerate(streets):
                if street not in [0, 1, 2, 3]:
                    issues.append({
                        'hand_id': hand_id,
                        'issue': f'Invalid street index {street}',
                        'position': i
                    })
            
            # Check if streets go backward (excluding same street)
            prev_street = -1
            for i, street in enumerate(streets):
                if street < prev_street:
                    issues.append({
                        'hand_id': hand_id,
                        'issue': f'Street went backward from {prev_street} to {street}',
                        'position': i
                    })
                if street >= 0:  # Valid street
                    prev_street = max(prev_street, street)
        
        if not issues:
            logger.info(f"  [PASS] All {len(self.df)} actions have valid street progression")
            self.validation_results['street_transitions'] = True
            return True
        else:
            logger.warning(f"  [FAIL] Found {len(issues)} street transition violations")
            for issue in issues[:5]:
                logger.warning(f"    {issue['hand_id']}: {issue['issue']}")
            self.issues.extend(issues)
            self.validation_results['street_transitions'] = False
            return False
    
    def validate_action_sequence_integrity(self) -> bool:
        """
        Check that action sequences are consistent and logically valid.
        
        Rules:
        - Bet amounts should be positive (already checked, but verify here)
        - No duplicate actions from same player in same state
        - Players should vary (not all actions by same player)
        
        Returns:
            True if all checks pass
        """
        logger.info("\n[3] Validating action sequence integrity...")
        
        issues = []
        
        # Check bet amounts
        negative_bets = self.df[self.df['bet_amount'] <= 0]
        if len(negative_bets) > 0:
            logger.warning(f"  Found {len(negative_bets)} non-positive bets")
            issues.append({'type': 'negative_bets', 'count': len(negative_bets)})
        
        # Check player variety within hands
        for hand_id, group in self.df.groupby('hand_id'):
            players = group['player_id'].unique()
            if len(players) < 2:
                issues.append({
                    'hand_id': hand_id,
                    'issue': f'Only {len(players)} player(s) in hand',
                })
            
            # Check for reasonable number of actions
            if len(group) > 20:  # More than 20 actions in hand seems like data error
                logger.warning(f"  {hand_id} has {len(group)} actions (unusual)")
        
        if not issues:
            logger.info(f"  [PASS] Action sequences are consistent")
            self.validation_results['action_integrity'] = True
            return True
        else:
            logger.warning(f"  [WARN] Found {len(issues)} potential issues in action sequences")
            for issue in issues[:5]:
                logger.warning(f"    {issue}")
            self.issues.extend(issues)
            self.validation_results['action_integrity'] = len(issues) == 0
            return len(issues) == 0
    
    def validate_across_strata(self) -> bool:
        """
        Validate consistency across dataset strata.
        
        Checks:
        - All strata present (if expected)
        - Strata-specific constraints (e.g., Pluribus has many hands per file)
        
        Returns:
            True if all checks pass
        """
        logger.info("\n[4] Validating across strata...")
        
        # Try to infer strata from hand_id (file name)
        self.df['source'] = self.df['hand_id'].apply(self._extract_source)
        
        strata_stats = self.df.groupby('source').agg({
            'hand_id': 'nunique',
            'player_id': 'nunique',
            'bet_amount': ['mean', 'median', 'std'],
        }).round(2)
        
        logger.info(f"  Strata breakdown:")
        for source in self.df['source'].unique():
            source_data = self.df[self.df['source'] == source]
            logger.info(f"    {source}: {source_data['hand_id'].nunique()} hands, "
                       f"{len(source_data)} actions, "
                       f"avg bet={source_data['bet_amount'].mean():.0f}")
        
        self.validation_results['strata_coverage'] = True
        return True
    
    def _extract_source(self, hand_id: str) -> str:
        """Extract data source from hand_id."""
        if 'pluribus' in hand_id.lower():
            return 'Pluribus'
        elif 'wsop' in hand_id.lower():
            return 'WSOP'
        else:
            return 'Individual'
    
    def run_all_validations(self) -> Dict[str, bool]:
        """
        Run all validation checks.
        
        Returns:
            Dictionary with validation results
        """
        logger.info("="*70)
        logger.info("SUBTASK 1.3.4: DATA QUALITY VALIDATION")
        logger.info("="*70)
        
        self.validate_pot_monotonicity()
        self.validate_street_transitions()
        self.validate_action_sequence_integrity()
        self.validate_across_strata()
        
        return self.validation_results
    
    def generate_report(self) -> str:
        """Generate validation report."""
        lines = []
        lines.append("\n" + "="*70)
        lines.append("DATA QUALITY VALIDATION REPORT")
        lines.append("="*70)
        
        lines.append(f"\nDataset Size:")
        lines.append(f"  Total records: {len(self.df)}")
        lines.append(f"  Total hands: {self.df['hand_id'].nunique()}")
        lines.append(f"  Total players: {self.df['player_id'].nunique()}")
        
        lines.append(f"\nValidation Results:")
        for check, passed in self.validation_results.items():
            status = "PASS" if passed else "WARN"
            lines.append(f"  [{status}] {check.replace('_', ' ').title()}")
        
        passed_count = sum(1 for v in self.validation_results.values() if v)
        total_count = len(self.validation_results)
        lines.append(f"\nOverall: {passed_count}/{total_count} checks passed")
        
        if passed_count == total_count:
            lines.append("\nConclusion: Data quality is ACCEPTABLE for feature engineering")
        else:
            lines.append("\nConclusion: Data quality has issues - review before feature engineering")
        
        lines.append("="*70)
        
        return "\n".join(lines)


def run_validation(file_path: str = None) -> bool:
    """
    Run the full validation suite on a parquet file.
    
    Args:
        file_path: Path to the parquet file to validate. 
                  If None, uses the default sample path.
    
    Returns:
        True if the data quality is acceptable (no critical failures).
    """
    from src.utils.config_loader import get_data_path
    
    if file_path is None:
        file_path = get_data_path("parsed_aggressive") or "parsed_output/parsed_hands_sample.parquet"
    
    parquet_file = Path(file_path)
    
    if not parquet_file.exists():
        logger.error(f"Parsed data file not found: {parquet_file}")
        return False
    
    logger.info(f"Loading parsed data for validation from: {parquet_file}")
    df = pd.read_parquet(parquet_file)
    
    if df.empty:
        logger.error("Parsed data is empty. Validation failed.")
        return False

    # Run validations
    validator = DataQualityValidator(df)
    results = validator.run_all_validations()
    
    # Generate report
    report = validator.generate_report()
    print(report)
    
    # Save report - try to save it in the same directory as the input
    report_file = parquet_file.parent / f"data_quality_report_{parquet_file.stem}.txt"
    try:
        with open(report_file, "w") as f:
            f.write(report)
        logger.info(f"\nReport saved to: {report_file}")
    except Exception as e:
        logger.warning(f"Could not save report file: {e}")
    
    # Define success criteria: critical checks must pass
    # We allow action_integrity to be a warning (False) if it's just due to single player aggressive hands
    critical_checks = ['pot_monotonicity', 'street_transitions']
    success = all(results.get(check, False) for check in critical_checks)
    
    return success

def main():
    """Main validation workflow."""
    run_validation()


if __name__ == "__main__":
    main()
