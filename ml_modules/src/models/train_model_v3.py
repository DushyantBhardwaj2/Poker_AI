import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_squared_error, r2_score, precision_recall_fscore_support, precision_recall_curve
import joblib
import logging
import matplotlib.pyplot as plt
import os
from src.utils.config_loader import load_config, get_data_path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train_model_v3():
    logger.info("Loading labeled dataset v3...")
    config = load_config()
    labels_v3_path = get_data_path('labels_v3')
    
    if not labels_v3_path or not os.path.exists(labels_v3_path):
        logger.error(f"Labeled dataset v3 not found at {labels_v3_path}")
        return
        
    df = pd.read_parquet(labels_v3_path)
    
    # Define features and target
    # All numerical/boolean features from v3
    features = [
        'street', 'rel_bet_size', 'bet_spike', 'dryness', 'dryness_delta', 
        'bet_bin', 'vpip', 'pfr', 'spr', 'bet_size_diff', 
        'is_monotonic', 'range_miss', 'dryness_bet_interaction', 
        'vpip_bet_interaction', 'tightness_bet_interaction', 'agg_profile'
    ]
    
    # Ensure all features exist
    available_features = [f for f in features if f in df.columns]
    missing_features = set(features) - set(available_features)
    if missing_features:
        logger.warning(f"Missing features in dataset: {missing_features}")
    
    target = 'soft_label'
    weight = 'confidence_weight'
    
    X = df[available_features]
    y = df[target]
    w = df[weight] if weight in df.columns else np.ones(len(df))
    groups = df['player_id']
    
    logger.info("Cleaning inf and nan values for training...")
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(0)
    
    logger.info(f"Training on {len(df)} records with {len(available_features)} features.")
    
    # Model Params optimized for depth and precision
    model_params = config.get('model', {}).get('params', {
        'n_estimators': 500, # Reduced for speed on 5.8M records, max_depth is high
        'learning_rate': 0.05,
        'max_depth': 10,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'tree_method': 'hist',
        'device': 'cpu', # Use 'cuda' if GPU available
        'n_jobs': -1,
        'random_state': 42
    })
    
    # On 5.8M records, GroupKFold might be very slow. 
    # Let's do a single stratified-by-player split for validation if the dataset is huge.
    if len(df) > 1000000:
        logger.info("Large dataset detected. Using single validation split for speed.")
        unique_players = groups.unique()
        np.random.seed(42)
        train_players = np.random.choice(unique_players, size=int(0.8 * len(unique_players)), replace=False)
        
        train_mask = groups.isin(train_players)
        X_train, X_val = X[train_mask], X[~train_mask]
        y_train, y_val = y[train_mask], y[~train_mask]
        w_train, w_val = w[train_mask], w[~train_mask]
        
        model = xgb.XGBRegressor(**model_params)
        model.fit(
            X_train, y_train, 
            sample_weight=w_train, 
            eval_set=[(X_val, y_val)], 
            sample_weight_eval_set=[w_val],
            verbose=50
        )
        final_model = model
    else:
        # Standard cross-validation for smaller datasets
        gkf = GroupKFold(n_splits=3)
        for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups), 1):
            logger.info(f"Training Fold {fold}...")
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            w_train, w_val = w.iloc[train_idx], w.iloc[val_idx]
            
            model = xgb.XGBRegressor(**model_params)
            model.fit(
                X_train, y_train, 
                sample_weight=w_train, 
                eval_set=[(X_val, y_val)], 
                sample_weight_eval_set=[w_val],
                verbose=100
            )
            final_model = model # Just keep the last one for now, or ensemble
            break # Just one fold for speed in this iteration
            
    # Save model
    model_output_path = os.path.join(config['paths']['models'], 'bluff_detector_v3.joblib')
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(final_model, model_output_path)
    logger.info(f"Model saved to {model_output_path}")
    
    # Feature Importance
    importance = pd.DataFrame({
        'feature': available_features,
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    importance_path = os.path.join(config['paths']['processed_data'], 'feature_importance_v3.csv')
    importance.to_csv(importance_path, index=False)
    logger.info(f"Top 5 Features:\n{importance.head()}")
    
    # Precision-Recall Optimization on Showdown Data
    showdown_mask = df['true_label'].notna()
    if showdown_mask.any():
        logger.info(f"Calibrating on {showdown_mask.sum()} showdown records...")
        X_test = X[showdown_mask]
        y_true = df.loc[showdown_mask, 'true_label'].astype(int)
        
        y_prob = final_model.predict(X_test)
        
        # Calculate PR curve
        precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
        
        # Find threshold for > 70% precision
        target_precision = config['training'].get('target_precision', 0.70)
        idx = np.where(precision[:-1] >= target_precision)[0]
        
        if len(idx) > 0:
            # We want the highest recall at this precision
            best_idx = idx[0] # First threshold that hits target precision
            best_threshold = thresholds[best_idx]
            logger.info(f"Target {target_precision*100}% precision hit at threshold {best_threshold:.3f}")
        else:
            best_threshold = thresholds[np.argmax(precision[:-1])]
            logger.info(f"Max precision achieved: {np.max(precision[:-1]):.3f} (did not reach {target_precision*100}%)")
            
        # Final metrics at chosen threshold
        y_pred = (y_prob >= best_threshold).astype(int)
        p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
        logger.info(f"\nFinal Showdown Performance (Threshold {best_threshold:.3f}):")
        logger.info(f"Precision: {p:.3f}, Recall: {r:.3f}, F1: {f1:.3f}")
        
        # Save Calibration Data
        calibration = {
            'threshold': float(best_threshold),
            'precision': float(p),
            'recall': float(r),
            'f1': float(f1),
            'version': 'v3'
        }
        cal_path = os.path.join(config['paths']['models'], 'model_calibration_v3.joblib')
        joblib.dump(calibration, cal_path)
        
    return final_model

if __name__ == "__main__":
    train_model_v3()
