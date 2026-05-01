import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_squared_error, r2_score, precision_recall_fscore_support, precision_recall_curve
import joblib
import logging
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_model_v2():
    logger.info("Loading labeled dataset v2...")
    # We will use the aggressive dataset if it exists, otherwise fallback to v1
    import os
    if os.path.exists('parsed_output/labeled_dataset_v2.parquet'):
        df = pd.read_parquet('parsed_output/labeled_dataset_v2.parquet')
    else:
        logger.warning("labeled_dataset_v2.parquet not found. Using v1.")
        df = pd.read_parquet('parsed_output/labeled_dataset_v1.parquet')
    
    # Define features and target
    features = [
        'street', 'rel_bet_size', 'bet_spike', 'dryness',
        'vpip', 'pfr', 'spr', 'bet_size_diff', 'is_monotonic', 'range_miss',
        'dryness_bet_interaction', 'vpip_bet_interaction', 'agg_profile'
    ]
    # Ensure all features exist (handle fallback)
    features = [f for f in features if f in df.columns]
    
    target = 'soft_label'
    weight = 'confidence_weight'
    
    X = df[features]
    y = df[target]
    w = df[weight]
    groups = df['player_id']
    
    logger.info("Cleaning inf and nan values...")
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(0)
    
    logger.info(f"Training on {len(df)} records with {len(features)} features.")
    
    # Initialize GroupKFold
    gkf = GroupKFold(n_splits=5)
    
    best_models = []
    
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups), 1):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        w_train, w_val = w.iloc[train_idx], w.iloc[val_idx]
        
        # High Depth, Low Learning Rate
        model = xgb.XGBRegressor(
            n_estimators=1000,
            learning_rate=0.01,
            max_depth=10,
            subsample=0.8,
            colsample_bytree=0.8,
            tree_method='hist', # Faster
            n_jobs=-1,
            random_state=42
        )
        
        model.fit(
            X_train, y_train, 
            sample_weight=w_train, 
            eval_set=[(X_val, y_val)], 
            sample_weight_eval_set=[w_val],
            verbose=100
        )
        
        best_models.append(model)
        
    # Final model on full data
    final_model = xgb.XGBRegressor(
        n_estimators=1000,
        learning_rate=0.01,
        max_depth=10,
        subsample=0.8,
        colsample_bytree=0.8,
        tree_method='hist',
        n_jobs=-1,
        random_state=42
    )
    final_model.fit(X, y, sample_weight=w)
    
    # Save model
    model_path = 'parsed_output/bluff_detector_v2.joblib'
    joblib.dump(final_model, model_path)
    logger.info(f"Model saved to {model_path}")
    
    # Precision-Recall Optimization on Showdown Data
    showdown_mask = df['true_label'].notna()
    if showdown_mask.any():
        X_test = df.loc[showdown_mask, features]
        X_test = X_test.replace([np.inf, -np.inf], np.nan).fillna(0)
        y_true = df.loc[showdown_mask, 'true_label'].astype(int)
        
        y_prob = final_model.predict(X_test)
        
        # Calculate PR curve
        precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
        
        # Find threshold for > 70% precision if possible
        # Note: precision and recall are size N+1, thresholds is size N.
        # The last precision value is 1.0 and has no corresponding threshold.
        target_precision = 0.70
        idx = np.where(precision[:-1] >= target_precision)[0]
        if len(idx) > 0:
            best_threshold = thresholds[idx[0]]
            logger.info(f"Best threshold for {target_precision*100}% precision: {best_threshold:.3f}")
        else:
            best_threshold = thresholds[np.argmax(precision[:-1])]
            logger.info(f"Max precision achieved: {np.max(precision[:-1]):.3f} at threshold {best_threshold:.3f}")
            
        # Final metrics at chosen threshold
        y_pred = (y_prob > best_threshold).astype(int)
        p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
        logger.info(f"\nFinal Showdown Performance (Threshold {best_threshold:.3f}):")
        logger.info(f"Precision: {p:.3f}, Recall: {r:.3f}, F1: {f1:.3f}")
        
    return final_model

if __name__ == "__main__":
    train_model_v2()
