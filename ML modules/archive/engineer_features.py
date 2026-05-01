import pandas as pd
import numpy as np
from analyze_dryness import calculate_dryness
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def engineer_features():
    logger.info("Loading data...")
    actions_df = pd.read_parquet('parsed_output/parsed_hands_full.parquet')
    player_stats_df = pd.read_parquet('parsed_output/player_stats.parquet')
    
    # 1. Join Player Stats
    logger.info("Joining player stats...")
    df = actions_df.merge(player_stats_df, on='player_id', how='left')
    
    # Fill missing stats with global averages (or sensible defaults)
    df['vpip'] = df['vpip'].fillna(df['vpip'].mean() if not df['vpip'].isna().all() else 0.25)
    df['pfr'] = df['pfr'].fillna(df['pfr'].mean() if not df['pfr'].isna().all() else 0.18)
    df['hands_played'] = df['hands_played'].fillna(0)
    
    # 2. Basic Betting Features
    logger.info("Engineering basic betting features...")
    df['rel_bet_size'] = df['bet_amount'] / df['pot_before']
    
    # 3. Board Texture
    logger.info("Calculating dryness...")
    df['dryness'] = df['board_cards'].apply(calculate_dryness)
    
    # 4. Temporal Features (Previous Street/Action)
    logger.info("Engineering temporal features...")
    # Group by hand_id to get previous max bet
    hand_groups = df.groupby('hand_id')
    
    # Max bet on previous street
    # This is tricky because we need the max bet of the street before the current record's street.
    # We'll calculate max bet per hand per street first.
    max_bets = df.groupby(['hand_id', 'street'])['bet_amount'].max().unstack(fill_value=0)
    
    def get_prev_max_bet(row):
        street = row['street']
        if street == 0:
            return 0.0
        # Return max bet from street - 1
        return max_bets.loc[row['hand_id'], street - 1] if street - 1 in max_bets.columns else 0.0
    
    df['prev_street_max_bet'] = df.apply(get_prev_max_bet, axis=1)
    df['bet_spike'] = np.where(df['prev_street_max_bet'] > 0, df['bet_amount'] / df['prev_street_max_bet'], 1.0)
    
    # Previous action in same hand
    df = df.sort_values(['hand_id', 'street', 'pot_before']) # Ensure order
    df['prev_action_bet_size'] = df.groupby('hand_id')['rel_bet_size'].shift(1).fillna(0)
    
    # 5. Narrative Consistency
    # consistency_with_line = 1 if current bet >= previous bet (monotonicity)
    df['is_monotonic'] = (df['rel_bet_size'] >= df['prev_action_bet_size']).astype(int)
    
    # 6. Mismatch Heuristic (Range Miss)
    # Using the logic from PLAN.md: vpip * dryness * position_weight * action_consistency
    # For now, position_weight is 1.0 (we don't have position yet)
    # action_consistency_factor = 1.0 + 0.3 * narrative_break_score
    # narrative_break_score = zscore(rel_bet_size) - consistency_with_line
    
    # Simplified Range Miss for v1:
    # High VPIP + High Dryness + Large Bet Spike = High Range Miss
    df['range_miss'] = df['vpip'] * df['dryness'] * np.log1p(df['bet_spike'])
    
    # Normalize features (Z-Score or clipping)
    df['bet_spike'] = df['bet_spike'].clip(0, 10)
    df['rel_bet_size'] = df['rel_bet_size'].clip(0, 5)
    
    # 7. Data Leakage Guard
    # Check that we don't use hole_cards for features (except for labels/validation later)
    feature_cols = [
        'hand_id', 'player_id', 'street', 'rel_bet_size', 'bet_spike', 'dryness',
        'vpip', 'pfr', 'prev_action_bet_size', 'is_monotonic', 'range_miss',
        'is_showdown', 'hole_cards', 'board_cards' # keeping these for labeling/validation in next phase
    ]
    
    final_df = df[feature_cols]
    
    output_path = 'parsed_output/features_v1.parquet'
    final_df.to_parquet(output_path)
    logger.info(f"Saved {len(final_df)} records with features to {output_path}")
    
    return final_df

if __name__ == "__main__":
    engineer_features()
