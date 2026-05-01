# PokerSense AI - Project Documentation

## Project Overview

PokerSense AI is an intelligent poker advisor that combines live game tracking, AI-based opponent analysis, strategy recommendations, and mathematical probability calculations. The system helps players make optimal decisions by providing real-time win probability, bluff detection, and move recommendations.

## Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
Poker_AI/
├── apps/
│   ├── api/              # FastAPI backend application
│   │   ├── interfaces/   # API controllers and routes
│   │   ├── application/  # Use cases and business logic
│   │   └── infrastructure/ # External dependencies
│   └── web/              # Astro frontend application
│       └── src/
│           ├── pages/    # Astro pages and routes
│           ├── components/ # Astro components
│           └── lib/      # API client and utilities
└── packages/            # Shared domain logic
    ├── domain/           # Core poker domain models
    └── ai/               # AI/ML algorithms
```

### Key Architectural Principles

- **Domain-Driven Design**: Core poker logic lives in `packages/domain/` with no external dependencies
- **Use Case Layer**: Business logic in `apps/api/application/` orchestrates domain operations
- **Interface Layer**: FastAPI controllers in `apps/api/interfaces/` handle HTTP requests
- **Frontend Separation**: Astro app in `apps/web/` communicates via REST API

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **Database**: SQLite (via SQLAlchemy)
- **Validation**: Pydantic

### Frontend
- **Framework**: Astro (React islands for interactivity)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **TypeScript**: Full type safety

### Development
- **Package Manager**: Python (pip), npm
- **Version Control**: Git
- **API Style**: REST with CORS enabled

## Core Features

### Game Engine
- **Hand Evaluation**: Best 5-of-7 card evaluation with all poker hand ranks
- **Turn Management**: Automatic round progression (Pre-flop → Flop → Turn → River)
- **Pot Logic**: Advanced side pot calculation for all-in scenarios
- **Action Processing**: Fold, Check, Call, Raise with validation

### AI Advisor
- **Win Probability**: Monte Carlo simulation for win chance calculation
- **Move Recommendation**: EV-based suggestions (Fold/Call/Raise)
- **Pot Odds Engine**: Mathematical comparison of pot odds vs hand equity
- **Bluff Detection**: Pattern-based opponent behavior analysis using imperfect information modeling:
    - **Narrative vs. Board Texture**: Comparing bet sizes to board connectivity.
    - **Relative Frequency**: Using VPIP/PFR to calculate range density.
    - **Pattern Recognition**: Trained on showdown data to recognize bluff "shapes."
    - **Range Analysis**: Probabilistic modeling across all 1,326 hole card combinations.

### User Interface
- **Live Poker Table**: Interactive visual representation of game state
- **Real-time Updates**: Dynamic tracking of bets, pots, and player status
- **AI Dashboard**: Side panel with probability analysis and recommendations
- **Card Visualization**: Suit-colored cards with proper poker symbols

## Development Workflow

### Starting the Backend

```bash
# Terminal 1
uvicorn apps.api.interfaces.main:app --reload
```

Backend runs on `http://localhost:8000`

### Starting the Frontend

```bash
# Terminal 2
cd apps/web
npm run dev
```

Frontend runs on `http://localhost:4321` (default Astro port)

### API Endpoints

#### Game Management
- `POST /api/v1/game/start` - Initialize a new poker game
- `POST /api/v1/game/action` - Process player actions
- `POST /api/v1/game/showdown` - Determine winners and distribute pots
- `GET /api/v1/game/state` - Get current game state

#### AI Analysis
- `POST /api/v1/ai/win-probability` - Calculate win probability
- `POST /api/v1/ai/recommend-move` - Get optimal move recommendation

#### Statistics
- `GET /api/v1/stats/player/{player_id}` - Get player statistics

## Domain Models

### Core Entities

**Card**: Represents a playing card with suit and rank
- Suits: ♠ (Spades), ♣ (Clubs), ♥ (Hearts), ♦ (Diamonds)
- Ranks: 2-10, J, Q, K, A

**Player**: Represents a poker player
- Stack size, current bet, status (active/folded/all-in)
- Position (Dealer, Small Blind, Big Blind)

**Game**: Represents a poker game session
- Community cards, pot size, current round
- List of players and game state

**HandRank**: Represents poker hand strength
- High Card → Royal Flush (8 levels)
- Includes tie-breaking logic with kickers

### Game Flow

1. **Pre-flop**: Deal hole cards, initial betting round
2. **Flop**: Deal 3 community cards, betting round
3. **Turn**: Deal 4th community card, betting round
4. **River**: Deal 5th community card, final betting round
5. **Showdown**: Reveal cards, determine winners, distribute pots

## Testing

### Backend Tests
```bash
# Run all tests
python -m pytest apps/api/application/

# Specific test files
python -m pytest apps/api/application/test_process_action.py
python -m pytest apps/api/application/test_showdown.py
```

### Frontend Tests
```bash
cd apps/web
npm test
```

## Database

The project uses SQLite for simplicity. Database schema is auto-created on startup via SQLAlchemy ORM.

**Location**: `poker_ai.db` in project root

**Key Tables**:
- `games`: Game sessions
- `players`: Player information
- `actions`: Action history
- `hands`: Hand history

## Project Status

The project has completed 5 development phases:

1. **Phase 1**: Core Architecture & Domain Models ✅
2. **Phase 2**: Game Engine (Hand Evaluator, Turn Manager, Pot Logic) ✅
3. **Phase 3**: AI Advisor (Win Probability, Move Recommendation) ✅
4. **Phase 4**: Frontend UI & Backend Integration ✅
5. **Phase 5**: Complete System Integration ✅

## Current Work: Frontend Premium Redesign (Phase 6)

**Status**: In Progress - CSS compilation error blocking deployment

### Design System Implementation
- **Theme**: Premium casino aesthetic with charcoal backgrounds (#0D0D0D, #1A1A1A, #2D2D2D)
- **Accents**: Gold/amber color palette (#D4AF37, #F4D03F, #B8960C)
- **Typography**: Playfair Display (headings) + Inter (body) via Google Fonts
- **Effects**: Glass-morphism with backdrop blur, noise texture overlay
- **Animations**: fadeIn, slideUp, scaleIn, pulseGold with stagger delays

### Files Modified
- `apps/web/src/styles/global.css` - Complete CSS overhaul with CSS variables, custom utilities, animations
- `apps/web/src/pages/index.astro` - Updated title, added noise overlay div
- `apps/web/src/components/SetupView.tsx` - Premium setup interface with gold gradient buttons
- `apps/web/src/components/ActionTracker.tsx` - Enhanced player cards with status indicators
- `apps/web/src/components/AIDashboard.tsx` - Improved AI panel with better data visualization
- `apps/web/src/components/CardInputView.tsx` - Premium card selection grid with suit symbols
- `apps/web/src/components/PokerTable.tsx` - Updated main container with error alert styling
- `apps/web/src/components/CardComponent.tsx` - Enhanced card design with corner decorations
- `apps/web/tailwind.config.mjs` - Added custom colors (gold, charcoal, cream), fonts, animations

### Current Issue
**CSS Compilation Error**: "Cannot apply unknown utility class border-border" in global.css
- Backend running on http://127.0.0.1:8000 (FastAPI) ✅
- Frontend dev server on http://localhost:4321 (Astro) ❌ CSS error blocking compilation

### Next Steps
1. Fix CSS compilation error - identify and remove border-border utility references
2. Restart frontend dev server with cache cleared
3. Verify all components render correctly with new premium design
4. Test full user flow: Setup → Card Input → Game Tracker → AI Analysis

## Frontend Migration Status

**Current Status**: Migrated from Next.js to Astro

The frontend has been successfully migrated from Next.js 16 to Astro with the following changes:

### Migration Details
- **Framework**: Next.js → Astro (with React islands for interactive components)
- **Structure**: App router → Astro pages and components
- **Styling**: Tailwind CSS 4 → Tailwind CSS (maintained)
- **API Client**: Preserved and adapted for Astro
- **State Management**: React hooks → Astro client-side state management

### Key Changes
- Removed Next.js-specific code (app router, server components)
- Created Astro pages structure (`src/pages/`)
- Converted React components to Astro components
- Maintained all existing functionality and API contracts
- Improved performance with Astro's static generation where applicable

### Benefits of Astro Migration
- Faster initial page loads
- Better SEO capabilities
- Smaller bundle sizes
- More flexible framework choices (can use React, Vue, Svelte, etc.)
- Better developer experience with Astro's component islands

## Future Enhancements

- Hand history storage & replay
- Player statistics dashboard (VPIP, PFR, aggression factor)
- Opponent profiling (Tight/Aggressive, Loose/Passive)
- Strategy explanation engine
- Session analytics & graphs
- Screenshot OCR recognition
- Voice assistant integration
- Real-time overlay on poker clients
- GTO Solver integration

## Important Notes

- **CORS**: Backend allows all origins for development (`allow_origins=["*"]`)
- **Type Safety**: Both backend (Pydantic) and frontend (TypeScript) are fully typed
- **Clean Architecture**: Domain logic has no dependencies on frameworks
- **API Design**: RESTful endpoints with clear separation of concerns
- **State Management**: Game state is server-side, frontend is stateless

## Common Commands

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd apps/web && npm install

# Run backend
uvicorn apps.api.interfaces.main:app --reload

# Run frontend
cd apps/web && npm run dev

# Build frontend for production
cd apps/web && npm run build

# Run backend tests
python -m pytest apps/api/application/
```

## File Structure Reference

### Backend Key Files
- `apps/api/interfaces/main.py` - FastAPI app entry point
- `apps/api/interfaces/game_controller.py` - Game API routes
- `apps/api/interfaces/ai_controller.py` - AI API routes
- `apps/api/application/start_game.py` - Game initialization logic
- `apps/api/application/process_action.py` - Action processing
- `apps/api/application/showdown.py` - Winner determination
- `packages/domain/hand_evaluator.py` - Hand ranking logic
- `packages/domain/deck.py` - Card deck utilities
- `packages/ai/win_probability.py` - Win probability calculation
- `packages/ai/move_recommender.py` - Move recommendation logic

### Frontend Key Files
- `apps/web/src/pages/index.astro` - Main poker table UI
- `apps/web/src/lib/api.ts` - API client wrapper
- `apps/web/src/components/` - Astro components for poker table, AI sidebar, etc.
- `apps/web/src/styles/global.css` - Global styles

## Contributing

When adding new features:

1. **Domain First**: Add domain models to `packages/domain/`
2. **Use Cases**: Implement business logic in `apps/api/application/`
3. **API Layer**: Add endpoints in `apps/api/interfaces/`
4. **Frontend**: Update UI in `apps/web/src/`
5. **Tests**: Add tests for new functionality
6. **Types**: Ensure TypeScript types match Pydantic models

### Frontend Development with Astro

- **Pages**: Add new pages in `apps/web/src/pages/`
- **Components**: Create reusable components in `apps/web/src/components/`
- **Styling**: Use Tailwind CSS classes for styling
- **Interactivity**: Use React islands for interactive components
- **API Calls**: Use the API client in `apps/web/src/lib/api.ts`

## Troubleshooting

**Backend won't start**: Check if port 8000 is in use
```bash
# Windows
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <PID> /F
```

**Frontend won't start**: Check if port 4321 is in use
```bash
# Windows
netstat -ano | findstr :4321
```

**Astro build issues**: Ensure all dependencies are installed and TypeScript is properly configured
```bash
cd apps/web
npm install
npm run build
```

**Database locked**: Close any database connections or delete `poker_ai.db` to reset

**CORS errors**: Ensure backend is running and CORS middleware is configured
