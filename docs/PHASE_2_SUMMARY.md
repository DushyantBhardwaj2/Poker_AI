# Phase 2 Summary: The Game Engine

## Achievements
- **Hand Evaluator:** 
  - Implemented best 5-of-7 card evaluation in `packages/domain/hand_evaluator.py`.
  - Supports all standard poker hand ranks from High Card to Royal Flush.
  - Robust tie-breaking logic using kicker values.
- **Turn Manager:** 
  - Implemented `ProcessActionUseCase` to handle player actions (Fold, Check, Call, Raise).
  - Automatic round advancement (Pre-flop -> Flop -> Turn -> River).
  - Validates turn order and illegal moves (e.g., checking when a bet is active).
- **Pot Logic & Showdown:**
  - Implemented advanced Side Pot logic in `apps/api/application/showdown.py`.
  - Correctly calculates and distributes multiple pots based on player contributions and eligibility.
  - Supports all-in scenarios and splitting pots on ties.
- **API Integration:**
  - Added `/action`, `/showdown`, and `/evaluate` endpoints to `apps/api/interfaces/game_controller.py`.

## New File Map
- `packages/domain/hand_evaluator.py`: Hand ranking and comparison logic.
- `apps/api/application/process_action.py`: Core game loop and round management.
- `apps/api/application/showdown.py`: Winner determination and pot distribution.
- `packages/domain/deck.py`: Utility for shuffling and dealing cards.

## How to Start Phase 3
When you are ready to begin Phase 3 (The AI Advisor), give me the following command:

**"Start Phase 3: Implement AI Move Recommendation and Win Probability."**

### Phase 3 Goals:
1. **Win Probability:** Monte Carlo simulation or heuristic-based win chance calculation.
2. **Move Recommendation:** Suggesting optimal moves based on EV (Expected Value) and Pot Odds.
3. **Opponent Profiling:** Basic tracking of player behavior.
