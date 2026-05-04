import pandas as pd
import numpy as np
from src.utils.config_loader import get_data_path

def check_feature_alignment():
    df = pd.read_parquet(get_data_path('labels_v3'))
    mask = df['true_label'].notna()
    
    features = [
        'street', 'rel_bet_size', 'bet_spike', 'dryness', 'dryness_delta', 
        'vpip', 'pfr', 'spr', 'bet_size_diff', 
        'is_monotonic', 'range_miss', 'dryness_bet_interaction', 
        'vpip_bet_interaction', 'tightness_bet_interaction', 'agg_profile'
    ]
    
    print("Correlation with Ground Truth (true_label):")
    corrs = []
    for f in features:
        if f in df.columns:
            c = df.loc[mask, [f, 'true_label']].corr().iloc[0,1]
            corrs.append({'feature': f, 'corr': c})
            
    corrs_df = pd.DataFrame(corrs).sort_values('corr', key=abs, ascending=False)
    print(corrs_df)

if __name__ == "__main__":
    check_feature_alignment()
