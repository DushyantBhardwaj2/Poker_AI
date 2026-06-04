# Project Deep Dive: PokerSense ML — Behavioral Bluff Detection

## 1. Project Overview
I built **PokerSense ML**, a behavioral intelligence engine designed to detect bluffs in No-Limit Texas Hold'em (NLHE). Unlike traditional poker bots that focus on Game Theory Optimal (GTO) play, this module acts as a "behavioral observer." It identifies when an opponent's betting narrative (the "story" they are telling with their chips) is inconsistent with the mathematical reality of the board texture and their historical tendencies.

*   **Objective:** Achieve >70% precision in real-time bluff detection to provide actionable alerts for a human player.
*   **Final Performance:** 71.1% Precision on the Turn, 93.2% Precision on the River.
*   **Key Innovation:** Pivoted from weak supervision (heuristic-based) to direct training on 615,000 ground-truth showdown records discovered during dataset scaling.

---

## 2. Technical Architecture (Data Pipeline)
The engine is built as a modular pipeline to ensure reproducibility and handle massive datasets (scaling from 18k to 5.8M records).

1.  **Ingestion:** Recursive discovery of `.phh` and `.phhs` files. Filters for NLHE (`variant == "NT"`).
2.  **Profiling:** Aggregates lifetime statistics (VPIP, PFR, Aggression Factor) for every unique player identity across the entire dataset.
3.  **Feature Engineering:** Transforms raw action sequences into 25+ behavioral and narrative features.
4.  **Labeling:**
    *   *Initial:* Weak Supervision using a "Heuristic Engine" to generate soft labels.
    *   *Final:* Binary labeling based on revealed showdown cards (Ground Truth).
5.  **Training:** XGBoost Classifier with custom sample weights and PR-curve calibration.
6.  **Inference:** Lightweight API delivering a `bluff_probability (%)` and a "Strict Bluff" flag based on street-wise thresholds.

---

## 3. Features & Engineering Decisions
I designed features to capture the "narrative" of a poker hand rather than just raw numbers:

*   **`rel_bet_size` (Relative Bet Size):** `bet_amount / pot_before`. Normalizes aggression across different pot sizes.
*   **`bet_spike`:** The delta between the current `rel_bet_size` and the previous street's. A sudden "spike" in aggression often signals a polarized range (strongest hands or total bluffs).
*   **`dryness` & `dryness_delta`:** Measures board texture. A "dry" board (e.g., 7-2-2) offers few natural draws, making large bets more suspicious (Narrative Mismatch).
*   **`tightness_bet_interaction`:** Calculated as `(1 - VPIP) * rel_bet_size`. This distinguishes between a "Maniac" (high VPIP) and a "Rock" (low VPIP). A large bet from a "Rock" on a dry board is a much higher signal than from a "Maniac."
*   **`range_miss`:** A heuristic proxy calculating the probability that a standard opening range failed to connect with the current board texture.
*   **`is_monotonic`:** Checks if the betting sequence is consistently increasing. Deviations (e.g., small bet, small bet, massive overbet) are flagged as "Narrative Breaks."

---

## 4. Problems Faced & Solutions

### A. The "Hidden" Dataset Scaling Problem
**Challenge:** Initial training on 18,000 Zenodo records yielded poor results because the heuristic labels were "echoing" my own assumptions rather than learning from data.
**Solution:** I discovered and integrated the **HandHQ (.phhs)** dataset, scaling the ingestion to **5.8 million records**. This massive scale revealed 615,000 "Showdown" records where the actual cards were known, allowing me to abandon weak supervision in favor of direct ground-truth training.

### B. Parser API Volatility
**Challenge:** The `pokerkit` library underwent an API change where the `.states` attribute was deprecated in favor of a `.state_actions` generator. This broke my entire ingestion pipeline.
**Solution:** I refactored the `PHHParser` to use a generator-based iterator, significantly reducing memory overhead (critical for processing 5.8M records) and ensuring future-proof compatibility with the library.

### C. Hand ID Collisions
**Challenge:** When merging multiple dataset sources (ACPC, WSOP, HandHQ), identical `hand_id` values caused data corruption.
**Solution:** I implemented a "Source-Aware ID" system that salts the `hand_id` with a hash of the relative file path, ensuring global uniqueness across 10,000+ files.

---

## 5. How the Model Works (The Logic Layer)
The engine doesn't just look at a single bet; it evaluates the **Temporal Action Sequence**.

1.  **Input Vectorization:** The system takes the current game state (Pot, Board, Player Stats, Action History) and vectorizes it into a feature row.
2.  **XGBoost Inference:** We use a tree-based ensemble. The model's "logic" is encoded in thousands of decision paths. For example:
    *   *Path A:* If `street == River` AND `rel_bet_size > 1.5` AND `board_dryness > 0.8` AND `player_vpip < 0.2` -> **High Bluff Probability**. (This captures a "tight" player trying to buy a pot on a board they likely missed).
    *   *Path B:* If `dryness_delta` is negative (board got wetter) AND `bet_spike` is low -> **Low Bluff Probability**. (This suggests a player naturally continuing their aggression as the board improved).
3.  **PR-Curve Gating:** The raw probability is passed through a street-specific threshold. If `P(Bluff) > Threshold_Street`, a "Strict Bluff" flag is raised.
4.  **Confidence Weighting:** The distance from the threshold determines the confidence level displayed in the UI.

---

## 6. Results & Performance Metrics
The model was evaluated against a held-out test set of **123,000 showdown records**.

| Metric | Value | Technical Significance |
| :--- | :--- | :--- |
| **ROC AUC** | **0.750** | Strong ability to distinguish between bluffs and value bets. |
| **PR AUC** | **0.620** | High performance in the "imbalanced" class (bluffs are rare). |
| **Log-Loss** | **0.312** | Predictions are well-calibrated (probabilities represent real frequencies). |
| **River Precision**| **93.2%** | Only 7% false alarms on the most expensive street. |
| **Turn Precision** | **71.1%** | Reliable enough for tactical decision-making. |
| **Inference Latency**| **~12ms** | Suitable for real-time live-tracking environments. |

---

## 7. Files Created
*   `aggressive_parser.py`: High-performance ingestion for .phhs files (processes ~5,000 hands/sec).
*   `engineer_features_v3.py`: Implementation of narrative interaction terms and SPR.
*   `calculate_player_stats_aggressive.py`: Distributed statistical aggregation using Pandas chunking.
*   `generate_mismatch_surface.py`: Dynamic analysis of board-texture/bet-size distributions.
*   `train_showdown_model.py`: The final training script for the v3 model with PR-optimization.
*   `inference_api.py`: The production wrapper for the backend with threshold gating.

---

## 8. Limitations & Future Work (v4.0)
*   **Limited Multi-Way Data:** Optimized for "Heads-Up" (1v1) pots. Multi-way dynamics (3+ players) are currently a fallback to a simplified heuristic.
*   **Temporal Drift:** Doesn't yet account for "Tilt" (a player becoming aggressive after a big loss).
*   **Future Work:** Implementation of **LSTM (Long Short-Term Memory)** networks to capture the exact order and timing of actions (seconds-to-act), which is a massive tell in online poker.

---

## 9. Deep Interview Prep (Mastering the "Why")

### Q1: "Why did you use XGBoost instead of a Deep Learning approach like a Transformer?"
**Answer:** "Two main reasons: **Data Type** and **Interpretability**. Poker features are heterogeneous—you have continuous variables (bet sizes), discrete variables (street), and historical ratios (VPIP). Tree-based models like XGBoost handle these different scales natively without needing complex normalization. Secondly, in a high-stakes application like poker, the 'Why' matters. I used **SHAP values** to verify that the model was learning actual poker theory (like the correlation between dry boards and bluffs) rather than just noise in the data. A black-box Transformer would have been much harder to audit for 'hallucinated' strategies."

### Q2: "How did you handle the fact that players have different styles? Doesn't a 'Maniac' bluff more than a 'Nit'?"
**Answer:** "I solved this through **Feature Interaction**. I didn't just give the model the `bet_size`; I gave it the interaction term `tightness_bet_interaction`, which is `(1 - VPIP) * bet_size`. This mathematically anchors the bet to the player's profile. A 100bb bet from a 15% VPIP player (a Nit) is weighted differently by the decision trees than the same bet from a 60% VPIP player. The model essentially learns 'Style-Relative Aggression' rather than 'Absolute Aggression'."

### Q3: "Explain your PR-Curve Calibration. Why is precision more important than recall here?"
**Answer:** "In a live poker advisor, a **False Positive** (calling a bluff that was actually a strong hand) is much more expensive than a **False Negative** (folding when the opponent was actually bluffing). If the AI tells a user 'He's bluffing!' and it's wrong, the user loses their entire stack. Therefore, I optimized for **Precision at a fixed Recall**. I moved the decision threshold up until I hit >90% precision on the River. I'd rather the AI stay silent on 50% of bluffs but be 93% certain on the ones it *does* flag."

### Q4: "You mentioned 615,000 showdown records. How did you ensure this data wasn't biased? (e.g., only bad players go to showdown)"
**Answer:** "That's a classic **Selection Bias** problem in poker data. To mitigate this, I used **Sample Weighting**. I weighted showdown records from high-stakes, professional datasets (like the Pluribus and ACPC bots) more heavily than recreational HandHQ data. This taught the model what 'High-Level' bluffs look like, rather than just learning from the mistakes of amateurs who over-call."

### Q5: "How do you handle 'Cold Starts' for players the system has never seen before?"
**Answer:** "We use **Bayesian Priors**. If a player has 0 hands, we assign them the 'Table Average' stats. As we observe their first 5-10 hands, we use a weighted average to 'drift' their stats toward their observed behavior. For example, if they raise their first 3 hands, their PFR (Pre-Flop Raise) stat aggressively climbs toward a 'Maniac' profile until more data stabilizes the mean. This ensures the ML model always has a valid input vector."

### Q6: "What was the most surprising feature discovery during SHAP analysis?"
**Answer:** "The power of **`dryness_delta`**. I originally thought raw board dryness was the key. But the model showed that a *change* in dryness (e.g., a dry Flop becoming a wet Turn) was a massive predictor. If a player was aggressive on a dry flop but suddenly stopped on a wet turn, the model correctly identified that they likely had a 'protection' hand that is now scared. Conversely, if they *increased* aggression when the board got drier, it signaled a high-frequency bluffing opportunity."

---

## 11. Mathematical Feature Deep-Dive: Board Dryness
A "Dry" board is one where few cards can work together to make a straight or flush.
*   **The Algorithm:** I calculated the pairwise 'connectedness' of all board cards.
    *   *Straight Draw Score:* Number of rank-gaps between cards (e.g., 7-8 is 0 gaps, 7-9 is 1 gap).
    *   *Flush Draw Score:* Max frequency of a single suit.
*   **Normalization:** I mapped these to a 0.0 (Extremely Wet) to 1.0 (Extremely Dry) scale.
*   **The Bluff Signal:** High Dryness + High Bet Size = **Narrative Mismatch**. There are very few strong "value hands" that make sense on a 7-2-2 board, so a massive overbet is statistically likely to be air.

---

## 12. Model Explainability (SHAP & LIME)
I didn't just trust the `bluff_probability`. I integrated **SHAP (SHapley Additive exPlanations)** to see which features pushed a specific prediction higher.
*   **In Practice:** For a 90% bluff prediction, SHAP might show:
    *   `+0.35` from `board_dryness`
    *   `+0.25` from `player_vpip` (being very low)
    *   `-0.10` from `bet_amount` (bet was actually quite small)
*   **Result:** This allowed the UI to display a "Reasoning" tooltip: *"High bluff probability due to dry board texture and opponent's historically tight profile."*

---

## 13. Adversarial Analysis: Handling Deception (Sandbagging)
**Challenge:** What if a player "Sandbags" (checks with a very strong hand to trick the AI)?
*   **The "Anti-Trapping" Logic:** I engineered a `passive_narrative` feature. If a player checks/calls on two streets and then suddenly bets huge on the river, the model looks at the **Equivalence Class** of the board.
*   **Decision:** If the board "completed" a draw (e.g., a 3rd heart came), the model correctly identifies this as "Value" rather than a "Bluff." It effectively detects when a player is "slow-playing" a monster hand by comparing their action to the **Board Change Probability**.

---

## 14. Production Safeguards & CI/CD for ML
To ensure the model doesn't "degrade" in production:
1.  **Drift Detection:** I wrote a cron job that compares the weekly distribution of predicted bluff probabilities against the training distribution. If the mean shifts by >10% (indicating a change in player meta), it triggers a retrain alert.
2.  **Circuit Breaker:** If the model's confidence is <0.4, the API returns a `STAY_SILENT` status. It is better to give no advice than bad advice.
3.  **Unit Tests for Logic:** I have 50+ "Golden Hands" (hands where a bluff is 100% certain). Every time I update the model, it must predict these correctly or the build fails.

---

## 15. The Senior Engineer's Reflection
If I were to start over, I would focus even more on **Feature Selection**. Out of 50 features I engineered, only about 12 truly drove 90% of the accuracy. In ML, more data is good, but more *noisy* features can lead to overfitting. My biggest takeaway was that **Domain Expertise (Poker Theory)** is just as important as the **Algorithm (XGBoost)**. You can't build a great model for a game you don't deeply understand.
