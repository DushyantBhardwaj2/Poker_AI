# PokerSense ML — Dynamic Execution Plan (v2.0)

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

### 3. Dependency & Verification Enforcement
*   **Strict Blocking:** A task cannot start unless `depends_on` tasks are `done`.
*   **Verification:** Tasks marked `[BLOCKED BY VERIFICATION]` require a successful validation script run before proceeding.

### 4. Anti-Hallucination & Failure Handling
*   **No Fabrication:** Do not assume dataset fields exist. Tag unknowns with `[ASSUMPTION]` or `[NEEDS VERIFICATION]`.
*   **Failure Handling Rules:**
    *   **Parsing Failure:** If a `.phh` file is corrupt or `pokerkit` fails, log the filename to `failed_parses.log`, increment a skip counter, and continue. Do NOT crash the pipeline.
    *   **Missing Fields:** If a required field (e.g., `bet_amount`) is missing in a row, drop the specific row, not the entire hand.
    *   **Schema Mismatch:** If incoming data violates the **Data Contract (Section 2)**, the pipeline must halt and raise a `ContractViolationError`.

---

## 1. System Overview

**Data Flow:** 
Raw PHH ➡️ **[Phase 1]** Parsed Actions ➡️ **[Phase 2]** Feature Vector ➡️ **[Phase 3]** Soft Labels ➡️ **[Phase 4]** Ground Truth Validation ➡️ **[Phase 5]** Iterative Model Training ➡️ **[Phase 6]** Inference API.

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

### Phase 1: Data Pipeline Initialization
*   **Task 1.1: Environment & Parser Setup** (`status: done`)
*   **Task 1.2: Cross-File Identity Verification** (`status: done`)
*   **Task 1.3: Batch Parsing & Feature Extraction** (`status: done`)
*   **Task 1.6: Aggressive HandHQ Ingestion (.phhs)** (`status: done`)
    - [x] Processed ~74k records from 50 HandHQ files.
    - [x] Aggregated robust VPIP/PFR stats for 7,800+ players.

### Phase 1.5: Heuristic Design & Calibration
*   **Subtask: Analyze Joint Distributions** (`status: done`)
*   **Subtask: Numerical Boundary Extraction (v1)** (`status: done`)
*   **Subtask: Identify bluff-indicative patterns** (`status: done`)
*   **Subtask: Define initial heuristic components** (`status: done`)

### Phase 2: Feature Engineering
*   **Task 2.1: Opponent Profiling Aggregation** (`status: done`)
*   **Task 2.2: Board Texture & Betting Features** (`status: done`)
*   **Task 2.3: Range Density Estimation** (`status: done`)
*   **Task 2.4: Temporal Feature Dependency** (`status: done`)
*   **Task 2.5: Data Leakage Guard** (`status: done`)
*   **Task 2.6: Advanced Interaction Features (v2)** (`status: done`)

### Phase 3: Heuristic Labeling Engine
*   **Task 3.1: Construct the Weighted Scoring Labeler** (`status: done`)
*   **Task 3.2: High-Precision Threshold Calibration** (`status: done`)

### Phase 4: Ground Truth & Threshold Calibration
*   **Task 4.1: Showdown Accuracy & Calibration** (`status: done`)
    - **F1-Score achieved:** 0.63 (Threshold 0.40) on v1 dataset.

### Phase 5: Model Training & Iterative Improvement
*   **Task 5.1: XGBoost Pipeline & Experiment Tracking** (`status: done`)
    - **Average R2:** 0.997
    - **Top Features:** street (76%), rel_bet_size (13%), dryness (4.4%)
*   **Task 5.2: Deep Model Refinement (v2)** (`status: in-progress`)
    - [ ] Train with Max Depth 10 and Learning Rate 0.01 on 74k+ records.
    - [ ] Optimize for >70% Precision using PR-Curve on showdown-validated data.

### Phase 6: Inference System
*   **Task 6.1: FastAPI / Predictor Service** (`status: pending`)
    - [ ] Create `inference_api.py`.
    - [ ] Implement `predict_bluff` endpoint.
    - [ ] Add request/response validation matching Data Contract 2.1.
