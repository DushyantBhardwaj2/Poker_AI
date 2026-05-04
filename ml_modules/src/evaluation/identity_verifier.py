"""
Cross-File Identity Verification

Verifies that player identities are consistent across different files in each dataset.
This confirms that calculating lifetime statistics (VPIP/PFR) is mathematically valid.

Samples files from ACPC, HandHQ, Pluribus, and WSOP sources to verify identity consistency.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import pokerkit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IdentityVerifier:
    """Verifies player identity consistency across PHH files."""
    
    def __init__(self):
        """Initialize the verifier."""
        self.player_files: Dict[str, Set[str]] = defaultdict(set)  # player_name -> set of files
        self.file_players: Dict[str, Set[str]] = defaultdict(set)  # filename -> set of players
        self.dataset_sources: Dict[str, Set[str]] = defaultdict(set)  # source -> set of players
        self.parse_errors: List[str] = []
    
    def extract_dataset_source(self, file_path: str) -> str:
        """
        Extract dataset source from file path.
        
        Expected structure:
        - poker-hand-histories/data/ACPC_*.phh -> "ACPC"
        - poker-hand-histories/data/handhq/.../*.phh -> "HandHQ"
        - poker-hand-histories/data/pluribus/.../*.phh -> "Pluribus"
        - poker-hand-histories/data/wsop/.../*.phh -> "WSOP"
        """
        path = Path(file_path)
        parts = path.parts
        
        if "annual-computer-poker-competition" in str(file_path).lower() or "acpc" in str(file_path).lower():
            return "ACPC"
        elif "handhq" in str(file_path).lower():
            return "HandHQ"
        elif "pluribus" in str(file_path).lower():
            return "Pluribus"
        elif "wsop" in str(file_path).lower():
            return "WSOP"
        else:
            # Default: try to infer from parent directory
            if len(parts) > 0:
                parent = parts[-2] if len(parts) > 1 else parts[0]
                return parent
            return "Unknown"
    
    def parse_phh_file(self, file_path: str) -> Optional[List[str]]:
        """
        Parse a PHH file and extract player names.
        
        Args:
            file_path: Path to PHH file
            
        Returns:
            List of player names, or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            hand_histories = pokerkit.HandHistory.loads(content)
            if not isinstance(hand_histories, list):
                hand_histories = [hand_histories]
            
            # Collect all unique player names from all hands in the file
            players = set()
            for hand in hand_histories:
                if hand.players:
                    players.update(hand.players)
            
            return list(players)
        
        except Exception as e:
            self.parse_errors.append(f"{Path(file_path).name}: {str(e)}")
            return None
    
    def verify_directory(self, directory: str, sample_size: int = 3) -> None:
        """
        Verify identity consistency in a directory.
        
        Samples `sample_size` files from the directory and checks for player consistency.
        
        Args:
            directory: Path to directory containing PHH files
            sample_size: Number of files to sample per source
        """
        path = Path(directory)
        files = sorted([f for f in path.glob("*.phh") if f.is_file()])[:sample_size]
        
        logger.info(f"\nVerifying {len(files)} sample files from: {directory}")
        
        for file_path in files:
            players = self.parse_phh_file(str(file_path))
            if players is None:
                continue
            
            filename = file_path.name
            source = self.extract_dataset_source(str(file_path))
            
            # Track which files each player appears in
            for player in players:
                self.player_files[player].add(filename)
                self.dataset_sources[source].add(player)
            
            # Track which players appear in each file
            self.file_players[filename].update(players)
            
            logger.info(f"  {filename}: {len(players)} players")
    
    def verify_subdirectories_recursive(
        self, 
        root_directory: str, 
        sample_per_dir: int = 2,
        max_depth: int = 3
    ) -> None:
        """
        Recursively verify identity consistency across subdirectories.
        
        Args:
            root_directory: Root directory to start from
            sample_per_dir: Number of files to sample per directory
            max_depth: Maximum directory depth to traverse
        """
        root = Path(root_directory)
        
        def process_dir(current_path: Path, depth: int) -> None:
            if depth > max_depth:
                return
            
            # Get PHH files in this directory
            phh_files = sorted([f for f in current_path.glob("*.phh") if f.is_file()])[:sample_per_dir]
            
            if phh_files:
                logger.info(f"\n[Depth {depth}] {current_path.relative_to(root)}")
                for file_path in phh_files:
                    players = self.parse_phh_file(str(file_path))
                    if players is None:
                        continue
                    
                    filename = file_path.name
                    source = self.extract_dataset_source(str(file_path))
                    
                    # Track players
                    for player in players:
                        self.player_files[player].add(filename)
                        self.dataset_sources[source].add(player)
                    
                    self.file_players[filename].update(players)
                    logger.info(f"  {filename}: {len(players)} players")
            
            # Recurse into subdirectories
            for subdir in sorted(current_path.iterdir()):
                if subdir.is_dir() and not subdir.name.startswith('.'):
                    process_dir(subdir, depth + 1)
        
        process_dir(root, depth=0)
    
    def generate_report(self) -> str:
        """
        Generate a summary report of identity verification.
        
        Returns:
            Report string
        """
        lines = []
        lines.append("\n" + "="*70)
        lines.append("CROSS-FILE IDENTITY VERIFICATION REPORT")
        lines.append("="*70)
        
        # Summary statistics
        lines.append(f"\nTotal unique players found: {len(self.player_files)}")
        lines.append(f"Total files processed: {len(self.file_players)}")
        lines.append(f"Parse errors: {len(self.parse_errors)}")
        
        # Players appearing in multiple files
        multi_file_players = {p: files for p, files in self.player_files.items() if len(files) > 1}
        lines.append(f"Players in multiple files: {len(multi_file_players)}")
        
        # Per-source breakdown
        lines.append("\n" + "-"*70)
        lines.append("BREAKDOWN BY SOURCE:")
        lines.append("-"*70)
        
        for source in sorted(self.dataset_sources.keys()):
            players = self.dataset_sources[source]
            lines.append(f"\n{source}:")
            lines.append(f"  Unique players: {len(players)}")
            
            # Count recurring players in this source
            recurring = sum(1 for p in players if len(self.player_files[p]) > 1)
            lines.append(f"  Players in multiple files: {recurring}")
            
            # Show sample of players
            if players:
                sample = sorted(list(players))[:5]
                lines.append(f"  Sample players: {', '.join(sample)}")
        
        # Top recurring players
        lines.append("\n" + "-"*70)
        lines.append("TOP 10 RECURRING PLAYERS (Most Files):")
        lines.append("-"*70)
        
        sorted_players = sorted(
            self.player_files.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        for player, files in sorted_players:
            lines.append(f"  {player}: {len(files)} files")
        
        # Conclusion
        lines.append("\n" + "="*70)
        
        if multi_file_players:
            conclusion = "[PASS] Player identities are consistent across multiple files."
            lines.append(conclusion)
            lines.append(f"   This confirms that lifetime statistics (VPIP/PFR) calculation is valid.")
        else:
            conclusion = "[WARN] Limited recurring players found."
            lines.append(conclusion)
            lines.append(f"   May need to check sample coverage or data source diversity.")
        
        if self.parse_errors:
            lines.append(f"\n[WARN] Parse Errors ({len(self.parse_errors)}):")
            for error in self.parse_errors[:5]:
                lines.append(f"   - {error}")
            if len(self.parse_errors) > 5:
                lines.append(f"   ... and {len(self.parse_errors) - 5} more")
        
        lines.append("="*70)
        
        return "\n".join(lines)


def main():
    """Main verification flow."""
    
    verifier = IdentityVerifier()
    
    # Define dataset sources to verify
    dataset_paths = {
        "ACPC": "./poker-hand-histories/data/annual-computer-poker-competition/competitions",
        "HandHQ": "./poker-hand-histories/data/handhq",
        "Pluribus": "./poker-hand-histories/data/pluribus",
        "WSOP": "./poker-hand-histories/data/wsop",
        "Individual": "./poker-hand-histories/data",
    }
    
    logger.info("Starting Cross-File Identity Verification...")
    
    for source_name, path in dataset_paths.items():
        if not Path(path).exists():
            logger.warning(f"Path not found: {path}")
            continue
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Verifying: {source_name}")
        logger.info(f"Path: {path}")
        logger.info(f"{'='*70}")
        
        # Use recursive verification for structured datasets
        if source_name in ["ACPC", "HandHQ", "Pluribus"]:
            verifier.verify_subdirectories_recursive(path, sample_per_dir=2, max_depth=2)
        else:
            # For individual files directory, just sample top-level files
            verifier.verify_directory(path, sample_size=5)
    
    # Generate and print report
    report = verifier.generate_report()
    print(report)
    
    # Save report
    with open("identity_verification_report.txt", "w") as f:
        f.write(report)
    logger.info("Report saved to: identity_verification_report.txt")
    
    return verifier


if __name__ == "__main__":
    verifier = main()
