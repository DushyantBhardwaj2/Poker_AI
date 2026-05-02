# ♠️ PokerSense AI — Real-Time Poker Intelligence System

PokerSense AI is a **real-time decision support system** designed to assist players during live poker games. Rather than just calculating math or serving as a post-game analytics dashboard, it combines mathematical probability, opponent behavioral modeling, and game logic to provide actionable, real-time advice with clear explanations.

## 1. What the System Is
PokerSense AI acts like an expert poker coach sitting beside you. It tracks the game state, calculates odds on the fly, profiles opponents based on their betting patterns, and gives you a single, clear recommendation (Fold, Call, Raise) along with the reasoning behind it.

## 2. Key Components
- **Win Probability Engine:** Uses Monte Carlo simulations to calculate your hand's mathematical equity against expected opponent ranges.
- **Bluff Detection Model:** Analyzes opponent actions (bet sizing relative to pot, board texture, and player history) to predict the likelihood of a bluff.
- **Decision Engine:** Merges win probability, pot odds, and bluff likelihood to generate an Expected Value (EV)-positive recommendation.
- **Explanation Engine:** Translates complex EV calculations into human-readable advice (e.g., "Call: You have 3-to-1 pot odds, but a 40% chance of hitting your flush, making this a profitable call.").
- **Player Modeling:** Continuously tracks opponent tendencies (VPIP, PFR, Aggression Frequency) and uses this data to adjust bluff detection and range estimation.

## 3. How It Works
1. **Game State Input:** You input your hole cards, community cards, pot size, and opponent actions via a fast, mobile-friendly UI.
2. **Feature Extraction:** The system processes the raw game state into features (pot odds, board texture, opponent VPIP).
3. **Probability & Bluff Modeling:** The AI runs win probability simulations and feeds the extracted features into the bluff detection model.
4. **Decision Engine:** The AI computes the highest EV move based on the math and the behavioral models.
5. **UI Output & Explanation:** The system presents the recommended action along with a clear, concise explanation of *why* you should make that move.

## 4. Use Cases
- **Live Poker Assistance:** Get real-time advice on complex decisions during a live or online game.
- **Decision Support:** Validate your instincts with mathematical and behavioral backing.
- **Player Analysis:** Keep track of how specific opponents play over time, allowing the system to adapt its advice to exploit their weaknesses.
- **Post-Game Coaching:** Review hands and understand the math and behavioral tells you might have missed.

## Tech Stack
- **Frontend:** Astro (with React components), Tailwind CSS, strictly tailored for real-time mobile tracking.
- **Backend/AI:** Python (FastAPI), SQLAlchemy, Scikit-Learn/PyTorch (for ML).
