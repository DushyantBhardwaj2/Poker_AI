import pandas as pd
import numpy as np
from src.utils.config_loader import get_data_path

def check_corr():
    df = pd.read_parquet(get_data_path('labels_v3'))
    mask = df['true_label'].notna()
    corr = df.loc[mask, ['soft_label', 'true_label']].corr().iloc[0,1]
    print(f"Heuristic-Showdown Correlation: {corr:.3f}")
    
    # Check by street
    for street in df['street'].unique():
        s_mask = mask & (df['street'] == street)
        if s_mask.any():
            s_corr = df.loc[s_mask, ['soft_label', 'true_label']].corr().iloc[0,1]
            print(f"Street {street} Correlation: {s_corr:.3f}")

if __name__ == "__main__":
    check_corr()
