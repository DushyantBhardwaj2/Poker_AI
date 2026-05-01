# PokerSense ML — Dynamic Execution Plan (v2.1)

This is a **production-grade execution system**. It is designed to be executed step-by-step by an AI agent, dynamically expand as complexity is uncovered, and maintain strict synchronization with `DEVELOPMENT_LOG.md`.

---

## 🔄 System Rules & Workflows

### 1. Dynamic Task Expansion & Evolution
*   **Expansion:** Any task taking longer than 60 minutes or containing hidden complexity MUST be broken down into smaller subtasks.
*   **Plan Evolution:** Update this `PLAN.md` file immediately when architecture changes or assumptions are invalidated.
*   **State Tracking:** Keep all `status` fields strictly updated (`pending` ➡️ `in-progress` ➡️ `done`).

### 2. Execution Logging & Experiment Tracking
*   **Mandatory Logging:** Upon completion of *any* task, a corresponding entry MUST be written to `DEVELOPMENT_LOG.md`.
*   **Experiment Tracking Layer:** For every model training run (Phase 5), the log entry MUST include:
    *   `dataset_version`: Timestamp/Hash of the training CSV.
    *   `feature_version`: List of active features used.
    *   `parameters`: XGBoost hyper-parameters.
    *   `metrics`: LogLoss, MSE, and Ground-Truth Accuracy (from Phase 4).

---

## 1. System Overview

**Modular Architecture:**
- `configs/`: Centralized JSON pipeline & model configurations.
- `data/`: Raw, interim (parsed), and processed (featured/labeled) data.
- `src/`: Core logic modules (parsers, features, labeling, models, evaluation).
- `pipeline/`: Unified entry point (`run_pipeline.py`).
- `tests/`: Automated validation suite.

**Data Flow:** 
Raw PHH (`data/raw`) ➡️ **[Phase 1: Parsers]** Parsed Actions (`data/interim`) ➡️ **[Phase 2: Features]** Feature Vector (`data/interim`) ➡️ **[Phase 3: Labeling]** Soft Labels (`data/processed`) ➡️ **[Phase 4: Evaluation]** Ground Truth Validation ➡️ **[Phase 5: Models]** Iterative Training ➡️ **[Phase 6: Inference]** API.

---

## 2. Data Contract Layer (Schemas)

### 2.1 Parsed Data Schema (Intermediate Parquet)
| Field | Type | Description |
| :--- | :--- | :--- |
| `hand_id` | String | Unique identifier (Filename + Hand Index) |
| `player_id` | String | Verified consistent identity |
| `street` | Int | 0:Pre, 1:Flop, 2:Turn, 3:River |
| `pot_before` | Float | Total chips in pot before the current action |
| `bet_amount` | Float | The value of the current aggressive action |
| `board_cards` | List[Str] | Public cards on the table (max 5) |
| `is_showdown` | Boolean | True if hand reached showdown |
| `hole_cards` | List[Str] | Revealed cards (if is_showdown=True), else Empty |

---

## 3. Execution Plan

### Phase 0: Production-Grade Restructuring
*   **Task 0.1: Modular Directory Setup** (`status: done`)
    - [x] Create `src/`, `configs/`, `data/`, `pipeline/` hierarchy.
*   **Task 0.2: Centralized Configuration** (`status: done`)
    - [x] Implement `pipeline_config.json` and `src/utils/config_loader.py`.
*   **Task 0.3: Modular Code Relocation** (`status: done`)
    - [x] Move scripts to functional modules and update absolute imports.
*   **Task 0.4: Unified Pipeline Entry** (`status: done`)
    - [x] Create `pipeline/run_pipeline.py` for atomic execution.

### Phase 1: Data Pipeline Initialization
*   **Task 1.1: Environment & Parser Setup** (`status: done`)
*   **Task 1.2: Cross-File Identity Verification** (`status: done`)
*   **Task 1.3: Batch Parsing & Feature Extraction** (`status: done`)
    - [x] Refactored into `src/parsers/batch_parser.py`.
*   **Task 1.6: Aggressive HandHQ Ingestion (.phhs)** (`status: done`)
    - [x] Scaled ingestion to 74k+ records in `data/interim`.

### Phase 1.5: Heuristic Design & Calibration
*   **Subtask: Analyze Joint Distributions** (`status: done`)
*   **Subtask: Numerical Boundary Extraction (v1)** (`status: done`)
*   **Subtask: Identify bluff-indicative patterns** (`status: done`)
*   **Subtask: Define initial heuristic components** (`status: done`)

### Phase 2: Feature Engineering (v2)
*   **Task 2.1: Opponent Profiling Aggregation** (`status: done`)
*   **Task 2.2: Board Texture & Betting Features** (`status: done`)
    - [x] Implemented in `src/features/engineer_features_v2.py`.
*   **Task 2.3: Range Density Estimation** (`status: done`)
*   **Task 2.4: Temporal Feature Dependency** (`status: done`)
*   **Task 2.5: Data Leakage Guard** (`status: done`)
*   **Task 2.6: Advanced Interaction Features (v2)** (`status: done`)

### Phase 3: Heuristic Labeling Engine (v2)
*   **Task 3.1: Construct Weighted Scoring Labeler** (`status: done`)
    - [x] Implemented in `src/labeling/heuristic_labeler_v2.py`.
*   **Task 3.2: High-Precision Threshold Calibration** (`status: done`)

### Phase 4: Ground Truth & Evaluation
*   **Task 4.1: Showdown Accuracy & Calibration** (`status: done`)
    - [x] Core eval logic moved to `src/evaluation/`.
*   **Task 4.2: Data Quality Verification** (`status: done`)
    - [x] Implemented `src/evaluation/check_data_stats.py`.

### Phase 5: Model Training & Iterative Improvement
*   **Task 5.1: XGBoost Pipeline & Experiment Tracking** (`status: done`)
*   **Task 5.2: Deep Model Refinement (v2)** (`status: in-progress`)
    - [x] Refactored `src/models/train_model_v2.py` with modular config.
    - [ ] Execute `train_model_v2` on 74k+ records via pipeline.
    - [ ] Verify >70% Precision target.

### Phase 6: Inference System
*   **Task 6.1: FastAPI / Predictor Service** (`status: pending`)
    - [ ] Create `src/interfaces/inference_api.py`.
    - [ ] Implement `predict_bluff` endpoint.
