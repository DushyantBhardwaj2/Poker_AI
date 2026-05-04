import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os

from src.features.analyze_distributions import get_hand_strength
from src.utils.config_loader import get_data_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Loading and processing data...")
    parsed_full_path = get_data_path('parsed_full')
    if not parsed_full_path or not os.path.exists(parsed_full_path):
        logger.error(f"Parsed data not found at {parsed_full_path}")
        return
        
    df = pd.read_parquet(parsed_full_path)
    df['rel_bet_size'] = df['bet_amount'] / df['pot_before']
    
    postflop_df = df[df['street'] > 0].copy()
    postflop_df['hand_strength'] = postflop_df.apply(get_hand_strength, axis=1)
    analysis_df = postflop_df.dropna(subset=['hand_strength']).copy()
    
    # Define weak hand threshold (bottom 30%)
    threshold = 0.3
    analysis_df['is_weak'] = analysis_df['hand_strength'] < threshold
    
    # Define bet size bins
    bet_bins = [0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 10.0, 1000]
    bet_labels = ['0-25%', '25-50%', '50-75%', '75-100%', '100-150%', '150-200%', '2-10x', 'Extreme']
    analysis_df['bet_bin'] = pd.cut(analysis_df['rel_bet_size'], bins=bet_bins, labels=bet_labels)
    
    # Pivot table: Street vs Bet Bin -> Prob(Weak)
    pivot = analysis_df.pivot_table(
        index='street', 
        columns='bet_bin', 
        values='is_weak', 
        aggfunc='mean',
        observed=True
    )
    
    # Count table for stability check
    counts = analysis_df.pivot_table(
        index='street', 
        columns='bet_bin', 
        values='is_weak', 
        aggfunc='count',
        observed=True
    )
    
    logger.info("\nProbability of Weak Hand by Street and Bet Size:")
    print(pivot)
    
    logger.info("\nSample Counts by Bin:")
    print(counts)
    
    # Visualization
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot, annot=True, cmap='YlOrRd', fmt='.2f')
    plt.title(f'P(Hand Strength < {threshold} | Street, Bet Size)')
    plt.savefig('parsed_output/bluff_probability_surface.png')
    
    # Save the lookup table
    pivot.to_csv('parsed_output/mismatch_surface_v1.csv')
    logger.info("Surface saved to parsed_output/mismatch_surface_v1.csv")

if __name__ == "__main__":
    main()
