from typing import List

def calculate_dryness(board_cards: List[str]) -> float:
    """
    Calculate a simple dryness score for the board.
    1.0 = Very Dry, 0.0 = Very Wet
    
    board_cards: List of card strings like ["As", "Kd", "8h"]
    """
    if not board_cards or len(board_cards) < 3:
        return 1.0
        
    RANK_MAP = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
        'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14,
        't': 10, 'j': 11, 'q': 12, 'k': 13, 'a': 14
    }
    
    ranks = []
    suits = []
    
    for c in board_cards:
        # Clean card string (handle [As], "As", etc.)
        c_str = str(c).strip('[]"\' ')
        if len(c_str) < 2: continue
        
        rank_char = c_str[0]
        suit_char = c_str[1].lower()
        
        if rank_char in RANK_MAP:
            ranks.append(RANK_MAP[rank_char])
            suits.append(suit_char)
        
    if not ranks:
        return 1.0
        
    score = 1.0
    
    # 1. Flush Draw Potential
    suit_counts = {}
    for s in suits:
        suit_counts[s] = suit_counts.get(s, 0) + 1
    
    if suit_counts:
        max_suit = max(suit_counts.values())
        if max_suit >= 3:
            score -= 0.4
        elif max_suit == 2:
            score -= 0.1
        
    # 2. Straight Draw Potential
    rank_values = sorted(list(set(ranks))) # Unique ranks
    if len(rank_values) >= 2:
        consecutive = 0
        max_consecutive = 0
        for i in range(len(rank_values) - 1):
            if rank_values[i+1] - rank_values[i] == 1:
                consecutive += 1
            else:
                max_consecutive = max(max_consecutive, consecutive)
                consecutive = 0
        max_consecutive = max(max_consecutive, consecutive)
        
        if max_consecutive >= 2:
            score -= 0.3
        elif max_consecutive == 1:
            score -= 0.1
            
    # 3. Paired Board
    if len(ranks) != len(set(ranks)):
        score += 0.1
        
    return max(0.0, min(1.0, score))
