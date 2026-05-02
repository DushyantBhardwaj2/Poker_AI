import joblib
import pandas as pd
import numpy as np
import os
from sklearn.metrics import precision_recall_curve
from src.utils.config_loader import load_config, get_data_path

def analyze_pr():
    config = load_config()
    df = pd.read_parquet(get_data_path('labels_v3'))
    model_path = os.path.join(config['paths']['models'], 'bluff_detector_v3.joblib')
    model = joblib.load(model_path)
    
    features = [
        'street', 'rel_bet_size', 'bet_spike', 'dryness', 'dryness_delta', 
        'bet_bin', 'vpip', 'pfr', 'spr', 'bet_size_diff', 
        'is_monotonic', 'range_miss', 'dryness_bet_interaction', 
        'vpip_bet_interaction', 'tightness_bet_interaction', 'agg_profile'
    ]
    
    showdown_mask = df['true_label'].notna()
    X_test = df.loc[showdown_mask, features].fillna(0)
    y_true = df.loc[showdown_mask, 'true_label'].astype(int)
    
    y_prob = model.predict(X_test)
    
    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    
    print(f"Total showdown records: {len(y_true)}")
    print(f"True positive (Strict Bluff) count: {y_true.sum()}")
    print(f"Max Precision: {np.max(precision):.3f}")
    
    for target_p in [0.3, 0.4, 0.5, 0.6, 0.7]:
        valid_idx = np.where(precision[:-1] >= target_p)[0]
        if len(valid_idx) > 0:
            # We want the highest recall for this precision level
            # precision/recall are sorted by threshold? No, thresholds are increasing.
            # As threshold increases, precision generally increases and recall decreases.
            # So the first index where precision >= target_p is the one with the highest recall.
            idx = valid_idx[0]
            print(f"P >= {target_p}: Threshold={thresholds[idx]:.3f}, Precision={precision[idx]:.3f}, Recall={recall[idx]:.3f}")
        else:
            print(f"P >= {target_p}: Not reached")

if __name__ == "__main__":
    analyze_pr()
