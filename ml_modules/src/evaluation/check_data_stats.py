import pandas as pd
import os
from src.utils.config_loader import get_data_path

def check_stats():
    parsed_full_path = get_data_path('parsed_full')
    if not os.path.exists(parsed_full_path):
        print(f"Data not found at {parsed_full_path}")
        return
        
    df = pd.read_parquet(parsed_full_path)
    print(f"Total records: {len(df)}")
    print(f"Showdown records: {df[df['is_showdown'] == True].shape[0]}")
    print(f"Hands with hole cards: {df[df['hole_cards'].map(lambda x: len(x) > 0 if x is not None else False)].shape[0]}")
    print(f"Unique hands: {df['hand_id'].nunique()}")

    # Distribution of streets
    print("\nStreet Distribution:")
    print(df['street'].value_counts().sort_index())

    # Preview some showdown data
    showdown_df = df[df['is_showdown'] == True]
    if not showdown_df.empty:
        print("\nSample Showdown Data:")
        print(showdown_df[['player_id', 'street', 'hole_cards', 'board_cards']].head())
    else:
        print("\nNo showdown data found in parsed_hands_full.parquet")

if __name__ == "__main__":
    check_stats()
