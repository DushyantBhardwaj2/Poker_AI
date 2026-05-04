import pandas as pd
import numpy as np
from src.features.analyze_distributions import get_hand_strength
from src.utils.config_loader import get_data_path
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_labels_v3():
    logger.info("Loading v3 features...")
    features_v3_path = get_data_path('features_v3')
    if not os.path.exists(features_v3_path):
        logger.error(f"Features not found at {features_v3_path}")
        return
    df = pd.read_parquet(features_v3_path)
    
    # 1. Load Mismatch Surface
    # Try to find it in the same directory as features
    parsed_agg_path = get_data_path('parsed_aggressive')
    surface_path = os.path.join(os.path.dirname(parsed_agg_path), 'mismatch_surface.csv') if parsed_agg_path else 'data/interim/mismatch_surface.csv'
        
    try:
        surface = pd.read_csv(surface_path).set_index('dryness_bin')
        logger.info(f"Loaded mismatch surface from {surface_path}")
    except Exception as e:
        logger.warning(f"Mismatch surface not found or invalid at {surface_path}, using defaults. Error: {e}")
        surface = pd.DataFrame()
    
    logger.info("Generating high-precision soft labels (v3)...")
    
    # Dryness Bins (must match generate_mismatch_surface.py)
    df['dryness_bin_cat'] = pd.cut(
        df['dryness'], 
        bins=[0, 0.4, 0.7, 1.1], 
        labels=['Wet', 'Medium', 'Dry'],
        include_lowest=True
    )
    
    # Bet Bins (must match generate_mismatch_surface.py)
    df['bet_bin_cat'] = pd.cut(
        df['rel_bet_size'], 
        bins=[0, 0.4, 0.8, 1.2, 2.5, 1000], 
        labels=['Small', 'Medium', 'Pot', 'Over', 'Extreme'],
        include_lowest=True
    )
    
    def get_baseline_p(row):
        street = row['street']
        if street == 0: return 0.15
        
        dbin = str(row['dryness_bin_cat'])
        bbin = str(row['bet_bin_cat'])
        
        if not surface.empty and dbin in surface.index and bbin in surface.columns:
            return surface.loc[dbin, bbin]
        return 0.25
        
    df['baseline_p'] = df.apply(get_baseline_p, axis=1)
    
    # Adjustments for Precision - Using v3 features
    df['dryness_adj'] = (df['dryness'] - 0.5) * 0.3
    df['dryness_delta_adj'] = df['dryness_delta'] * 0.2
    df['spike_adj'] = np.where(df['bet_spike'] > 3.0, 0.2, 0.0)
    df['narrative_adj'] = np.where(df['is_monotonic'] == 0, 0.15, -0.05)
    
    # Using the new Tightness interaction
    # Higher tightness_bet_interaction means a tight player is betting big -> lower bluff prob
    df['tightness_adj'] = -df['tightness_bet_interaction'] * 0.2
    
    # Range Miss (already incorporates vpip and dryness in v3)
    df['range_miss_adj'] = (df['range_miss'] - df['range_miss'].mean()) * 0.25
    
    # Calculate Soft Label
    df['soft_label'] = (df['baseline_p'] + df['dryness_adj'] + df['dryness_delta_adj'] + 
                        df['spike_adj'] + df['narrative_adj'] + df['tightness_adj'] + 
                        df['range_miss_adj'])
    
    df['soft_label'] = df['soft_label'].clip(0.01, 0.99)
    
    # 2. Ground Truth Validation (High Precision Threshold)
    logger.info("Generating ground truth labels (v3 Showdown)...")
    df['true_strength'] = df.apply(get_hand_strength, axis=1)
    
    # true_label is 1 if it's a "Strict Bluff"
    df['true_label'] = np.nan
    mask = df['true_strength'].notna()
    df.loc[mask, 'true_label'] = (df.loc[mask, 'true_strength'] < 0.2).astype(int)
    
    # Confidence weight
    df['confidence_weight'] = 0.2
    df.loc[mask, 'confidence_weight'] = 1.0
    
    output_path = get_data_path('labels_v3')
    if not output_path:
        output_path = 'data/interim/labeled_dataset_v3.parquet'
        
    df.to_parquet(output_path)
    logger.info(f"Saved {len(df)} labeled records to {output_path}")
    
    return df

if __name__ == "__main__":
    generate_labels_v3()
