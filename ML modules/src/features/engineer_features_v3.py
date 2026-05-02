import pandas as pd
import numpy as np
from src.features.analyze_dryness import calculate_dryness
from src.utils.config_loader import get_data_path
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def engineer_features_v3():
    logger.info("Loading aggressive data for v3 features...")
    parsed_agg_path = get_data_path('parsed_aggressive')
    player_stats_agg_path = get_data_path('player_stats_aggressive')
    
    if os.path.exists(parsed_agg_path):
        actions_df = pd.read_parquet(parsed_agg_path)
        player_stats_df = pd.read_parquet(player_stats_agg_path)
        logger.info(f"Loaded {len(actions_df)} aggressive actions.")
    else:
        logger.warning(f"Aggressive data not found at {parsed_agg_path}. Falling back to full dataset.")
        actions_df = pd.read_parquet(get_data_path('parsed_full'))
        player_stats_df = pd.read_parquet(get_data_path('player_stats_full'))

    # 1. Join Player Stats
    logger.info("Joining player stats...")
    df = actions_df.merge(player_stats_df, on='player_id', how='left')
    
    # Fill missing stats with global averages
    df['vpip'] = df['vpip'].fillna(df['vpip'].mean() if not df['vpip'].isna().all() else 0.25)
    df['pfr'] = df['pfr'].fillna(df['pfr'].mean() if not df['pfr'].isna().all() else 0.18)
    df['hands_played'] = df['hands_played'].fillna(0)
    
    # 2. Advanced Betting Features
    logger.info("Engineering advanced betting features...")
    df['rel_bet_size'] = df['bet_amount'] / (df['pot_before'] + 1e-6)
    
    # SPR (Stack-to-Pot Ratio)
    df['spr'] = df['starting_stack'] / (df['pot_before'] + 1e-6)
    
    # 3. Board Texture & Dryness Delta
    logger.info("Calculating dryness (unique boards optimization)...")
    
    # Make board_cards hashable for unique/map
    board_tuples = df['board_cards'].apply(tuple)
    unique_boards_tuples = board_tuples.drop_duplicates()
    logger.info(f"Computing dryness for {len(unique_boards_tuples)} unique boards...")
    
    # Map from tuple to dryness
    dryness_map = pd.Series(
        unique_boards_tuples.apply(calculate_dryness).values,
        index=unique_boards_tuples
    )
    
    # Map back to main dataframe
    df['dryness'] = board_tuples.map(dryness_map)
    
    # Vectorized dryness delta
    # Get the first dryness value per hand and street
    hand_street_dryness = df.groupby(['hand_id', 'street'])['dryness'].first().reset_index()
    hand_street_dryness['prev_street'] = hand_street_dryness['street'] - 1
    
    # Create a mapping for previous street dryness
    prev_dryness_map = hand_street_dryness.rename(columns={'dryness': 'prev_dryness', 'street': 'temp_street', 'prev_street': 'street'})
    df = df.merge(prev_dryness_map[['hand_id', 'street', 'prev_dryness']], on=['hand_id', 'street'], how='left')
    
    df['dryness_delta'] = np.where(df['street'] > 1, df['dryness'] - df['prev_dryness'].fillna(df['dryness']), 0.0)
    df.drop(columns=['prev_dryness'], inplace=True)
    
    # 4. Semantic Binning of Bet Sizes
    logger.info("Applying semantic binning...")
    df['bet_bin'] = 0
    df.loc[df['rel_bet_size'] >= 0.1, 'bet_bin'] = 1
    df.loc[df['rel_bet_size'] >= 0.4, 'bet_bin'] = 2
    df.loc[df['rel_bet_size'] >= 0.65, 'bet_bin'] = 3
    df.loc[df['rel_bet_size'] >= 1.1, 'bet_bin'] = 4
    
    # 5. Temporal Features
    logger.info("Engineering temporal features...")
    df = df.sort_values(['hand_id', 'street', 'pot_before'])
    
    # Previous action in same hand
    df['prev_action_bet_size'] = df.groupby('hand_id')['rel_bet_size'].shift(1).fillna(0)
    
    # Max bet on previous street (for bet spike) - Vectorized
    max_bets = df.groupby(['hand_id', 'street'])['bet_amount'].max().reset_index()
    max_bets['street'] = max_bets['street'] + 1 # Align with "next" street
    max_bets = max_bets.rename(columns={'bet_amount': 'prev_street_max_bet'})
    
    df = df.merge(max_bets[['hand_id', 'street', 'prev_street_max_bet']], on=['hand_id', 'street'], how='left')
    df['prev_street_max_bet'] = df['prev_street_max_bet'].fillna(0)
    
    df['bet_spike'] = np.where(df['prev_street_max_bet'] > 0, df['bet_amount'] / df['prev_street_max_bet'], 1.0)
    
    # Street-wise relative bet size change
    df['bet_size_diff'] = df['rel_bet_size'] - df['prev_action_bet_size']
    
    # 6. Narrative Consistency
    df['is_monotonic'] = (df['rel_bet_size'] >= df['prev_action_bet_size'] * 0.9).astype(int)
    
    # 7. Deep Insights: Interaction Terms (v3 specific)
    logger.info("Adding interaction terms...")
    df['dryness_bet_interaction'] = df['dryness'] * df['rel_bet_size']
    df['vpip_bet_interaction'] = df['vpip'] * df['rel_bet_size']
    
    # New v3 Interaction: Tightness * Bet Size
    # Tightness is (1 - vpip). High tightness + big bet = low bluff probability.
    df['tightness_bet_interaction'] = (1 - df['vpip']) * df['rel_bet_size']
    
    # 8. Range Miss Heuristic (Enhanced v3)
    # vpip * (dryness + dryness_delta) * log(bet_spike)
    df['range_miss'] = df['vpip'] * (df['dryness'] + df['dryness_delta'].clip(0, 1)) * np.log1p(df['bet_spike']) * (2 - df['is_monotonic'])
    
    # 9. Aggression Profile
    df['agg_profile'] = df['vpip'] / (df['pfr'] + 0.01)
    
    # Clipping for stability
    df['bet_spike'] = df['bet_spike'].clip(0, 20)
    df['rel_bet_size'] = df['rel_bet_size'].clip(0, 10)
    df['spr'] = df['spr'].clip(0, 100)
    df['dryness_delta'] = df['dryness_delta'].clip(-1, 1)
    
    # Filter columns
    feature_cols = [
        'hand_id', 'player_id', 'street', 'rel_bet_size', 'bet_spike', 'dryness',
        'dryness_delta', 'bet_bin', 'vpip', 'pfr', 'spr', 'bet_size_diff', 
        'is_monotonic', 'range_miss', 'dryness_bet_interaction', 
        'vpip_bet_interaction', 'tightness_bet_interaction', 'agg_profile',
        'is_showdown', 'hole_cards', 'board_cards'
    ]
    
    final_df = df[feature_cols]
    
    output_path = get_data_path('features_v3')
    final_df.to_parquet(output_path)
    logger.info(f"Saved {len(final_df)} records with v3 features to {output_path}")
    
    return final_df

if __name__ == "__main__":
    engineer_features_v3()
