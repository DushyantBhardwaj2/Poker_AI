import pandas as pd
import numpy as np
from analyze_distributions import get_hand_strength
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_labels():
    logger.info("Loading features...")
    df = pd.read_parquet('parsed_output/features_v1.parquet')
    
    # 1. Load Mismatch Surface (from Phase 1.5)
    try:
        surface = pd.read_csv('parsed_output/mismatch_surface_v1.csv', index_index='street')
    except:
        # Fallback to a simplified version if CSV not found or formatted differently
        surface = pd.read_csv('parsed_output/mismatch_surface_v1.csv').set_index('street')
    
    logger.info("Generating soft labels using heuristic engine...")
    
    # Map each action to its baseline bluff probability from the surface
    bet_bins = [0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 10.0, 1000]
    bet_labels = ['0-25%', '25-50%', '50-75%', '75-100%', '100-150%', '150-200%', '2-10x', 'Extreme']
    df['bet_bin'] = pd.cut(df['rel_bet_size'], bins=bet_bins, labels=bet_labels)
    
    def get_baseline_p(row):
        street = row['street']
        bet_bin = row['bet_bin']
        if street == 0:
            return 0.2 # Pre-flop default
        if street in surface.index and bet_bin in surface.columns:
            return surface.loc[street, bet_bin]
        return 0.3 # Global default
        
    df['baseline_p'] = df.apply(get_baseline_p, axis=1)
    
    # Adjust baseline with other factors
    # Dryness: Increase bluff prob on dry boards (found to be +12% in Phase 1.5)
    # dryness is 0 (wet) to 1 (dry). Center at 0.5.
    df['dryness_adj'] = (df['dryness'] - 0.5) * 0.2
    
    # Bet Spike: Sudden large bets are slightly more likely to be bluffs
    df['spike_adj'] = np.where(df['bet_spike'] > 2.0, 0.1, 0.0)
    
    # Calculate Soft Label (bounded [0, 1])
    df['soft_label'] = (df['baseline_p'] + df['dryness_adj'] + df['spike_adj']).clip(0.01, 0.99)
    
    # 2. Generate True Labels for Showdown Hands (for validation)
    logger.info("Generating true labels for showdown hands...")
    # Calculate actual hand strength for ground truth
    df['true_strength'] = df.apply(get_hand_strength, axis=1)
    
    # True label: 1 if strength < 0.3 (Bluff), 0 otherwise (Value)
    # Only defined if true_strength is available
    df['true_label'] = np.nan
    mask = df['true_strength'].notna()
    df.loc[mask, 'true_label'] = (df.loc[mask, 'true_strength'] < 0.3).astype(int)
    
    # Confidence weight: 1.0 for showdown hands (ground truth), 0.3 for soft-labels
    df['confidence_weight'] = 0.3
    df.loc[mask, 'confidence_weight'] = 1.0
    
    output_path = 'parsed_output/labeled_dataset_v1.parquet'
    df.to_parquet(output_path)
    logger.info(f"Saved {len(df)} labeled records to {output_path}")
    
    # Summary of labels
    logger.info(f"Soft label mean: {df['soft_label'].mean():.3f}")
    if mask.any():
        logger.info(f"True label (showdown) mean: {df.loc[mask, 'true_label'].mean():.3f}")
        logger.info(f"Showdown hands: {mask.sum()}")
    
    return df

if __name__ == "__main__":
    generate_labels()
