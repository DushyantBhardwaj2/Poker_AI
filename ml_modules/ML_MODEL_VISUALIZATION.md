# PokerSense AI — ML Model Architecture & Decision Workflow

This document explains the internal mechanics of the **PokerSense AI** behavioral intelligence engine. It describes how the model ingests game telemetry, engineers features, executes XGBoost v3 bluff detection inference, and uses Expected Value (EV) formulas to recommend **CALL** or **RAISE** actions. 

Additionally, it provides high-quality generative AI image prompts and includes a visual preview of the architecture.

---

## 1. System Architecture Overview

Below is the conceptual flow of the pipeline, illustrating how raw inputs are transformed into real-time decision recommendations:

```mermaid
graph TD
    %% Define Styles
    classDef inputStyle fill:#1e1e24,stroke:#d4af37,stroke-width:2px,color:#fff;
    classDef engineStyle fill:#111,stroke:#d4af37,stroke-width:3px,color:#fff;
    classDef mathStyle fill:#2d2d30,stroke:#d4af37,stroke-width:2px,color:#fff;
    classDef actionStyle fill:#1a3a2a,stroke:#2ecc71,stroke-width:2px,color:#fff;
    classDef foldStyle fill:#3a1a1a,stroke:#e74c3c,stroke-width:2px,color:#fff;

    %% Input Data
    subgraph Inputs ["1. Input Features & Telemetry"]
        A[Board Cards & Texture]:::inputStyle
        B[Opponent Stats: VPIP / PFR]:::inputStyle
        C[Betting Narrative: Bet Size & Spikes]:::inputStyle
    end

    %% ML Engine
    subgraph MLEngine ["2. Bluff Ingestion & Inference"]
        D[Feature Engineering & Interaction Terms]:::engineStyle
        E[XGBoost v3 Model Classifier]:::engineStyle
        F["Raw Bluff Probability: P(Bluff)"]:::engineStyle
    end

    %% Decision Logic
    subgraph DecisionEngine ["3. Smart Advisor (Sklansky Theory & EV)"]
        G[Bayesian Reliability Weighting]:::mathStyle
        H[Behavioral Drift Adjustment]:::mathStyle
        I[Adjusted Win Probability]:::mathStyle
        J[Expected Value (EV) Calculation]:::mathStyle
    end

    %% Action Output
    subgraph Outputs ["4. Tactical Actions (AdvisorHUD)"]
        K[Action: RAISE - Value/Semi-bluff]:::actionStyle
        L[Action: CALL - Bluff Catch]:::actionStyle
        M[Action: FOLD - Capital Preservation]:::foldStyle
    end

    %% Edges
    A & B & C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    J --> L
    J --> M
```

---

## 2. In-Depth Pipeline Mechanics

### Phase A: Input Feature Engineering
The model transforms raw table events into structured "narrative features":
*   **Board Dryness ($D_{board}$):** Measures the pairwise connectedness of community cards (suit matches, rank gaps). Outputs a value from `0.0` (wet/heavy draw potential) to `1.0` (dry/rainbow board with no draws).
*   **Aggression Metrics:**
    *   `rel_bet_size` = $\frac{\text{bet\_amount}}{\text{pot\_before}}$. Normalizes betting sizing across varying pot sizes.
    *   `bet_spike` = ratio of current street's relative bet size vs. the previous street's. A sudden bet spike indicates a polarized range.
*   **Player Profile Interaction:**
    *   `tightness_bet_interaction` = $(1 - VPIP) \times \text{rel\_bet\_size}$. This ensures a 100bb bet from a tight player ($VPIP = 15\%$) is weighted differently than the same bet from an aggressive maniac ($VPIP = 60\%$).

### Phase B: Bluff Detection via XGBoost v3
The engineered vector is passed to the XGBoost classifier model:
1.  **Ensemble Trees:** The tree path analyzes features in combination.
    *   *Example Path:* If `street == River` AND `rel_bet_size > 1.2` AND `board_dryness > 0.8` AND `opponent_vpip < 0.20` $\rightarrow$ **High Bluff Probability**. (A tight player firing a large bet on a dry board that missed their opening range).
2.  **Inference:** Outputs a calibrated raw bluff probability, $P(\text{Bluff})$.

### Phase C: Smart Advisor Decision Logic
The bluff probability is synthesized with Sklansky's Theory of Poker:
1.  **Bayesian Prior Weighting:**
    If the opponent hand sample size ($N$) is low, we weight the prediction against a GTO baseline bluff probability ($15\%$):
    $$P(\text{Bluff})_{weighted} = \left(P(\text{Bluff}) \times \frac{N}{50}\right) + \left(0.15 \times \left(1 - \frac{N}{50}\right)\right) \quad (\text{bounded at } N \le 50)$$
2.  **Behavioral Drift Correction:**
    If the session tracker detects behavioral drift (e.g., an opponent's aggression index rising above their historical baseline), $P(\text{Bluff})_{weighted}$ is scaled dynamically.
3.  **Adjusted Win Probability:**
    Calling a bluff guarantees a win. The final winning probability is calculated as:
    $$P(\text{Win})_{adjusted} = \left(P(\text{Win})_{GTO} \times (1 - P(\text{Bluff})_{weighted})\right) + \left(0.98 \times P(\text{Bluff})_{weighted}\right)$$
4.  **Expected Value (EV) Formulation:**
    The system calculates pot odds and expected value:
    $$\text{Pot Odds} = \frac{\text{Call Amount}}{\text{Pot Before Call} + \text{Call Amount}}$$
    $$\text{EV} = \left(P(\text{Win})_{adjusted} \times \text{Pot Size}\right) - \left((1 - P(\text{Win})_{adjusted}) \times \text{Call Amount}\right)$$

### Phase D: Tactical Recommendations
*   **RAISE:** If $\text{EV} > 0$ and $P(\text{Win})_{adjusted} > 0.75$. (Value bet or heavy semi-bluff).
*   **CALL:** If $\text{EV} > 0$ and $P(\text{Win})_{adjusted} \ge \text{Pot Odds}$. (Bluff-catching or positive EV draw).
*   **FOLD:** If $\text{EV} \le 0$. (Capital preservation).

---

## 3. Visual Concept Art: How the Model Works
Here is a high-tech infographic showing how the inputs, ML model, and EV math converge to make a decision:

![ML Model Workflow](C:/Users/Dushy/.gemini/antigravity-ide/brain/35fc43f0-606c-4906-9dbf-114c6eecd8e0/ml_model_workflow_1780606709281.png)

---

## 4. Prompts for Image Generators
If you want to generate alternative custom illustrations or UI mockups using Midjourney, DALL-E 3, or Stable Diffusion, you can use the following tailored prompts:

### Prompt 1: The Model Architecture Diagram (Tech/Infographic style)
> **Prompt:** A detailed technical infographic showing a poker machine learning model architecture. The background is a clean, dark cyberpunk grid with black and gold glowing lines. The flow runs from left to right: on the left are inputs labeled "Board Dryness", "Player Stats (VPIP/PFR)", and "Betting Narrative" feeding gold light streams into a central 3D network/decision-tree web labeled "XGBoost v3 Engine". In the center, a digital gauge displaying "Bluff Probability: 76%" glows in red. On the right, decision branches exit pointing to "EV Calculation" and recommendations labeled "Action: CALL" and "Action: RAISE". Professional UI/UX illustration, sleek typography, clean design, 4k resolution.

### Prompt 2: Real-time Live HUD Interface (In-Use style)
> **Prompt:** A futuristic, high-contrast, premium dark-themed live HUD overlaying an online poker screen. The interface uses a luxurious black and gold aesthetic with neon accent highlights. The active player hud box displays stats like VPIP: 22%, PFR: 18%, and showcases a central ring-gauge labeled "Bluff Index: 78%" glowing in amber. Below the gauge, a tactical advice box reads "ADVICE: CALL (Bluff Catch)" with detailed math indicators: "EV: +14.2bb" and "Win Prob: 82%". Cyberpunk style, detailed UI design, smooth curves, sharp vector graphics, game dashboard overlay.

### Prompt 3: Data Flow Concept Art (Abstract ML style)
> **Prompt:** An abstract conceptual art piece showing data flow in a poker artificial intelligence system. Holographic playing cards (7 of Hearts, 2 of Clubs) float in a dark room. Gold streams of binary code and statistical metrics (VPIP, PFR, Pot Odds) flow out of the cards and the betting chips into a glowing, transparent 3D brain/neural net. The neural net processes the streams, changing their color from gold to a bright emerald green, outputting green glowing paths that trace out the words "RAISE" and "CALL" in a sleek futuristic font. Cinema lighting, volumetric glow, octane render, 3d design, high-end visualization.
