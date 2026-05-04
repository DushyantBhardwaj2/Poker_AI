"""Quick test to understand pokerkit API."""

import pokerkit
from pathlib import Path

# Test different files
test_files = [
    'poker-hand-histories/data/dwan-ivey-2009.phh',
    'poker-hand-histories/data/antonius-blom-2009.phh',
]

for file_path in test_files:
    if not Path(file_path).exists():
        continue
        
    print(f"\n{'='*60}")
    print(f"File: {Path(file_path).name}")
    print('='*60)
    
    with open(file_path) as f:
        content = f.read()
    
    hands = pokerkit.HandHistory.loads(content)
    if not isinstance(hands, list):
        hands = [hands]
    
    print(f"Total hands: {len(hands)}")
    
    for idx, hand in enumerate(hands[:1]):  # First hand only
        print(f"\nHand {idx}:")
        print(f"  Variant: {hand.variant}")
        print(f"  Players: {hand.players}")
        print(f"  Winnings: {hand.winnings}")
        
        # Check states
        state_actions = list(hand.state_actions)
        print(f"  state_actions: {len(state_actions)}")
        
        # Show first few state actions
        for i, (s, a) in enumerate(state_actions[:5]):
            total_pot = sum(p.amount for p in s.pots) if s.pots else 0
            actor_name = hand.players[s.actor_index] if s.actor_index is not None and s.actor_index < len(hand.players) else None
            print(f"    [{i}] street={s.street_index}, actor={actor_name}, pot={total_pot}, action={a}")
        
        # Check if any non-None winning (indicates showdown)
        if hand.winnings:
            has_showdown = any(w != 0 for w in hand.winnings if w is not None)
            print(f"  Has showdown (nonzero winnings): {has_showdown}")
        else:
            print(f"  Winnings is None")
        
        break
