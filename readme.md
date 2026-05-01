# ♠️ PokerSense AI — Smart Poker Advisor & Live Game Analyzer

An AI-powered poker assistant that tracks live poker games, analyzes betting behavior, predicts bluff probability, calculates winning chances, and recommends optimal moves in real-time.

---

## 1. Project Overview

### Project Name
**PokerSense AI**

### Problem Statement
Poker is a game of incomplete information, probability, psychology, and strategic decision-making. Players often struggle to:
- Calculate winning probability quickly
- Evaluate pot odds and expected value
- Detect opponent bluffing
- Determine the best move under pressure

There is no simple, real-time assistant that combines live game tracking, AI-based opponent analysis, strategy recommendations, and post-game coaching.

### Objective of the Project
To build an intelligent poker advisor that:
- Mirrors a real poker game through manual input
- Tracks player actions in real-time
- Calculates mathematical probabilities
- Detects bluff patterns
- Recommends optimal decisions
- Teaches users strategy using historical analysis

### Target Users
- Beginner poker players
- Intermediate poker players
- Professional players wanting assistance
- Poker learners/students
- Game theory enthusiasts

### Real-world Use Case
A poker game is being played in real life or online. User opens PokerSense AI and:
1. Enters the number of players
2. Enters stack sizes
3. Enters their own cards
4. Tracks every player's action turn-by-turn

The app then:
- Updates pot size
- Calculates winning chances
- Predicts bluff probability
- Suggests the best move

### Why this Project is Unique / Innovative
Unlike simple poker calculators, PokerSense AI combines:
- **Live Poker Tracking UI**
- **AI Move Recommendation**
- **Bluff Detection**
- **Opponent Behavior Analysis**
- **Game Theory Integration**
- **Hand History Coaching**

It is a hybrid of a poker calculator, poker coach, and poker AI advisor.

---

## 2. Features

### Core Features
- [x] Create live poker table/game
- [x] Add N players
- [x] Add stack sizes
- [x] Select user cards
- [x] Add community cards
- [x] Track player actions (bet, raise, fold, check, call)
- [x] Automatic pot calculation (including side pots)
- [x] Turn management (pre-flop, flop, turn, river, showdown)

### Advanced Features
- [ ] Hand history storage & replay
- [ ] Player statistics dashboard (VPIP, PFR, aggression factor)
- [ ] Opponent profiling (Tight/Aggressive, Loose/Passive)
- [ ] Strategy explanation engine (explain *why* a move is suggested)
- [ ] Session analytics & graphs

### AI/ML Features

| Feature | Purpose |
|---------|---------|
| Win Probability Prediction | Predict the chance of winning the hand |
| Bluff Detection | Predict if an opponent is bluffing |
| Opponent Type Classification | Classify as Tight/Loose, Aggressive/Passive |
| Hand Strength Prediction | Estimate opponent’s hidden card range |
| Bet Size Recommendation | Suggest optimal bet size based on pot odds & opponent |
| Move Recommendation | Fold / Call / Raise / All-in |
| EV Analysis | Long-term profitability of a decision |
| Pot Odds Engine | Compare pot odds to hand equity |
| Personalized Strategy | Adapt to user’s playstyle over time |

### Future Enhancements
- Screenshot OCR recognition (auto-detect cards/chips)
- Computer Vision card/chip detection
- Voice assistant (“What should I do?”)
- Real-time overlay on poker clients
- Multiplayer sync (cloud game state)
- GTO Solver integration

---

## 3. Tech Stack

| Layer | Technology |
|------|------------|
| Frontend | React.js / Next.js |
| Styling | Tailwind CSS |
| Backend | Node.js / Express.js (or FastAPI) |
| Database | MongoDB (or PostgreSQL) |
| Auth | Firebase Auth / JWT |
| AI/ML | Python, Scikit-learn, TensorFlow, PyTorch |
| ML API | FastAPI (Python microservice) |
| APIs | REST (future: WebSocket for real-time) |
| Deployment (Frontend) | Vercel / Netlify |
| Deployment (Backend) | Railway / Render / AWS EC2 |
| Deployment (ML Service) | Hugging Face Spaces / AWS Lambda / FastAPI on Render |
| Version Control | Git + GitHub |
| CI/CD | GitHub Actions |

---

## 4. System Architecture

### High-Level Architecture