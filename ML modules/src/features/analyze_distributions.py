import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pokerkit import StandardHighHand
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_hand_strength(row):
    if row['street'] == 0:
        return None # Skip pre-flop for now
    
    hole = row['hole_cards']
    board = row['board_cards']
    
    if hole is None or board is None or len(hole) < 2 or len(board) == 0:
        return None
    
    # Flatten board if it's nested list
    if len(board) > 0 and isinstance(board[0], (list, np.ndarray)):
        try:
            board = [card[0] if isinstance(card, (list, np.ndarray)) else card for card in board]
        except:
             board = [card for sublist in board for card in sublist]
    
    try:
        # Strip brackets if present (sometimes pokerkit strings include them)
        hole = [str(c).strip('[]') for c in hole]
        board = [str(c).strip('[]') for c in board]
        
        hole_str = ''.join(hole)
        board_str = ''.join(board)
        hand = StandardHighHand.from_game(hole_str, board_str)
        if hand:
            # Standard NLHE has 7462 distinct hand ranks (0 to 7461)
            # We normalize to [0, 1]
            return hand.entry.index / 7461.0
    except Exception as e:
        # Debug the first few failures
        if not hasattr(get_hand_strength, 'count'): get_hand_strength.count = 0
        if get_hand_strength.count < 5:
            logger.warning(f"Eval failed for hole={hole}, board={board}, error={e}")
            get_hand_strength.count += 1
    return None

from src.utils.config_loader import get_data_path

def main():
    logger.info("Loading parsed data...")
    parsed_full_path = get_data_path('parsed_full')
    if not parsed_full_path or not os.path.exists(parsed_full_path):
        logger.error(f"Parsed data not found at {parsed_full_path}")
        return
        
    df = pd.read_parquet(parsed_full_path)
    
    # Calculate relative bet size
    df['rel_bet_size'] = df['bet_amount'] / df['pot_before']
    
    # Filter for post-flop actions
    postflop_df = df[df['street'] > 0].copy()
    logger.info(f"Post-flop records: {len(postflop_df)}")
    
    # Calculate hand strength
    logger.info("Calculating hand strengths (this may take a moment)...")
    postflop_df['hand_strength'] = postflop_df.apply(get_hand_strength, axis=1)
    
    # Drop rows without strength (no revealed cards)
    analysis_df = postflop_df.dropna(subset=['hand_strength']).copy()
    logger.info(f"Records with revealed hand strength: {len(analysis_df)}")
    
    if analysis_df.empty:
        logger.error("No showdown data available for post-flop analysis.")
        return

    # 1. Analyze distribution of hand strength for aggressive actions
    plt.figure(figsize=(10, 6))
    sns.histplot(analysis_df['hand_strength'], bins=20, kde=True)
    plt.title('Distribution of Hand Strength for Aggressive Actions (Showdown Data)')
    plt.xlabel('Hand Strength (0=Worst, 1=Best)')
    plt.ylabel('Frequency')
    plt.savefig('parsed_output/dist_hand_strength.png')
    
    # 2. Analyze Hand Strength vs Rel Bet Size
    plt.figure(figsize=(10, 6))
    # Clip rel_bet_size for better visualization (avoid extreme overbets)
    analysis_df['rel_bet_size_clipped'] = analysis_df['rel_bet_size'].clip(0, 2)
    sns.scatterplot(data=analysis_df, x='hand_strength', y='rel_bet_size_clipped', alpha=0.3)
    plt.title('Hand Strength vs Relative Bet Size')
    plt.xlabel('Hand Strength')
    plt.ylabel('Rel Bet Size (Clipped at 2.0)')
    plt.savefig('parsed_output/strength_vs_bet.png')
    
    # 3. Aggregated analysis: Bluff Frequency vs Bet Size Bins
    # We define a "weak hand" as strength < 0.3 for this exploratory analysis
    analysis_df['is_weak'] = analysis_df['hand_strength'] < 0.3
    
    # Bin relative bet size
    analysis_df['bet_bin'] = pd.cut(analysis_df['rel_bet_size'], bins=[0, 0.3, 0.6, 1.0, 2.0, 100], labels=['Small', 'Medium', 'Pot', 'Over', 'Extreme'])
    
    bluff_by_bin = analysis_df.groupby('bet_bin', observed=True)['is_weak'].mean()
    logger.info("\nWeak Hand Frequency by Bet Size Bin:")
    logger.info(bluff_by_bin)
    
    # Save statistics
    with open('parsed_output/analysis_report.txt', 'w') as f:
        f.write("JOINT DISTRIBUTION ANALYSIS\n")
        f.write(f"Total post-flop records analyzed: {len(analysis_df)}\n")
        f.write("\nWeak Hand (<0.3 strength) frequency by bet size:\n")
        f.write(bluff_by_bin.to_string())
        f.write("\n\nCorrelation (Strength vs Rel Bet Size): ")
        f.write(str(analysis_df[['hand_strength', 'rel_bet_size']].corr().iloc[0, 1]))

    logger.info("Analysis complete. Reports and plots saved to parsed_output/")

if __name__ == "__main__":
    main()
