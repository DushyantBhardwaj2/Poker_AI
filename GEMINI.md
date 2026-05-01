# ♠️ PokerSense AI — AI Poker Advisor & Turn-Based Poker Tracker

An intelligent poker assistant focused on speed, accuracy, and real-time strategic advice. PokerSense AI tracks live poker games through a minimalist, mobile-friendly interface, calculates deep mathematical probabilities, and provides optimal move recommendations.

---

## 1. Project Overview

### Project Name
**PokerSense AI**

### Problem Statement
Standard poker calculators are often clunky and difficult to use during a live game. Players need a fast, turn-based tracker that provides instant AI-backed advice on win probability, pot odds, and expected value (EV) without the distraction of complex game graphics.

### Objective of the Project
To provide a high-speed, minimalist "poker sidekick" that:
- Tracks live game state through a simple turn-based UI.
- Calculates mathematical equity and EV using Monte Carlo simulations.
- Analyzes opponent behavior (VPIP/PFR) to predict bluffs and hand ranges.
- Recommends the mathematically optimal move in real-time.

### Positioning
**AI Poker Advisor + Turn-Based Poker Tracker**

---

## 2. Features

### Core Features
- [x] **Setup Game:** Configure players, stacks, and blinds in seconds.
- [x] **Card Selection:** Quickly input hole cards and community cards (Flop, Turn, River).
- [x] **Vertical Action Tracker:** A color-coded vertical list for tracking player actions turn-by-turn.
- [x] **AI Strategy Engine:** Real-time Win Probability, Pot Odds, and EV Analysis.
- [x] **Persistent Stats:** Tracks opponent VPIP/PFR across hands using a local database.

### UI/UX Flow (New Architecture)
1. **Setup Screen:** Input number of players, stacks, and blinds.
2. **Card Selection Screen:** Interactive card picker for user hole cards and community cards.
3. **Turn-Based Tracker:** Vertical list of players with color-coded turn indicators.
   - **Green:** Action completed this round.
   - **Blue:** Current active player (input allowed).
   - **Yellow:** Next upcoming turn.
   - **Gray/Red:** Folded or busted.
4. **AI Suggestion Panel:** Comprehensive breakdown of the current situation and the recommended move.

---

## 3. Tech Stack

| Layer | Technology |
|------|------------|
| Frontend | React.js / Next.js (TypeScript) |
| Styling | Tailwind CSS |
| Backend | FastAPI (Python) |
| Database | SQLite (SQLAlchemy) |
| AI/ML | Monte Carlo Simulations, Heuristic Engines |

---

## 4. System Architecture

### Frontend Component Structure
- `SetupView`: Handles game initialization.
- `CardInputView`: Handles card selection for hole and community cards.
- `ActionTracker`: The main vertical list of player status and action buttons.
- `AIDashboard`: Real-time analysis panel.

### Data Flow
1. User inputs setup/cards/actions in the UI.
2. UI calls FastAPI endpoints (`/game/start`, `/game/action`, `/ai/win-probability`).
3. Backend processes logic and returns updated `GameState`.
4. UI renders the state using color-coded turn indicators and updated stack sizes.
5. At showdown, stats are committed to the SQLite database.

---

## 5. Development Roadmap

### Completed
- [x] Phase 1: Core Architecture & Domain Models
- [x] Phase 2: Game Engine (Turn management, Round advancement)
- [x] Phase 3: AI Advisor (Win Prob, EV, Opponent Profiling)
- [x] Phase 4: Initial Frontend Integration
- [x] Phase 5: Persistent Hand History & Stats

### Current Focus
- [ ] **Frontend Redesign:** Pivot from graphical simulation to minimalist Turn-Based Tracker UI.
- [ ] **Bluff Probability Engine:** Implement advanced logic for bluff detection based on bet sizes and opponent profiles.
- [ ] **Session Exports:** Allow users to export hand histories for post-game study.
   