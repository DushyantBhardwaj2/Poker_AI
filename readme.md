# ♠️ PokerSense AI — AI Poker Advisor & Turn-Based Tracker

[![Deploy to Render](https://img.shields.io/badge/Deploy%20to-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![Deploy with Vercel](https://img.shields.io/badge/Deploy%20with-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)

**PokerSense AI** is a real-time poker intelligence system designed to provide high-speed, actionable advice during live gameplay. Rooted in David Sklansky's "The Theory of Poker," it synthesizes mathematical probability with behavioral analysis to deliver strategic recommendations.

## 🚀 Key Features

- **Real-Time Bluff Detection**: Powered by an **XGBoost v3** model that analyzes betting patterns, board texture, and player history.
- **Range-Aware Win Probability**: Monte Carlo simulations calculate equity against estimated opponent ranges.
- **Smart Advisor HUD**: A tactical "Black and Gold" interface providing real-time EV-positive recommendations (Fold, Call, Raise).
- **Explainable AI (XAI)**: Every move comes with a theoretical breakdown (Pot Odds, Implied Odds, Fundamental Theorem).
- **Automated Side-Pot Resolution**: Complex multi-way all-ins and side pots are handled instantly by the backend.
- **Cold-Start Resilience**: New opponents are seeded with table-averaged baselines for immediate inference accuracy.

## 🏗️ Architecture

- **Frontend**: Astro + React (Zustand State Management) - Hosted on **Vercel**.
- **Backend**: FastAPI (Python) - Hosted on **Render**.
- **Database**: PostgreSQL (Neon) with JSONB for flexible opponent profiling.
- **ML Engine**: XGBoost for behavioral inference + Custom hand evaluation logic.

## 🛠️ Installation & Setup

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DushyantBhardwaj2/Poker_AI.git
   cd Poker_AI
   ```

2. **Backend Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   pip install -r requirements.txt
   pip install -e ./packages/domain
   ```

3. **Frontend Setup**:
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```

4. **Database Initialization**:
   ```bash
   python scripts/init_postgres.py
   ```

## 🌐 Deployment

This repository is configured for automated deployment via GitHub Actions:

- **API (Render)**: Automatically builds from the root `Dockerfile`.
- **Web (Vercel)**: Automatically builds from the `apps/web` directory using the Astro preset.

### Environment Variables Required:
- `DATABASE_URL`: Your PostgreSQL connection string.
- `GEMINI_API_KEY`: For AI-driven insights and automated repository maintenance.

---

*“The Fundamental Theorem of Poker: Every time you play a hand differently from the way you would have played it if you could see all your opponents' cards, they gain; and every time you play your hand the same way you would have played it if you could see all their cards, they lose.” — David Sklansky*
