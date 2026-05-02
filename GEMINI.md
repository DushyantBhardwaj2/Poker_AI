# ♠️ PokerSense AI — AI Poker Advisor & Turn-Based Poker Tracker

## 1. Project Overview
**PokerSense AI** is a real-time poker intelligence system. Its primary goal is to provide high-speed, actionable advice during live poker games, deeply rooted in the foundational principles of David Sklansky's "The Theory of Poker". It is a poker assistant, not a dashboard or a simple poker calculator. 

### Core Objective
To track live games efficiently and provide immediate strategic advice based on a fusion of mathematical probability (EV, Pot Odds, Equity) and opponent behavioral modeling (Hand Ranges, Player Profiling, Deception).

## 2. System Behavior Expectations
- **Decision Usefulness over Metrics:** The system's primary directive is to provide the best possible *actionable* advice (Fold, Call, Raise) in real-time. Academic ML metrics (like achieving 99% precision in bluff detection) are secondary to making EV-positive recommendations that make sense in the context of the game.
- **Always Explain:** A recommendation is useless without trust. The system MUST explain its reasoning, citing specific theoretical concepts like **Pot Odds, Implied Odds, Positional Advantage, or the Fundamental Theorem**.
- **Real-Time Constraints:** The system must be fast. All calculations and model inferences must execute in milliseconds to keep up with the pace of a live game.
- **Adaptive:** The system must adapt its advice based on the accumulated behavior profile of the specific opponents at the table.
- **Educational Core:** The system doubles as a learning tool. The foundational data from "The Theory of Poker" has been comprehensively extracted into detailed modules in `docs/theory/` and summarized in `docs/poker_theory_summary.md`, forming the basis for a "Theory Mastery Course" and a quick-reference "Strategist's Guide".

## 3. Architecture Overview (Modular)
- **Frontend (Astro + React)**: Utilizing **Astro File-Based Routing** for high-performance navigation.
  - **MainLayout**: Global wrapper ensuring persistent Sidebar and Footer.
  - **View Transitions**: Seamless SPA-like transitions using Astro's `ClientRouter`.
  - **Component Model**: React handles intensive game logic (`PokerTable`), while Astro orchestrates routing and static content (Theory, Guide).
- **Backend (FastAPI)**: Orchestrates game flow, AI analysis, and data persistence.
- **AI Domain (packages/ai/)**:
  - `win_probability.py`: Mathematical simulation.
  - `opponent_profiler.py`: Behavior tracking (VPIP/PFR) and classification (TAG/LAG/Nit).
  - `move_recommender.py`: Strategic recommendation engine with theoretical injection.
- **Database (SQLite)**: Persistent storage for hand history and player profiling.

## 4. Design Aesthetics & UX
- **Premium Interface**: Dark-themed, high-contrast 'Black and Gold' aesthetic inspired by tactical HUDs.
- **Responsive & Tactile**: Full mobile support with optimized touch targets and tactile scale feedback on all interactive elements.
- **Minimal Clicks**: Real-time updates and simplified input flows to keep pace with live gameplay.
