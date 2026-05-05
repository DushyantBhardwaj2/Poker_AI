# ♠️ PokerSense AI — AI Poker Advisor & Turn-Based Poker Tracker

## 1. Project Overview
**PokerSense AI** is a real-time poker intelligence system. Its primary goal is to provide high-speed, actionable advice during live poker games, deeply rooted in the foundational principles of David Sklansky's "The Theory of Poker".

**Current Status:** Priority 2 (ML Integration & Decision Engine) is 100% complete. The system can now perform real-time bluff detection using XGBoost, calculate range-aware win probability, and synthesize them into actionable advice with theoretical explanations.

## 2. System Behavior Expectations
- **Decision Usefulness over Metrics:** The system's primary directive is to provide the best possible *actionable* advice.
- **Explainable AI:** Recommendations include theoretical context (Pot Odds, Implied Odds, Fundamental Theorem).
- **Production Persistence:** Historical stats are stored in PostgreSQL with multi-tenant isolation via `user_id`.
- **Cold-Start Resilience:** New players are seeded with table-averaged stats for immediate inference accuracy.

## 3. Architecture Overview
- **Database (PostgreSQL/Neon)**: JSONB-powered storage for `opponent_stats`.
- **Backend (FastAPI)**: Stateless endpoints with repository-pattern data access.
- **Frontend (Astro + React)**: 
  - **AdvisorHUD**: Tactical UI for real-time win/bluff analysis.
  - **ActionTracker**: Real-time game state input.
- **AI Domain**: 
  - `bluff_detector.py`: Real-time XGBoost v3 inference.
  - `smart_advisor.py`: Synthesizes math and behavior into strategic advice.

**Current Status:** Priority 2 (ML & Frontend Integration) is 100% complete. The system is fully operational from database to UI.

## 4. Design Aesthetics & UX
- **Premium Interface**: Dark-themed, high-contrast 'Black and Gold' aesthetic inspired by tactical HUDs.
- **Responsive & Tactile**: Full mobile support with optimized touch targets and tactile scale feedback on all interactive elements.
- **Minimal Clicks**: Real-time updates and simplified input flows to keep pace with live gameplay.
- **Automated Showdown & Pot Distribution**: 
  - The UI removes manual pot distribution entirely. Dealers only need to mark players as "SHOW" or "MUCK" and input the revealed hole cards.
  - The Python backend automatically evaluates all 5-card hands, determines the hierarchy, correctly computes side pots based on varying player stacks, and instantly returns the payouts.
  - Multi-winner split pots and complex side-pot resolutions are displayed dynamically in the `PostHandAnalysis` component, ensuring the tracking experience doesn't halt during complex multi-way all-ins.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
