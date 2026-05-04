# 🛠️ ML Module Technical Guide

This document outlines the implementation details and development workflow for the PokerSense Bluff Detection ML module.

## File Map

```text
ML modules/
├── data/               # Raw Zenodo dataset (extracted from poker-hand-histories.zip)
├── models/             # Exported .joblib model files
├── data_loader.py      # PHH (Poker Hand History) parser and filter
├── feature_factory.py  # Behavioral feature engineering (Pandas)
├── labeler.py          # Heuristic engine (Range-based estimation)
├── trainer.py          # XGBoost training and validation loop
└── predictor.py        # Inference service for the FastAPI backend
```

## Development Workflow

### 1. Data Preparation
Extract the Zenodo database and run the PHH loader to filter for NLHE hands:
```bash
python data_loader.py --input ./data/poker-hand-histories.zip --variant nlhe
```

### 2. Feature Engineering & Labeling
Transform raw actions into ML features and generate probabilistic labels:
```bash
python labeler.py --input ./processed_hands.parquet --output ./training_set.csv
```

### 3. Model Training
Train the XGBoost classifier and evaluate feature importance:
```bash
python trainer.py --data ./training_set.csv --out ./models/bluff_v1.joblib
```

## Implementation Standards

- **Imperfect Information**: The `predictor.py` service must NEVER access hidden card data during inference. It only operates on public board state and betting history.
- **Interpretability**: All predictions must include a "Feature Importance" breakdown to allow the backend to generate human-readable reasons for a bluff prediction.
- **Probabilistic Output**: The model must return `predict_proba()` values to represent the inherent uncertainty of poker.

## Core Heuristics (labeler.py)

- **Rule: Narrative Mismatch**: If `bet_size > pot_size` AND `board_texture == 'dry'`, increase bluff probability.
- **Rule: Range Exhaustion**: If `opponent_vpip > 0.60` AND `round == 'river'`, increase bluff probability (mathematical exhaustion of value hands).
- **Rule: Bet Spike**: Sudden 3x+ increase in bet size relative to previous streets.
