import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from analyze_distributions import get_hand_strength
from pokerkit import Card
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_dryness(board_cards):
    """
    Calculate a simple dryness score for the board.
    1.0 = Very Dry, 0.0 = Very Wet
    """
    if board_cards is None or len(board_cards) < 3:
        return 1.0
        
    # Flatten and clean cards
    cards = []
    for c in board_cards:
        if isinstance(c, (list, np.ndarray)):
            cards.append(str(c[0]).strip('[]'))
        else:
            cards.append(str(c).strip('[]'))
            
    # Pokerkit card objects
    try:
        pk_cards = []
        for c in cards:
            # Card.parse returns a generator
            pk_cards.extend(list(Card.parse(c)))
    except:
        return 0.5 # Fallback
        
    if not pk_cards:
        return 1.0
        
    RANK_MAP = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    ranks = [RANK_MAP.get(c.rank.value, 0) for c in pk_cards]
    suits = [c.suit.value for c in pk_cards]
    
    score = 1.0
    
    # 1. Flush Draw Potential
    suit_counts = pd.Series(suits).value_counts()
    max_suit = suit_counts.max()
    if max_suit >= 3:
        score -= 0.4 # Flush completed or heavy draw
    elif max_suit == 2:
        score -= 0.1 # Backdoor or minor draw
        
    # 2. Straight Draw Potential (simplified)
    rank_values = sorted([r for r in ranks])
    # Check for gaps
    gaps = np.diff(rank_values)
    if (gaps == 1).sum() >= 2:
        score -= 0.3 # Connected board
    elif (gaps == 1).sum() == 1:
        score -= 0.1
        
    # 3. Paired Board
    rank_counts = pd.Series(ranks).value_counts()
    if rank_counts.max() >= 2:
        score += 0.1 # Paired boards are often drier for some ranges
        
    return max(0.0, min(1.0, score))

def main():
    logger.info("Loading data and calculating dryness...")
    df = pd.read_parquet('parsed_output/parsed_hands_full.parquet')
    
    # Analyze post-flop records
    postflop_df = df[df['street'] > 0].copy()
    postflop_df['dryness'] = postflop_df['board_cards'].apply(calculate_dryness)
    postflop_df['hand_strength'] = postflop_df.apply(get_hand_strength, axis=1)
    
    analysis_df = postflop_df.dropna(subset=['hand_strength']).copy()
    analysis_df['is_weak'] = analysis_df['hand_strength'] < 0.3
    
    # Bin dryness
    analysis_df['dryness_bin'] = pd.cut(analysis_df['dryness'], bins=[0, 0.4, 0.7, 1.0], labels=['Wet', 'Medium', 'Dry'])
    
    # Bluff frequency by dryness
    dryness_pivot = analysis_df.groupby('dryness_bin', observed=True)['is_weak'].mean()
    logger.info("\nWeak Hand Frequency by Board Dryness:")
    print(dryness_pivot)
    
    # Interaction: Dryness + Bet Size
    analysis_df['rel_bet_size'] = analysis_df['bet_amount'] / analysis_df['pot_before']
    analysis_df['bet_bin'] = pd.cut(analysis_df['rel_bet_size'], bins=[0, 0.5, 1.0, 100], labels=['Small', 'Pot', 'Over'])
    
    interaction = analysis_df.pivot_table(
        index='dryness_bin',
        columns='bet_bin',
        values='is_weak',
        aggfunc='mean',
        observed=True
    )
    
    logger.info("\nInteraction Heatmap (Dryness x Bet Size):")
    print(interaction)
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(interaction, annot=True, cmap='YlOrRd')
    plt.title('P(Weak Hand | Dryness, Bet Size)')
    plt.savefig('parsed_output/dryness_bet_interaction.png')

if __name__ == "__main__":
    main()
