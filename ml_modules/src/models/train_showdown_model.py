import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import GroupKFold
from sklearn.metrics import precision_recall_fscore_support, precision_recall_curve, roc_auc_score
import joblib
import logging
import os
from src.utils.config_loader import load_config, get_data_path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train_showdown_model():
    logger.info("Loading labeled dataset v3 for direct showdown training...")
    config = load_config()
    labels_path = get_data_path('labels_v3')
    
    if not labels_path or not os.path.exists(labels_path):
        logger.error(f"Dataset not found at {labels_path}")
        return
        
    df = pd.read_parquet(labels_path)
    
    # Filter for showdown only
    showdown_df = df[df['true_label'].notna()].copy()
    showdown_df['true_label'] = showdown_df['true_label'].astype(int)
    
    logger.info(f"Training on {len(showdown_df)} showdown records.")
    
    features = [
        'street', 'rel_bet_size', 'bet_spike', 'dryness', 'dryness_delta', 
        'bet_bin', 'vpip', 'pfr', 'spr', 'bet_size_diff', 
        'is_monotonic', 'range_miss', 'dryness_bet_interaction', 
        'vpip_bet_interaction', 'tightness_bet_interaction', 'agg_profile'
    ]
    
    X = showdown_df[features].fillna(0).replace([np.inf, -np.inf], 0)
    y = showdown_df['true_label']
    groups = showdown_df['player_id']
    
    # Stratified split by player
    unique_players = groups.unique()
    np.random.seed(42)
    train_players = np.random.choice(unique_players, size=int(0.8 * len(unique_players)), replace=False)
    
    train_mask = groups.isin(train_players)
    X_train, X_test = X[train_mask], X[~train_mask]
    y_train, y_test = y[train_mask], y[~train_mask]
    
    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # XGBoost Classifier for direct binary prediction
    model_params = {
        'n_estimators': 1000,
        'learning_rate': 0.05,
        'max_depth': 6,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'tree_method': 'hist',
        'random_state': 42,
        'n_jobs': -1,
        'eval_metric': 'logloss'
    }
    
    model = xgb.XGBClassifier(**model_params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=100
    )
    
    # Evaluation
    y_prob = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)
    logger.info(f"ROC AUC: {auc:.3f}")
    
    # PR Calibration
    precision, recall, thresholds = precision_recall_curve(y_test, y_prob)
    target_p = 0.70
    valid_idx = np.where(precision[:-1] >= target_p)[0]
    
    if len(valid_idx) > 0:
        # Get threshold with highest recall for target precision
        # Since thresholds increase, precision generally increases.
        # We pick the FIRST threshold that hits target precision to maximize recall.
        best_threshold = thresholds[valid_idx[0]]
        p_final = precision[valid_idx[0]]
        r_final = recall[valid_idx[0]]
    else:
        # Max precision if target not reached
        best_idx = np.argmax(precision[:-1])
        best_threshold = thresholds[best_idx]
        p_final = precision[best_idx]
        r_final = recall[best_idx]
        
    logger.info(f"Best Threshold for {target_p*100}% Precision: {best_threshold:.3f}")
    logger.info(f"Final Test Performance: Precision={p_final:.3f}, Recall={r_final:.3f}")
    
    # Save Model
    model_dir = config['paths']['models']
    model_path = os.path.join(model_dir, 'bluff_detector_showdown_v3.joblib')
    joblib.dump(model, model_path)
    logger.info(f"Showdown model saved to {model_path}")
    
    # Feature Importance
    importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    logger.info(f"Top 5 Features (Showdown):\n{importance.head()}")
    
    return model

if __name__ == "__main__":
    train_showdown_model()
