# 🤖 PokerSense ML — Refined Execution Plan (v3.0)

## 1. EXECUTIVE SUMMARY
PokerSense ML is the **behavioral intelligence engine** of the PokerSense AI project. It specializes in **Bluff Detection** by analyzing inconsistencies between betting narratives, board textures, and player historical profiles.

**Current Stage:** The system has successfully transitioned from experimental scripts to a modular directory structure. Core logic for features, labeling, and models is implemented. We are currently in the **Pipeline Integration Phase**, focusing on unifying disparate steps into a single, automated execution flow to ensure reproducibility and high-precision results (>70%).

---

## 2. SYSTEM ARCHITECTURE

The ML system operates as an independent engine that consumes raw Hand Histories (PHH) and produces a serialized XGBoost model for the `apps/api` layer.

### Data Flow Overview (Textual)
`Raw PHH (Zenodo/HandHQ)` ➡️ **[Ingestion]** ➡️ `Parsed Actions (Parquet)` ⬅️ **[Profiling]** ⬅️ `Player Stats (VPIP/PFR)` ➡️ **[Features]** ➡️ `Feature Matrix (Temporal/Interactive)` ➡️ **[Labeling]** ➡️ `Heuristic Soft Labels + Confidence` ➡️ **[Training]** ➡️ `XGBoost Regressor` ➡️ **[Evaluation]** ➡️ `PR-Calibrated Model`.

---

## 3. PIPELINE DESIGN (STRICT ORDER)

The pipeline is managed via `pipeline/run_pipeline.py` and driven by `configs/pipeline_config.json`.

| Step | Module | Purpose | Input ➡️ Output |
| :--- | :--- | :--- | :--- |
| **1. Ingestion** | `parsers/` | Recursive discovery and NLHE filtering. | `*.phh/*.phhs` ➡️ `parsed_hands_full.parquet` |
| **2. Profiling** | `features/` | Calculate lifetime VPIP/PFR/Aggression. | `parsed_hands_full` ➡️ `player_stats.parquet` |
| **3. Features** | `features/` | Narrative, Texture, and Interaction terms. | `parsed_hands` + `stats` ➡️ `features_v2.parquet` |
| **4. Labeling** | `labeling/` | Probabilistic Weak Supervision (Heuristics). | `features_v2` ➡️ `labeled_dataset_v2.parquet` |
| **5. Training** | `models/` | XGBoost training with confidence weights. | `labeled_dataset_v2` ➡️ `bluff_detector_v2.joblib` |
| **6. Evaluation**| `evaluation/`| PR-Curve calibration on showdown data. | `detector_v2` + `showdown` ➡️ `Performance Report` |
| **7. Inference** | `interfaces/`| Expose prediction as a lightweight service. | `Game State` ➡️ `Bluff Probability (%)` |

---

## 4. MODULE STRUCTURE

*   **`preprocessing/`**: Handles data cleaning, stratified sampling, and identity verification.
*   **`parsers/`**: Core ingestion logic using `pokerkit`. Translates diverse PHH dialects into a unified schema.
*   **`features/`**: Domain-specific logic (Board Dryness, SPR, Bet Spikes, Narrative Monotonicity).
*   **`labeling/`**: The "Heuristic Engine". Assigns soft labels (0-1) based on mismatch between action and hand range probability.
*   **`models/`**: Wrapper for XGBoost. Handles hyper-parameters and experiment tracking via JSON logs.
*   **`evaluation/`**: Statistical validation. Anchors the heuristic logic to real-world showdown outcomes.
*   **`pipeline/`**: The orchestrator. Ensures correct step sequencing and path management.

---

## 5. CURRENT STATUS VS PLAN

| Task | Category | Planned Status | Actual Status | Note |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0** | Infrastructure | `done` | `done` | Modular structure and config loader implemented. |
| **Phase 1** | Ingestion | `done` | `done` | Integrated into `run_pipeline.py`. |
| **Phase 2** | Features | `done` | `done` | v2 features (SPR, Interaction terms) implemented. |
| **Phase 3** | Labeling | `done` | `done` | Heuristic engine v2 implemented with soft-labels. |
| **Phase 4** | Evaluation | `done` | `done` | Integrated into pipeline and model training. |
| **Phase 5** | Training | `in-progress` | `in-progress` | Training on 74k records; Precision optimization pending. |
| **Phase 6** | Inference | `pending` | `pending` | Blocked by Phase 5 completion. |

---

## 6. IDENTIFIED GAPS (CRITICAL)

1.  **Pipeline Fragmentation:** Steps 1 (Ingestion) and 2 (Profiling) are currently manual scripts (`aggressive_parser.py`, `calculate_player_stats.py`) and not part of the main `run_pipeline.py` flow.
2.  **Hardcoded Path Leakage:** Some scripts still use relative strings (e.g., `"./data/raw"`) instead of the centralized `config_loader`.
3.  **Missing Automated Gating:** The pipeline continues even if Data Quality checks (Phase 4.2) fail.
4.  **Static Mismatch Surface:** The heuristic labeler relies on a manual `mismatch_surface_v1.csv` which should be dynamically generated from the current dataset's showdown distributions.

---

## 7. REFINED ROADMAP (ACTIONABLE)

### Phase A: Pipeline Consolidation (Short-term)
*   [x] **A.1:** Refactor `run_pipeline.py` to include `ingest` and `profile` steps.
*   [x] **A.2:** Enforce `config_loader` across all modules to eliminate hardcoded paths.
*   [x] **A.3:** Implement a "Dry Run" check that verifies all input file dependencies before execution.

### Phase B: Quality & Calibration (Mid-term)
*   [x] **B.1:** Integrate `validate_data_quality.py` as a mandatory gate after Ingestion.
*   [x] **B.2:** Automate the "Joint Distribution Analysis" to generate the `mismatch_surface` dynamically before Labeling.
*   [ ] **B.3:** Scale `AggressiveParser` to 200k+ records to maximize behavioral depth.

### Phase C: Model Optimization & Delivery (Final)
*   [ ] **C.1:** Execute full PR-curve calibration to hit the **>70% Precision** target for "Strict Bluffs".
*   [ ] **C.2:** Create the `inference_api.py` wrapper.
*   [ ] **C.3:** Archive all legacy "v1" scripts into the `archive/` folder to clean the codebase.

---

## 8. SAFE IMPROVEMENTS (NO DEVIATION)

*   **Validation Gating:** Add a check in `run_pipeline.py` that aborts if the `showdown_correlation` drops below a defined threshold (e.g., 0.50).
*   **Smart Rerunning:** Implement a lightweight "stale check" (checking file timestamps) so the pipeline only reruns steps if inputs have changed.
*   **Standardized Logging:** Shift all `print` statements to a structured `logging` system that writes to both stdout and a `pipeline_run.log`.
*   **Feature Importance Export:** Automatically export a `feature_importance.png` and CSV during the Training step to maintain observability.

---

## 9. SYSTEM RULES & WORKFLOWS

### 1. Dynamic Task Expansion & Evolution
*   **Expansion:** Any task taking longer than 60 minutes or containing hidden complexity MUST be broken down into smaller subtasks.
*   **Plan Evolution:** Update this `PLAN.md` file immediately when architecture changes or assumptions are invalidated.
*   **State Tracking:** Keep all `status` fields strictly updated (`[ ]` ➡️ `[/]` ➡️ `[x]`).

### 2. Execution Logging & Experiment Tracking
*   **Mandatory Logging:** Upon completion of *any* task, a corresponding entry MUST be written to `DEVELOPMENT_LOG.md`.
*   **Experiment Tracking Layer:** For every model training run, the log entry MUST include:
    *   `dataset_version`: Timestamp/Hash of the training CSV.
    *   `feature_version`: List of active features used.
    *   `parameters`: XGBoost hyper-parameters.
    *   `metrics`: LogLoss, MSE, and PR-AUC.
