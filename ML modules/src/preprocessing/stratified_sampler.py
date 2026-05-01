"""
Stratified Sampling for Batch Parsing

Creates a stratified 1-5% sample of PHH files across:
- Dataset source (ACPC, WSOP, HandHQ, Pluribus, Individual)
- Stakes levels
- Other relevant attributes
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import random

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StratifiedSampler:
    """Creates stratified samples of PHH files."""
    
    def __init__(self, random_seed: int = 42):
        """Initialize the sampler."""
        random.seed(random_seed)
        self.all_files: List[Path] = []
        self.files_by_source: Dict[str, List[Path]] = defaultdict(list)
        self.files_by_stakes: Dict[str, List[Path]] = defaultdict(list)
        self.file_metadata: Dict[str, Dict] = {}
        
    def extract_source(self, file_path: Path) -> str:
        """Extract dataset source from file path."""
        path_str = str(file_path).lower()
        
        if "annual-computer-poker-competition" in path_str or "acpc" in path_str:
            return "ACPC"
        elif "handhq" in path_str:
            return "HandHQ"
        elif "pluribus" in path_str:
            return "Pluribus"
        elif "wsop" in path_str:
            return "WSOP"
        else:
            return "Individual"
    
    def extract_stakes(self, file_path: Path) -> str:
        """
        Extract stakes level from file path or name.
        
        Examples:
        - ABS-2009-07-01_2009-07-23_1000NLH_OBFU -> "1000"
        - PS-2009-07-01_2009-07-23_50NLH_OBFU -> "50"
        - 0.phh -> "Unknown"
        """
        filename = file_path.stem
        
        # Try to match stake patterns like "50NLH", "100NLH", "1000NLH"
        match = re.search(r'(\d+)NLH', filename)
        if match:
            return f"${match.group(1)}"
        
        # Try to match other patterns
        match = re.search(r'_(\d+)_', str(file_path))
        if match:
            return f"${match.group(1)}"
        
        return "Unknown"
    
    def scan_directory(self, root_dir: str) -> None:
        """
        Recursively scan directory and collect all PHH files.
        
        Args:
            root_dir: Root directory to scan
        """
        root = Path(root_dir)
        
        phh_files = list(root.rglob("*.phh"))
        logger.info(f"Found {len(phh_files)} total PHH files")
        
        for file_path in phh_files:
            self.all_files.append(file_path)
            
            source = self.extract_source(file_path)
            stakes = self.extract_stakes(file_path)
            
            self.files_by_source[source].append(file_path)
            self.files_by_stakes[stakes].append(file_path)
            
            self.file_metadata[str(file_path)] = {
                'source': source,
                'stakes': stakes,
                'path': file_path,
            }
        
        # Log distribution
        logger.info("\nFile Distribution by Source:")
        for source in sorted(self.files_by_source.keys()):
            count = len(self.files_by_source[source])
            logger.info(f"  {source}: {count} files")
        
        logger.info("\nFile Distribution by Stakes:")
        for stakes in sorted(self.files_by_stakes.keys()):
            count = len(self.files_by_stakes[stakes])
            logger.info(f"  {stakes}: {count} files")
    
    def stratified_sample(self, percentage: float = 2.0) -> List[Path]:
        """
        Create a stratified random sample.
        
        Samples `percentage` of files while maintaining proportions across:
        - Sources
        - Stakes levels
        
        Args:
            percentage: Percentage of files to sample (1-5 recommended)
            
        Returns:
            List of sampled file paths
        """
        if not self.all_files:
            logger.warning("No files scanned. Call scan_directory first.")
            return []
        
        total_count = len(self.all_files)
        sample_size = max(1, int(total_count * percentage / 100))
        
        logger.info(f"\nStratified Sampling")
        logger.info(f"  Total files: {total_count}")
        logger.info(f"  Sample percentage: {percentage}%")
        logger.info(f"  Target sample size: {sample_size} files")
        
        sampled = []
        
        # Sample from each source proportionally
        logger.info("\n  Sampling by source:")
        for source in sorted(self.files_by_source.keys()):
            source_files = self.files_by_source[source]
            source_count = len(source_files)
            source_proportion = source_count / total_count
            source_sample_size = max(1, int(sample_size * source_proportion))
            
            source_sample = random.sample(source_files, min(source_sample_size, len(source_files)))
            sampled.extend(source_sample)
            
            logger.info(f"    {source}: {source_sample_size} files from {source_count} "
                       f"({100*source_proportion:.1f}%)")
        
        # Also ensure we have diversity across stakes
        logger.info("\n  Strata coverage:")
        stakes_in_sample = set()
        for file_path in sampled:
            stakes = self.file_metadata[str(file_path)]['stakes']
            stakes_in_sample.add(stakes)
        
        logger.info(f"    Unique stakes levels: {len(stakes_in_sample)}")
        logger.info(f"    Stakes: {sorted(stakes_in_sample)}")
        
        return sampled[:sample_size]  # Cap at exact sample size
    
    def generate_sample_list(self, sample_files: List[Path]) -> str:
        """
        Generate a sample list file for batch processing.
        
        Args:
            sample_files: List of sampled file paths
            
        Returns:
            Content of sample list file
        """
        lines = []
        lines.append("# Stratified Sample File List")
        lines.append(f"# Total: {len(sample_files)} files")
        lines.append(f"# Generated: 2026-05-01\n")
        
        lines.append("SAMPLE_FILES = [")
        
        by_source = defaultdict(list)
        for f in sample_files:
            source = self.file_metadata[str(f)]['source']
            by_source[source].append(f)
        
        for source in sorted(by_source.keys()):
            lines.append(f"    # {source} ({len(by_source[source])} files)")
            for f in sorted(by_source[source]):
                # Convert Path to string and use forward slashes for consistency
                path_str = str(f).replace("\\", "/")
                lines.append(f'    "{path_str}",')
        
        lines.append("]")
        
        return "\n".join(lines)


def main():
    """Main sampling workflow."""
    
    sampler = StratifiedSampler(random_seed=42)
    
    # Scan dataset directory
    data_dir = "./poker-hand-histories/data"
    logger.info(f"Scanning: {data_dir}\n")
    sampler.scan_directory(data_dir)
    
    # Create stratified sample (2.5% = middle of 1-5% range)
    sample_files = sampler.stratified_sample(percentage=2.5)
    
    logger.info(f"\nFinal sample: {len(sample_files)} files")
    
    # Generate and save sample list as Python file
    sample_list = sampler.generate_sample_list(sample_files)
    
    with open("sample_files.py", "w", encoding='utf-8') as f:
        f.write(sample_list)
    
    logger.info(f"Python sample list saved to: sample_files.py")
    
    return sampler, sample_files


if __name__ == "__main__":
    sampler, sample_files = main()
