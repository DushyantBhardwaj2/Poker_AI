# 🤖 PokerSense ML — Bluff Detection Module

This module is the "behavioral brain" of PokerSense AI. It focuses on detecting bluffing behavior by identifying inconsistencies between betting patterns, board texture, and player history.

## 🛠 Execution & Planning
Development follows a **Production-Grade Dynamic Execution System** defined in `PLAN.md`.
- **Atomic Tasks**: All work is broken into <60 min subtasks.
- **Logging & Tracking**: Every completed task is logged in `DEVELOPMENT_LOG.md`. Model training sessions include comprehensive experiment tracking (versioning, params, metrics).
- **Data Contracts**: Strict schemas are enforced between parsing, feature engineering, and training stages.
- **Validation**: Heuristic soft-labels are validated against ground-truth showdown data before model training.
- **Dependencies**: Tasks are strictly blocked by their `depends_on` requirements and `[BLOCKED BY VERIFICATION]` markers.

## 1. Methodology: Probabilistic Weak Supervision (v2.0)

Since real-world poker data lacks explicit "bluff" labels, this module uses a **Hybrid Heuristic-ML approach**:

1.  **Data Source**: Training relies on the **Zenodo Poker Hand Histories Dataset (2009-2023)**. We leverage a massive dataset expansion (integrating `.phhs` HandHQ files) to provide over 100k+ aggressive action records for deep learning.
2.  **Heuristic Engine**: Generates **Probabilistic Labels** (0.0 to 1.0) using a weighted scoring system calibrated against data-derived boundary surfaces.
3.  **Hand Strength Proxy**: Uses **3D Range Modeling**. It calculates the mathematical probability that an opponent's range "missed" the board based on position, board texture, and **narrative consistency**.
4.  **High-Precision ML**: Uses **XGBoost Regressor** with a depth of 10 and PR-curve optimization to achieve >70% precision for bluff detection on showdown-validated data.

## 2. Feature Set (v2.0)

The module analyzes expanded data streams:

*   **Betting Narrative**: Bet-to-pot ratios, bet spikes, relative bet size changes, and narrative consistency (monotonicity).
*   **Opponent Profiling**: Robust VPIP, PFR, and Aggression Factor (agg_profile) aggregated from 100k+ hand histories.
*   **Board Texture**: Advanced dryness analysis and its interaction with betting patterns.
*   **Deep Insights**: Interaction terms between board texture, betting narrative, and opponent profiles to capture non-linear behavioral cues.

## 3. Tech Stack

| Component | Technology |
|-----------|------------|
| Core Engine | XGBoost (Gradient Boosting) |
| Data Processing | Pandas, NumPy |
| Preprocessing | Scikit-Learn |
| Serialization | Joblib |
| Environment | Python 3.12+ |

## 4. Training Roadmap

1.  **Phase 1: Ingestion**: Parse Zenodo PHH files and filter for NLHE hands. Currently scaled to 70k+ records using HandHQ expansion.
2.  **Phase 2: Labeling**: Apply the range-based heuristic engine to generate soft targets with confidence weighting.
3.  **Phase 3: Optimization**: Train XGBoost to minimize Log-Loss between behavioral features and heuristic labels.
4.  **Phase 5: Calibration**: Validate predictions against known showdown outcomes in the test set and optimize decision thresholds for >70% precision.
