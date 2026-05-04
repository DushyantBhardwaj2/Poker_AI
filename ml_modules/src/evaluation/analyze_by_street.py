import joblib
import pandas as pd
import numpy as np
import os
from sklearn.metrics import precision_recall_fscore_support
from src.utils.config_loader import load_config, get_data_path

def analyze_by_street():
    config = load_config()
    df = pd.read_parquet(get_data_path('labels_v3'))
    model_path = os.path.join(config['paths']['models'], 'bluff_detector_showdown_v3.joblib')
    model = joblib.load(model_path)
    
    features = [
        'street', 'rel_bet_size', 'bet_spike', 'dryness', 'dryness_delta', 
        'vpip', 'pfr', 'spr', 'bet_size_diff', 
        'is_monotonic', 'range_miss', 'dryness_bet_interaction', 
        'vpip_bet_interaction', 'tightness_bet_interaction', 'agg_profile'
    ]
    
    showdown_mask = df['true_label'].notna()
    test_df = df[showdown_mask].copy()
    X_test = test_df[features].fillna(0).replace([np.inf, -np.inf], 0)
    y_true = test_df['true_label'].astype(int)
    
    y_prob = model.predict_proba(X_test)[:, 1]
    test_df['y_prob'] = y_prob
    
    threshold = 0.4 # Reasonable threshold for analysis
    
    print(f"Overall Precision (T={threshold}): {precision_recall_fscore_support(y_true, y_prob > threshold, average='binary')[0]:.3f}")
    
    for street in [1, 2, 3]:
        s_mask = test_df['street'] == street
        if s_mask.any():
            s_y_true = y_true[s_mask]
            s_y_prob = y_prob[s_mask]
            p, r, f1, _ = precision_recall_fscore_support(s_y_true, s_y_prob > threshold, average='binary')
            print(f"Street {street}: Precision={p:.3f}, Recall={r:.3f}, Count={s_mask.sum()}")

if __name__ == "__main__":
    analyze_by_street()
