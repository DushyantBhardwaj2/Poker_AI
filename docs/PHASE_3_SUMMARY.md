# Phase 3 Summary: The AI Advisor

## Achievements
- **Win Probability Calculator (`packages/ai/win_probability.py`):**
  - Uses Monte Carlo simulations to estimate win, tie, and equity probabilities.
  - Dynamically adjusts to the number of opponents and current community cards.
- **Move Recommendation Engine (`packages/ai/move_recommender.py`):**
  - Analyzes win probability against Pot Odds.
  - Calculates Expected Value (EV) to determine the mathematically optimal action.
  - Recommends Fold, Check, Call, or Raise along with a textual explanation of the logic.
- **Opponent Profiling (`packages/ai/opponent_profiler.py`):**
  - Takes VPIP (Voluntarily Put In Pot) and PFR (Preflop Raise) metrics.
  - Classifies opponents into distinct play styles: TAG (Tight-Aggressive), Nit (Tight-Passive), LAG (Loose-Aggressive), and Calling Station (Loose-Passive).
- **API Integration (`apps/api/interfaces/ai_controller.py`):**
  - Exposed three new AI endpoints under `/api/v1/ai/`:
    - `POST /win-probability`
    - `POST /recommend-move`
    - `POST /profile-opponent`

## New File Map
- `packages/ai/win_probability.py`: Monte Carlo simulation engine.
- `packages/ai/move_recommender.py`: Decision-making logic based on EV.
- `packages/ai/opponent_profiler.py`: Opponent classification.
- `apps/api/interfaces/ai_controller.py`: FastAPI routes for AI interactions.
- `packages/ai/test_*.py`: Unit tests for the AI components.

## How to Start Phase 4
When you are ready to begin Phase 4 (The Frontend Integration), give me the following command:

**"Start Phase 4: Build the Frontend UI and connect it to the backend."**

### Phase 4 Goals:
1. **Live Poker Table UI:** A visual representation of the game state (players, cards, pot).
2. **Action Controls:** Buttons for users to input game actions (Fold, Call, Raise).
3. **AI Dashboard:** A panel displaying real-time Win Probability, EV, and recommended moves.
