"""
Generate Mismatch Surface (Task B.2)

Dynamically analyzes showdown data to create a probability matrix 
mapping (Board Dryness, Bet Size) -> Probability of a Weak Hand.
This surface is used by the heuristic labeler for weak supervision.
"""

import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from src.features.analyze_distributions import get_hand_strength
from src.features.analyze_dryness import calculate_dryness
from src.utils.config_loader import get_data_path, load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_mismatch_surface():
    """Main workflow to generate the surface."""
    config = load_config()
    parsed_path = get_data_path("parsed_aggressive")
    
    if not parsed_path or not os.path.exists(parsed_path):
        logger.error(f"Parsed data not found at {parsed_path}")
        return False
        
    logger.info(f"Loading data from {parsed_path}...")
    df = pd.read_parquet(parsed_path)
    
    # 1. Filter for post-flop showdown data
    # We need both board cards and revealed hole cards
    showdown_df = df[(df['street'] > 0) & (df['is_showdown'] == True)].copy()
    
    # Ensure we have hole cards for the actor
    showdown_df = showdown_df[showdown_df['hole_cards'].apply(len) > 0].copy()
    
    if len(showdown_df) < 100:
        logger.warning(f"Low showdown sample size: {len(showdown_df)}. Results may be unstable.")
        if len(showdown_df) == 0:
            logger.error("No showdown data found. Cannot generate surface.")
            return False

    logger.info(f"Analyzing {len(showdown_df)} showdown actions...")

    # 2. Calculate behavioral and texture features
    showdown_df['hand_strength'] = showdown_df.apply(get_hand_strength, axis=1)
    showdown_df['dryness'] = showdown_df['board_cards'].apply(calculate_dryness)
    showdown_df['rel_bet_size'] = showdown_df['bet_amount'] / showdown_df['pot_before']
    
    # Drop failures
    analysis_df = showdown_df.dropna(subset=['hand_strength']).copy()
    
    # 3. Define 'Weak Hand' (Bluff Candidate)
    # Threshold 0.4 captures weak pairs and draws
    analysis_df['is_weak'] = analysis_df['hand_strength'] < 0.4
    
    # 4. Bin features for the surface
    # Dryness: Wet (0.0-0.4), Medium (0.4-0.7), Dry (0.7-1.0)
    # Bet Size: Small (<0.5 pot), Pot (0.5-1.0), Over (1.0-2.0), Extreme (>2.0)
    analysis_df['dryness_bin'] = pd.cut(
        analysis_df['dryness'], 
        bins=[0, 0.4, 0.7, 1.1], 
        labels=['Wet', 'Medium', 'Dry'],
        include_lowest=True
    )
    
    analysis_df['bet_bin'] = pd.cut(
        analysis_df['rel_bet_size'], 
        bins=[0, 0.4, 0.8, 1.2, 2.5, 1000], 
        labels=['Small', 'Medium', 'Pot', 'Over', 'Extreme'],
        include_lowest=True
    )
    
    # 5. Create the Surface (Pivot Table)
    surface = analysis_df.pivot_table(
        index='dryness_bin',
        columns='bet_bin',
        values='is_weak',
        aggfunc='mean',
        observed=True
    )
    
    # Fill missing values with reasonable defaults (interpolation)
    # If a bin is empty, we use the average for that dryness level
    surface = surface.apply(lambda row: row.fillna(row.mean()), axis=1)
    # If still NaN, use global mean
    surface = surface.fillna(analysis_df['is_weak'].mean())
    
    # 6. Save Artifacts
    output_dir = Path(parsed_path).parent
    surface_path = output_dir / "mismatch_surface.csv"
    surface.to_csv(surface_path)
    logger.info(f"Mismatch surface saved to {surface_path}")
    
    # 7. Visualization
    plt.figure(figsize=(10, 6))
    sns.heatmap(surface, annot=True, cmap='YlOrRd', fmt='.2f')
    plt.title('P(Weak Hand | Board Dryness, Bet Size)')
    plt.xlabel('Bet Size (Rel to Pot)')
    plt.ylabel('Board Dryness (1.0=Dry)')
    
    plot_path = output_dir / "mismatch_surface_plot.png"
    plt.savefig(plot_path)
    logger.info(f"Surface plot saved to {plot_path}")
    
    return True

if __name__ == "__main__":
    generate_mismatch_surface()
