# ♠️ PokerSense AI — Real-Time Strategic Advisor

[![Production Website](https://img.shields.io/badge/Live-Website-FFD700?style=for-the-badge&logo=vercel&logoColor=black)](https://poker-g23cvv44r-dushyant2.vercel.app)

**PokerSense AI** is a professional-grade poker intelligence tool designed to provide real-time, actionable advice for live poker games. By combining advanced mathematical modeling with behavioral analysis, it acts as a digital co-pilot, helping players make EV-positive (Expected Value) decisions rooted in professional poker theory.

## 🌟 What it Does
PokerSense AI transforms the way you track and analyze live poker. Instead of relying on gut feeling, you get a data-driven HUD (Heads-Up Display) that provides:
- **Real-Time Win Probabilities**: Instant calculation of your hand's equity against opponent ranges.
- **Bluff Detection**: An AI engine that identifies when opponents are likely deviating from their standard range.
- **Strategic Advice**: Contextual recommendations (Fold/Call/Raise) based on pot odds, implied odds, and the *Fundamental Theorem of Poker*.
- **Live Game Tracking**: Simplified interface to record actions, handle complex side pots, and track player stats across multiple sessions.

## 🎮 How to Use
1. **Launch the App**: Open the [Production Website](https://poker-g23cvv44r-dushyant2.vercel.app).
2. **Setup the Table**: Input the current blinds and player stacks to begin tracking a session.
3. **Record Actions**: Click on player names to record their actions (Fold, Check, Call, Raise) as they happen at your real-world table.
4. **Get Advice**: Watch the **AI Advisor HUD** update instantly with win percentages, opponent profiles, and recommended moves.
5. **Post-Hand Analysis**: Review side-pot distributions and hand results to refine your strategy for the next round.

## 🛠️ Built With
- **Frontend**: Modern, high-performance UI built with **Astro** and **React**.
- **Backend**: High-speed, asynchronous API powered by **FastAPI (Python)**.
- **AI/ML**: Behavioral inference engine utilizing **XGBoost** and custom Monte Carlo simulations.
- **Database**: Scalable data persistence with **PostgreSQL (Neon)**.
- **Authentication**: Secure user management via **Neon Auth (JWT)**.
- **Infrastructure**: Automated CI/CD pipelines deployed on **Vercel** and **Render**.

---

*“Every time you play a hand differently from the way you would have played it if you could see all your opponents' cards, they gain; and every time you play your hand the same way you would have played it if you could see all their cards, they lose.” — David Sklansky*

---
© 2026 PokerSense AI
