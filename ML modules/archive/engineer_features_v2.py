import pandas as pd
import numpy as np
from src.features.analyze_dryness import calculate_dryness
from src.utils.config_loader import get_data_path
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def engineer_features_v2():
    logger.info("Loading aggressive data...")
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
    df['rel_bet_size'] = df['bet_amount'] / df['pot_before']
    
    # SPR (Stack-to-Pot Ratio) - In-depth feature
    df['spr'] = df['starting_stack'] / (df['pot_before'] + 1e-6)
    
    # 3. Board Texture
    logger.info("Calculating dryness...")
    df['dryness'] = df['board_cards'].apply(calculate_dryness)
    
    # 4. Temporal Features
    logger.info("Engineering temporal features...")
    df = df.sort_values(['hand_id', 'street', 'pot_before'])
    
    # Previous action in same hand
    df['prev_action_bet_size'] = df.groupby('hand_id')['rel_bet_size'].shift(1).fillna(0)
    
    # Max bet on previous street (for bet spike)
    max_bets = df.groupby(['hand_id', 'street'])['bet_amount'].max().unstack(fill_value=0)
    
    def get_prev_max_bet(row):
        street = row['street']
        if street == 0: return 0.0
        return max_bets.loc[row['hand_id'], street - 1] if street - 1 in max_bets.columns else 0.0
    
    df['prev_street_max_bet'] = df.apply(get_prev_max_bet, axis=1)
    df['bet_spike'] = np.where(df['prev_street_max_bet'] > 0, df['bet_amount'] / df['prev_street_max_bet'], 1.0)
    
    # Street-wise relative bet size change
    df['bet_size_diff'] = df['rel_bet_size'] - df['prev_action_bet_size']
    
    # 5. Narrative Consistency
    df['is_monotonic'] = (df['rel_bet_size'] >= df['prev_action_bet_size'] * 0.9).astype(int)
    
    # 6. Deep Insights: Interaction Terms
    df['dryness_bet_interaction'] = df['dryness'] * df['rel_bet_size']
    df['vpip_bet_interaction'] = df['vpip'] * df['rel_bet_size']
    
    # 7. Range Miss Heuristic (Enhanced v2)
    # vpip * dryness * log(bet_spike) / log(is_monotonic + 1)
    df['range_miss'] = df['vpip'] * df['dryness'] * np.log1p(df['bet_spike']) * (2 - df['is_monotonic'])
    
    # 8. Aggression Profile
    df['agg_profile'] = df['vpip'] / (df['pfr'] + 0.01)
    
    # Position Inference (Simplified: 1 to 6)
    # We don't have total players easily, but we can use actor index as a proxy for relative position
    # In PHH, actor_index is fixed. We'll just keep it as is.
    
    # Clipping for stability
    df['bet_spike'] = df['bet_spike'].clip(0, 20)
    df['rel_bet_size'] = df['rel_bet_size'].clip(0, 10)
    df['spr'] = df['spr'].clip(0, 100)
    
    # Filter columns
    feature_cols = [
        'hand_id', 'player_id', 'street', 'rel_bet_size', 'bet_spike', 'dryness',
        'vpip', 'pfr', 'spr', 'bet_size_diff', 'is_monotonic', 'range_miss',
        'dryness_bet_interaction', 'vpip_bet_interaction', 'agg_profile',
        'is_showdown', 'hole_cards', 'board_cards'
    ]
    
    final_df = df[feature_cols]
    
    output_path = get_data_path('features_v2')
    final_df.to_parquet(output_path)
    logger.info(f"Saved {len(final_df)} records with v2 features to {output_path}")
    
    return final_df

if __name__ == "__main__":
    engineer_features_v2()
