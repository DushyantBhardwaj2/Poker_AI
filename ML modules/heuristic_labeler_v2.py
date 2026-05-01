import pandas as pd
import numpy as np
from analyze_distributions import get_hand_strength
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_labels_v2():
    logger.info("Loading v2 features...")
    df = pd.read_parquet('parsed_output/features_v2.parquet')
    
    # 1. Load Mismatch Surface
    try:
        surface = pd.read_csv('parsed_output/mismatch_surface_v1.csv').set_index('street')
    except:
        logger.warning("Mismatch surface not found, using defaults.")
        surface = pd.DataFrame()
    
    logger.info("Generating high-precision soft labels...")
    
    # Bet Bins
    bet_bins = [0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 10.0, 1000]
    bet_labels = ['0-25%', '25-50%', '50-75%', '75-100%', '100-150%', '150-200%', '2-10x', 'Extreme']
    df['bet_bin'] = pd.cut(df['rel_bet_size'], bins=bet_bins, labels=bet_labels)
    
    def get_baseline_p(row):
        street = row['street']
        bet_bin = row['bet_bin']
        if street == 0: return 0.15
        if not surface.empty and street in surface.index and bet_bin in surface.columns:
            return surface.loc[street, bet_bin]
        return 0.25
        
    df['baseline_p'] = df.apply(get_baseline_p, axis=1)
    
    # Adjustments for Precision
    # 1. Dryness: Increase bluff prob on dry boards (+15%)
    df['dryness_adj'] = (df['dryness'] - 0.5) * 0.3
    
    # 2. Bet Spike: Large spikes are suspicious (+15%)
    df['spike_adj'] = np.where(df['bet_spike'] > 2.5, 0.15, 0.0)
    
    # 3. Narrative Break: Non-monotonic lines (+10%)
    df['narrative_adj'] = np.where(df['is_monotonic'] == 0, 0.1, -0.05)
    
    # 4. Range Miss: High range miss = high bluff probability
    # range_miss was calculated in feature eng. We'll use it as a multiplier or addition.
    df['range_miss_adj'] = (df['range_miss'] - df['range_miss'].mean()) * 0.2
    
    # 5. Opponent Profile: Loose-Aggressive (LAG) players bluff more
    # agg_profile = vpip / pfr. High agg_profile (> 1.5) means passive. Low (< 1.2) means aggressive.
    df['opp_adj'] = np.where(df['agg_profile'] < 1.2, 0.05, -0.05)
    
    # Calculate Soft Label
    df['soft_label'] = (df['baseline_p'] + df['dryness_adj'] + df['spike_adj'] + df['narrative_adj'] + df['range_miss_adj'] + df['opp_adj'])
    df['soft_label'] = df['soft_label'].clip(0.01, 0.99)
    
    # 2. Ground Truth Validation (High Precision Threshold)
    logger.info("Generating ground truth labels (High Precision: <0.2 strength)...")
    df['true_strength'] = df.apply(get_hand_strength, axis=1)
    
    # true_label is 1 if it's a "Strict Bluff"
    df['true_label'] = np.nan
    mask = df['true_strength'].notna()
    df.loc[mask, 'true_label'] = (df.loc[mask, 'true_strength'] < 0.2).astype(int) # Conservative threshold
    
    # Confidence weight
    df['confidence_weight'] = 0.2 # Lower base confidence for heuristics
    df.loc[mask, 'confidence_weight'] = 1.0 # High confidence for showdown
    
    output_path = 'parsed_output/labeled_dataset_v2.parquet'
    df.to_parquet(output_path)
    logger.info(f"Saved {len(df)} labeled records to {output_path}")
    
    return df

if __name__ == "__main__":
    generate_labels_v2()
