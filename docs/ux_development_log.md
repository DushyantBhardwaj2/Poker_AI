# PokerSense AI - UX Development Log

This log tracks the incremental implementation of the UX Advancement Plan. Its purpose is to maintain a clear and detailed record of all UX changes, architectural decisions, and backend refactors.

---

## 2026-05-09 — Phase 13: Deterministic Decision Pipeline

### Objective
Implement the 9-stage deterministic decision pipeline as defined in Section 20 of the UX Advancement Plan. This addresses the critical hallucination risk by ensuring "Narrative summarizes evidence; it does not create it."

### Rationale
The UX Advancement Plan (Section 20) mandates a pipeline where each stage's output serves as validated input for the next. This architecture prevents the AI from generating invented reasoning - every narrative claim must be traceable to deterministic calculations.

### UX Impact
- **Critical** - Establishes architectural safeguards against AI hallucination
- **High** - Ensures trust through transparency in reasoning

### Changes Made

#### 1. New Pipeline Module (packages/ai/pipeline.py)
- **Created 9-stage deterministic pipeline:** Implements the full architecture as specified
- **Stage 1 (Raw Input):** Ingestion layer for hand state inputs
- **Stage 2 (Validation):** `validate_game_state()` - Checks for illegal actions, inconsistent stacks, out-of-order turns
- **Stage 3 (Range Engine):** `estimate_opponent_range()` - Probabilistic range estimation based on position, VPIP/PFR
- **Stage 4 (Tactical Engine):** `compute_tactical_analysis()` - Pure mathematical computation (equity, pot odds, EV)
- **Stage 5 (Confidence Engine):** `assess_confidence()` - Bayesian reliability scoring based on sample size
- **Stage 6 (Semantic Mapping):** `map_to_semantics()` - Rules-based translation of numbers to labels
- **Stage 7 (Narrative Renderer):** `render_narrative()` - Template-based text generation (NOT LLM)
- **Stage 8 (Response Validator):** `validate_response()` - Schema validation, sanity checks, certainty filtering
- **Stage 9 (UI Delivery):** `build_delivery_response()` - Builds final AdvisorResponse

#### 2. Pipeline Orchestrator
- **`run_advisor_pipeline()`:** Main entry point that runs all 9 stages sequentially
- Returns tuple of (AdvisorResponse, pipeline_errors)
- Raises `ValidationError` if game state is invalid

#### 3. Hallucination Safeguards
- **Template-based generation:** No LLM - uses pre-defined templates populated with structured data
- **Prohibited language filter:** Removes certainty words (definitely, certainly, always, never)
- **Cross-stage validation:** Ensures narrative doesn't contradict tactical data
- **Confidence constraints:** High confidence blocked if sample_size < 50

#### 4. Semantic Mapping (Stage 6)
- **Equity → Labels:** Maps 80-100% → "Overwhelming Favorite", 65-79% → "Strong Favorite", etc.
- **Pot Odds → Labels:** Maps >40% → "Excellent Price", 28-40% → "Good Price", etc.
- **Risk Levels:** Low/Medium/High based on board texture and flags
- **Strategic Themes:** Maps actions + equity to Value Betting, Bluff Catching, Semi-Bluff, etc.

#### 5. Response Validation (Stage 8)
- **Checks performed:**
  - Narrative confidence must match sample size
  - Narrative shouldn't contradict equity (e.g., fold with >70% equity)
  - Key factors must align with tactical flags
  - Certainty words filtered from output

### Technical Notes
- Pipeline is decoupled from SmartAdvisor - can run independently
- Uses dataclasses for each stage's output type
- All narrative generation uses templates, not generative AI
- Philosophy: "Trust is more important than appearing intelligent"

### Pipeline Architecture Summary
```
[Raw Hand State] → Validation Layer → Range Engine → Tactical Engine → 
Confidence Engine → Semantic Mapping → Narrative Renderer → Response Validator → [UI Delivery]
```

### Non-Goals Implementation (Per Section 25)
- **No LLM integration:** Template-based system avoids hallucination risk
- **No real-time "reads":** All opponent analysis is statistical/probabilistic
- **No range guessing:** Uses established range models, not imagination
- **No certainty claims:** All language is probabilistic

### Next Step
Phase 14: Integration with existing SmartAdvisor for fallback mode
Phase 26: Hallucination Risk Audit (formal verification of safeguards)

---

## 2026-05-09 — Phase 6: Session Analytics & Post-Game Review

### Objective
Implement session analytics and post-game review capabilities to provide players with insights into their session performance, hand history, and strategic patterns over time.

### Rationale
As outlined in Section 13 of the UX Advancement Plan, a complete poker experience includes post-hand analysis and session summaries. Players need to understand how they're performing to improve their game.

### UX Impact
- **Medium** - Provides session-level insights
- **Low** - No immediate UI; analytics available for future dashboard components

### Changes Made

#### 1. Database Schema Expansion (db_models.py)
- **Added HandHistory model:** New table tracks individual hand results including street, pot size, cards, result, amount won, action count, and duration
- **Enhanced GameSession:** Added `total_winnings` field to track session profit/loss

#### 2. StatsRepository Enhancements (stats_repository.py)
- **record_hand_result():** Records hand outcome for analytics
- **get_session_analytics():** Returns comprehensive session metrics including win rate, showdown rate, biggest pot/loss
- **get_hand_history():** Returns hand history across all sessions
- **end_session():** Marks a session as ended with timestamp

#### 3. Stats Controller Endpoints (stats_controller.py)
- **POST /stats/hand_result:** Records the result of a completed hand
- **GET /stats/history:** Returns hand history across all sessions
- **GET /stats/session/{session_id}/analytics:** Returns comprehensive session analytics
- **POST /stats/session/end:** Marks a session as ended

#### 4. Frontend API Client (api.ts)
- Added TypeScript interfaces: `HandHistory`, `SessionSummary`, `SessionAnalytics`
- Added API functions: `getSessionAnalytics()`, `getAllHandHistory()`, `recordHandResult()`

### Technical Notes
- Hand history stores cards as JSON for later display
- Session analytics calculates win rate, showdown rate, average hand duration
- Most played opponent derived from SessionOpponent relationships

### Next Step
Phase 7: Session Analytics Dashboard.

---

## 2026-05-09 — Phase 7: Session Analytics Dashboard

### Objective
Implement the Session Analytics Dashboard to provide players with a comprehensive view of their session performance, historical hands, and strategic trends.

### Rationale
As outlined in Section 13 of the UX Advancement Plan, the complete poker experience requires a post-game reflection layer. Players need to see their profit/loss, win rates, and specific hand histories to learn from their sessions.

### UX Impact
- **High** - Adds a major new functional area for post-game analysis
- **Medium** - New navigation item in the Sidebar

### Changes Made

#### 1. Frontend Navigation (Sidebar.tsx)
- **Added Analytics Link:** Integrated a new "Analytics" item using the `TrendingUp` icon.
- **Visual Integration:** Positioned for high visibility between "Play Game" and "Learn Poker".

#### 2. Analytics Page (analytics.astro)
- **New Route:** Created the `/analytics` route with full SSR support and client-side hydration.

#### 3. Analytics View Component (AnalyticsView.tsx)
- **HUD-Style Dashboard:** Implemented a high-contrast tactical dashboard.
- **Stat Cards:** Visualizes Net Profit/Loss, Win Rate, Volume, and Hand Duration with trend indicators.
- **Hand History Feed:** Interactive list showing every recorded hand, including street reached, pot size, and card results.
- **Dynamic Insights:** Added a "Strategic Insight" section that provides text-based feedback based on session volume.
- **Session Context:** Shows start time and duration for the active session.

#### 4. Live Integration (PokerTable.tsx)
- **Automated Recording:** Updated `handleShowdown` to automatically transmit hand results (net winnings, street, cards) to the database upon hand completion.
- **Outcome Calculation:** Implemented client-side logic to determine net profit/loss and outcome category (win/loss/tie) for accurate history tracking.

### Technical Notes
- Uses `getSessionAnalytics` and `getAllHandHistory` from the API.
- Graceful degradation for sessions with low or no data.
- Mobile-responsive grid layout for stats and history.

### Next Step
Phase 11: Advanced Coaching & Leak Detection.

---

## 2026-05-09 — Phase 11: Advanced Coaching & Leak Detection

### Objective
Implement a "Leak Detection" module that identifies systematic mathematical and strategic errors in the user's play. This transitions the application from a real-time advisor into a long-term coaching tool.

### Rationale
As outlined in the UX Advancement Plan (Phase D), advanced coaching provides strategic feedback by analyzing play over multiple sessions. By identifying specific -EV decisions (leaks), we help users improve their game fundamentally.

### UX Impact
- **High** - Adds a "Strategic Leaks Identified" section to the Analytics Dashboard.
- **Medium** - Dynamic "Strategic Insight" based on detected leaks.

### Changes Made

#### 1. Database Schema Evolution (docs/schema.sql & db_models.py)
- **Enhanced HandHistory:** Added `tactical_data` (JSONB) to store the AI's analysis at the time of decision.
- **New Metadata:** Added `leak_detected` (Boolean) and `leak_description` (Text) for fast filtering of strategic errors.

#### 2. Intelligence Engine Expansion (stats_repository.py)
- **Deterministic Leak Detection:** Implemented logic in `record_hand_result` to identify:
    - **-EV Calls:** Flagged when `win_probability < pot_odds`.
    - **Over-Aggression:** Flagged when a high-variance bluff fails to get through.
- **Data Persistence:** Tactical snapshots from the `AdvisorResponse` are now permanently linked to hand results.

#### 3. Frontend Analytics Update (AnalyticsView.tsx)
- **Leaks Dashboard:** Added a prominent section for "Strategic Leaks Identified" that surfaces the specific hands and reasons for identified mistakes.
- **Dynamic Coaching:** Refactored the "Strategic Insight" card to provide personalized feedback based on the user's specific leaks in the current session.

#### 4. Game Loop Integration (PokerTable.tsx & api.ts)
- **Tactical Capturing:** Updated the showdown and hand-recording logic to transmit the AI's tactical context (equity, pot odds, verdict) to the backend.

### Technical Notes
- Leak detection currently focuses on river/showdown decisions where tactical data is most definitive.
- Uses Bayesian-style regression in the backend to ensure leaks are only flagged when the AI has high confidence in the tactical signals.

### Next Step
Phase 12: Visual Polish & Tactile Feedback.

---

## 2026-05-09 — Phase 12: Visual Polish & Tactile Feedback

### Objective
Enhance the tactile and visual feedback of the "Poker Night" spatial interface. The goal is to make the application feel more like a high-end gaming experience by animating physical metaphors (chips, cards, dealer movement).

### Rationale
As outlined in Priority 4 of the project roadmap, visual polish is critical for immersion and user satisfaction. Non-static UIs reduce cognitive load by providing clear visual cues for state changes (e.g., seeing chips move to the pot clarifies that a bet was processed).

### UX Impact
- **High** - Drastically improves the "feel" and immersion of the gameplay.
- **Medium** - Provides better visual feedback for actions and round transitions.

### Changes Made

#### 1. Enhanced Chip Animation System (VirtualTable.tsx)
- **Multi-Directional Chips:** Implemented a `ChipParticle` system that supports both "Betting" (Player to Pot) and "Winning" (Pot to Player) directions.
- **Dynamic Spawning:** Chips now spawn from the specific player who acted, with randomized spreads for a physical feel.
- **Showdown Effects:** At showdown or hand reset, chips now "explode" from the pot towards the winner (dealer fallback).

#### 2. Spatial Card Deal Animations (VirtualTable.tsx)
- **Community Deals:** Community cards now fly from the dealer button position to the center of the felt, rather than just fading in.
- **Hole Card Deals:** Hole cards now animate from the dealer position to the player's pod, with rotation and scaling for a "dealt" feel.
- **Showdown Reveal:** Cards revealed at showdown use spring physics for a tactile flip effect.

#### 3. Interactive Feedback (ActionTracker.tsx)
- **Haptic Visuals:** Added `whileHover` and `whileTap` animations to all major action buttons.
- **High-Stakes Emphasis:** The "All-In" button now features a continuous golden pulse and a rotation-shake on hover to emphasize the weight of the decision.
- **Active Player Pulse:** The active player's status ring now uses a slower, more deliberate 2s pulse with subtle scaling.

#### 4. Dealer Button Movement (VirtualTable.tsx)
- **Layout Animations:** The Dealer button now uses `layoutId` for smooth transitions between seats when the dealer rotates or reorders.

### Technical Notes
- Leverages `Framer Motion` for all hardware-accelerated animations.
- Animation coordinates are calculated dynamically based on the spatial table layout (% to px conversion).
- Spring-based physics (`stiffness`, `damping`) ensure animations feel "snappy" and "tactile" rather than robotic.

### Next Step
Phase 13: Stealth Mode & Mobile Discretion (Watch/Mini-HUD Support).

---

## 2026-05-08 — UX Refinement Pass (Pre-Phase 3)

### Objective
Perform a focused polish and usability refinement pass on the current Phase 2 implementation. The goal is to make the interface feel fast, alive, effortless, readable, premium, and tactically responsive—without adding feature bloat or increasing cognitive load.

### Rationale
Before implementing Phase 3 (Opponent Memory System), the existing UX must feel polished enough that adding new systems feels like an enhancement, not a rescue attempt for weak UX.

### UX Impact
- **High** - Visible improvements to visual hierarchy, interaction feel, and readability
- **Low** - No new features added; purely refinements to existing components

### Changes Made

#### 1. Visual Noise Reduction (global.css)
- **Reduced glow intensity:** Shadow values reduced from `0 0 30px` to `0 0 20px` with lower opacity (0.12 vs 0.15)
- **Strong shadow reduced:** From `0 0 50px` (0.25) to `0 0 30px` (0.18)
- **Glass effects refined:** Blur reduced from 20px to 16px; border opacity lowered from 0.1 to 0.08
- **Pulse animation subdued:** Gold pulse now uses 15px/25px shadows vs 20px/40px

**Why:** The previous glow effects were creating visual fatigue during extended play sessions. The interface felt "neon" rather than "premium tactical tool."

#### 2. Sidebar De-emphasis (Sidebar.tsx)
- **Width reduced:** From 72 (w-72) to 64 (w-64) on desktop
- **Border simplified:** From `border-gold/10` to `border-white/5`
- **Background lighter:** From `bg-charcoal` to `bg-charcoal-dark/95`
- **Branding simplified:** Removed "OS v2.4 // THEORY DRIVEN" tagline; logo reduced from 10 to 9 size; font changed from black to bold

**Why:** The sidebar was visually competing with the gameplay table. Navigation should support gameplay, not compete with it.

#### 3. Table-Centric UX Refinement (VirtualTable.tsx)
- **Felt border reduced:** From 3px gold/10 to 2px white/5
- **Grid pattern simplified:** Opacity reduced from 0.03 to 0.015; grid size increased from 50px to 60px
- **Player pod borders:** Reduced from white/10 to white/8; active state ring from gold to gold/60
- **Active player scale:** Reduced from scale-115 to scale-105 for more subtle emphasis
- **Status ring pulse:** Replaced aggressive pulse-gold animation with slower 2s pulse animation

**Why:** The table felt static and decorative. Now it feels more active and tactically responsive while maintaining visual clarity.

#### 4. Typography System Refinement (AdvisorHUD.tsx)
- **Mode toggle:** Smaller padding (px-3.5 py-1.5 vs px-4 py-2); font from bold to semibold; reduced shadow
- **Info badges:** Smaller padding (p-3.5 vs p-4); text size reduced to 9px; tracking increased to wider
- **Factor cards:** Reduced padding (p-3.5 vs p-4); smaller icons (16 vs 18); tighter spacing
- **Strategic view:** Reduced font size (text-2xl vs text-3xl); tighter spacing
- **Gauges:** Smaller size (w-20 h-20 vs w-24 h-24); reduced stroke width (3 vs 4)

**Why:** Typography was feeling inconsistent and slightly oversized. Unified sizing creates better visual rhythm.

#### 5. Right Panel Information Balance (AdvisorHUD.tsx)
- **Container gap increased:** From gap-4 to gap-5 for breathing room
- **Border refinement:** From white/10 to white/5 for subtler definition
- **Tactical view card:** Reduced padding; border from gold/30 to gold/20; gradient intensity reduced
- **Explanation section:** Cleaner border (white/5 vs gold/20); improved spacing and hierarchy

**Why:** Information density was high but compressed. Better spacing improves scanability and reduces cognitive load.

#### 6. Interaction & Live Play Feel (global.css + components)
- **New utility classes:** Added `transition-tactical` (0.2s) and `transition-tactical-fast` (0.15s) for consistent interaction timing
- **Action panel:** Reduced border radius (32 vs 40); lighter border (white/10 vs gold/30); subtler background
- **Mode toggle:** Consistent 0.2s transitions across states

**Why:** The UI felt slightly static. Subtle transitions improve perceived responsiveness without being distracting.

#### 7. Copywriting Pass (ActionTracker.tsx)
- **Street notification:** Changed from "Analyzing opponent tendencies from recent action" to "Reading opponent from current hand"
- **Language change:** Removed technical backend terminology in favor of strategic, human-readable poker language

**Why:** Phrases like "VPIP/PFR analysis running" feel robotic. Strategic language creates better immersion.

### Technical Notes
- All changes are purely presentational; no logic changes
- Backward compatible with existing API contracts
- Animation durations reduced for faster perceived responsiveness

### Mobile-First Validation
- Touch targets remain appropriately sized (buttons use p-3 to p-4)
- Fixed action panel at bottom provides good thumb reach
- Layout uses flex-col on mobile, flex-row on lg breakpoint
- Text sizes scale appropriately (9-14px range maintained)

### Rejected Approaches
- **Full animation overhaul:** Rejected - would increase cognitive load
- **Casino-style effects:** Rejected - conflicts with "premium tactical tool" aesthetic
- **Bold color changes:** Rejected - maintaining gold/cream/charcoal palette for brand consistency

### Next Step
Phase 3: Opponent Memory System — the foundation is now laid for adding memory/recall features to an already-polished UX.

---

## 2026-05-08 — Phase 3: Opponent Memory System

### Objective
Implement a persistent, user-specific opponent intelligence system that tracks player behavior across sessions, calculates playstyle archetypes, and provides session-vs-baseline analysis for behavioral drift detection.

### Rationale
As outlined in the UX Advancement Plan (Section 5), a truly intelligent poker assistant must remember opponents and their tendencies. This saves the user mental energy and enables more accurate strategic advice.

### UX Impact
- **High** - Adds intelligent opponent profiles with automatic classification
- **Medium** - New expanded stats panel shows reliability and session comparison

### Changes Made

#### 1. Database Schema Expansion (db_models.py)
- **Added Opponent fields:** `notes` (user notes), `playstyle_archetype`, `last_seen`
- **Added OpponentStats enhancements:** `session_features` for session vs baseline tracking, `reliability_score` based on sample size
- **Added GameSession table:** Tracks individual sessions for session-vs-baseline analysis
- **Added SessionOpponent table:** Tracks opponent stats within specific sessions

**Why:** Persistent storage is required for opponent memory. The schema expansion enables automatic archetype classification and data quality assessment.

#### 2. StatsRepository Enhancement (stats_repository.py)
- **calculate_archetype():** Automatic classification based on VPIP/PFR/aggression thresholds (Rock, Nit, TAG, LAG, Maniac, Tight Passive, Loose Passive)
- **calculate_reliability():** Scores data quality as Low/Medium/High based on hand count (500+ = High, 100+ = Medium)
- **Enhanced update_player_stats():** Now tracks C-bet success, 3-bet frequency, fold-to-river, showdown wtsd, and session-only stats
- **get_opponent_profile():** Returns detailed profile including session vs baseline comparison and behavioral drift detection
- **get_recent_opponents():** Returns list of recently played opponents for quick-add
- **update_opponent_notes():** Allows users to add notes to opponent profiles

**Why:** The repository is the single source of truth for all opponent data. These methods enable the full Opponent Memory System functionality.

#### 3. API Endpoint Expansion (stats_controller.py)
- **GET /stats:** Returns all opponent stats with Phase 3 metrics (archetype, reliability, cbet_rate, wtsd, etc.)
- **GET /stats/recent:** Returns recently played opponents
- **GET /stats/player/{name}:** Returns detailed profile including session vs baseline analysis
- **POST /stats/update_stats:** Updates opponent stats after each hand with enhanced tracking
- **POST /stats/notes:** Updates opponent notes
- **POST /stats/reset_session:** Resets session-only stats for fresh baseline comparison

**Why:** Frontend needs these endpoints to consume and display opponent data.

#### 4. Frontend API Client (api.ts)
- Added TypeScript interfaces: `OpponentProfile`, `OpponentProfileDetail`, `RecentOpponent`
- Added API functions: `getRecentOpponents()`, `getOpponentProfile()`, `updateOpponentNotes()`, `updatePlayerStats()`, `resetSessionStats()`

**Why:** Frontend must be able to consume the new backend endpoints with full type safety.

#### 5. PlayerStats Component Refactor (PlayerStats.tsx)
- **New display:** Shows archetype badges with color coding (Rock=Red, TAG=Green, LAG=Blue, etc.)
- **Reliability indicator:** Shows data quality (Low/Medium/High confidence) next to hand count
- **Expandable details:** Click to see expanded stats (C-bet, 3-bet, WTSD, notes)
- **Improved hierarchy:** Cleaner layout with proper spacing and typography

**Why:** UI must display the new data in an accessible, scannable format.

#### 6. PokerTable Integration (PokerTable.tsx)
- **Session reset:** Calls `resetSessionStats()` on new session start for fresh baseline
- **Stats update:** Calls `updatePlayerStats()` after showdown with hand details

**Why:** The frontend must feed data back to the backend to build opponent profiles.

### Technical Notes
- All stats are user-specific (tied to user_id) for privacy
- Cold-start problem solved with table-averaged baseline initialization
- Sample-size gates prevent unreliable classifications (archetypes only after 20 hands)
- Session vs baseline comparison enables "shifting" detection

### Data Flow
1. New session starts → `resetSessionStats()` clears session features
2. Hand played → Actions tracked in game state
3. Showdown → `updatePlayerStats()` called for each opponent with hand details
4. Next session → Compare session_vpip vs baseline_vpip to detect drift

### Mobile-First Validation
- Stats panel remains compact on mobile
- Expandable details use simple tap-to-expand
- Archetype badges are color-coded for quick visual identification
- Reliability indicator uses color (green/yellow/gray) instead of small text

### Next Step
Phase 3 is now complete. The foundation for adaptive opponent modeling is in place. Future enhancements could include:
- More advanced bluff detection heuristics
- Session analytics for post-game review
- Integration with the Explanation Engine for opponent-specific factors

---

## 2026-05-08 — Hidden Information & Realism Correction Pass

### Objective
Restore proper hidden-information poker behavior and fix the critical realism issue where opponent hole cards were visible during active play. The system must preserve uncertainty, probabilistic reasoning, and behavioral inference integrity.

### Rationale
The advisor system must feel like it's interpreting BEHAVIOR and estimating TENDENCIES, not reading hidden cards. When opponent cards are visible during live play, the AI appears omniscient, fake, and unfair - breaking user trust and strategic authenticity.

### UX Impact
- **Critical** - Restores poker realism and strategic tension
- **High** - Improves advisor believability and trust

### Changes Made

#### 1. Card Visibility Fix (CardComponent.tsx)
- **Added CardBack component:** New component displays a gold-patterned card back for hidden cards
- **Sizes supported:** xs, sm, md, lg to match regular CardComponent

**Why:** The UI needs to display something for opponents with hole cards, without revealing their actual hand.

#### 2. VirtualTable Opponent Card Handling (VirtualTable.tsx)
- **User's hand (index 0):** Shows actual cards as before
- **Active opponents:** Shows two CardBack components (hidden card backs)
- **Folded opponents:** Shows "Folded" indicator instead of any cards
- **Showdown:** Cards revealed only through ShowdownLogicView (proper input flow)

**Why:** Maintains hidden-information integrity during live play while preserving showdown resolution flow.

#### 3. Advisor Wording Refinement (mock-data.ts)
- **All summaries now use probabilistic language:** "appears", "suggests", "may represent", "potentially indicating"
- **Removed omniscient phrasing:** No more "is bluffing", "has AK", "missed flush"
- **Added uncertainty acknowledgment:** Notes when sample size is limited
- **Created factory function:** `createAdvisorResponse()` generates behavior-based narratives dynamically

**Examples of new language:**
- OLD: "Opponent is bluffing."
- NEW: "Opponent's betting pattern appears aggressive and may represent a bluff attempt."

- OLD: "They missed their flush."
- NEW: "The large bet size represents either a strong hand or a pure bluff - difficult to distinguish."

**Why:** The advisor must never sound like it has hidden information access. Users should trust the system is interpreting behavior, not reading cards.

#### 4. Data Quality Integration
- **Sample size acknowledgment:** Explicitly notes when history is limited
- **Confidence degradation:** Lower confidence when fewer hands recorded
- **Decay reason display:** Shows user why confidence is reduced

**Why:** Transparency about data quality builds trust. The system is honest about what it knows vs. assumes.

### Technical Notes
- Hidden cards only render during active play states
- ShowdownLogicView properly handles card entry (user inputs cards, not auto-revealed)
- CardBack matches the visual style of regular cards (gold accent)

### Why Hidden Information Matters

1. **Poker Realism:** Live poker is about playing opponents, not their cards. Visible cards break this fundamental.

2. **Strategic Tension:** Uncertainty creates the strategic complexity that makes poker interesting.

3. **Trust in AI:** When cards are visible, the advisor feels fake/unfair. When hidden, users trust the advisor is working from behavior/probability.

4. **Behavioral Focus:** Opponent profiling should identify WHO the player is (TAG, LAG, etc.), not WHAT they have.

5. **Learning Value:** Users learn to read players through the advisor's behavioral interpretation, not by seeing cards.

### Rejected Approaches
- **Auto-deal reveal to all players:** Would break poker integrity
- **Show all cards during review mode:** Not implementing full replay yet - preserving architecture for later
- **Change confidence colors based on data quality:** Already implemented in Phase 3

---

## 2026-05-08 — Phase 4: Table Management UX

### Objective
Redesign the table interface for maximum speed, flexibility, and resilience. Eliminate disruptive modals in favor of inline editing and spatial interactions. Implement session resilience to handle interruptions.

### Rationale
Live poker is chaotic. Players join, leave, sit out, and make bet-entry errors constantly. The interface must be as dynamic as the game itself without requiring full-page reloads or complex setup flows.

### UX Impact
- **High** - Drastically improves the "live tracking" experience with drag-and-drop and inline editing.
- **Critical** - Adds Undo support and Auto-save, preventing data loss from misclicks or refreshes.

### Changes Made

#### 1. Centralized State Migration (usePokerStore.ts)
- **Store Refactor:** Migrated the core `GameState` from local component state to a centralized Zustand store. This unifies state across the `ActionTracker`, `VirtualTable`, and `PokerTable` components.
- **Undo Stack:** Implemented a rolling 10-level deep undo stack that snapshots state before any mutation.

#### 2. Spatial Table Interactivity (VirtualTable.tsx)
- **Drag-and-Drop Seating:** Enabled native HTML5 drag-and-drop on `PlayerPod` components for real-time seat reordering.
- **Dealer Rotation:** Added tactical buttons to manually rotate the dealer button in either direction.
- **Undo Button:** Integrated a prominent "Undo Action" button for immediate error correction.

#### 3. Mobile-First Management (PlayerPod.tsx)
- **Tap-to-Toggle Menu:** Replaced hover-only overlays with a mobile-friendly tap-to-toggle management grid.
- **Inline Stack Editing:** Clicking a player's stack now opens an inline numeric input for instant adjustment.
- **Quick Player Lifecycle:** Added one-tap buttons for "Sit Out/Join", "Kick (Remove)", and "Add Stack".

#### 4. Session Resilience (usePokerStore.ts)
- **Auto-Save Mechanism:** The store now automatically persists the current session state to `localStorage` on every significant action.
- **Fault Tolerance:** Users can refresh the browser or recover from a crash without losing their current hand or opponent data.

### Technical Notes
- **Event-Sourced Pattern:** By snapshotting the full state in the undo stack, we ensure complex mutations (like removing a player mid-hand) are always reversible.
- **Optimistic Sync:** Handled the synchronization between local store updates and backend API responses, ensuring a smooth, "zero-lag" feel.

### Next Step
Phase 4 is complete. The foundation for a fast, reliable live tracker is fully realized. Next is Phase 6: Session Analytics & Post-Game Review.

---

## 2026-05-08 — Phase 5: Reliability & Trust Layer

### Objective
Implement the Trust & Reliability Architecture to earn and maintain user trust by transparently communicating uncertainty. The system must degrade gracefully when data is sparse and prioritize game-theory principles over unreliable behavioral reads.

### Rationale
As outlined in Section 11 of the UX Advancement Plan, trust is the primary product metric. A single piece of bad, overconfident advice can destroy user trust. The system must "know when it doesn't know."

### UX Impact
- **High** - Adds clear reliability indicators and trust-centric narrative
- **Medium** - Integrates opponent archetypes into strategic advice

### Changes Made

#### 1. Bayesian Reliability Weighting (SmartAdvisor.py)
- **Weighted Bluff Probability:** Implemented a weight `min(1.0, hands / 50.0)` that regresses the ML bluff detection towards a 15% baseline when sample size is low.
- **Sample-Size-Aware Reasoning:** Recommendations are heavily weighted towards GTO if `hands < 50`.

#### 2. Enhanced Confidence Engine (SmartAdvisor.py)
- **Multidimensional Scoring:** Reliability is now calculated based on sample size (20/50/100 thresholds), archetype stability, data completeness, and mathematical "edge" (spot clarity).
- **Graceful Degradation:** The `confidence_level` is programmatically downgraded based on these factors.

#### 3. Trust-Centric Narrative (SmartAdvisor.py)
- **Probabilistic Language:** All advice strings now use "appears to be", "suggests", "may" instead of deterministic claims.
- **Uncertainty Context:** Added specific explanations for why confidence is reduced (e.g., "Insufficient data: This is a new opponent").
- **Archetype Integration:** Strategic advice now explicitly mentions the opponent's playstyle archetype.

#### 4. AdvisorHUD Trust UI (AdvisorHUD.tsx)
- **Low Reliability Warning:** Added a prominent orange "Low Read Reliability" badge for speculative reads.
- **Archetype Badge:** Replaced generic "Theme" badge with "Opponent Type" in the Strategic View.
- **Refined Data Quality Section:** Updated with semantic reliability labels (High, Moderate, Low, Speculative) and trust-centric descriptions.

#### 5. Controller Integration (ai_controller.py)
- **Profile Injection:** The `analyze_full` endpoint now retrieves the detailed opponent profile from the database to provide the advisor with archetype and sample size context.
- **Completeness Estimation:** Added a heuristic for data completeness based on hand history length.

### Technical Notes
- 50 hands is the threshold for "full trust" in ML behavioral reads.
- Bayesian regression prevents the system from chasing noise in small samples.
- The UI now explicitly warns users when the AI is making a "best guess" vs. a "data-backed read."

### Next Step
Phase 5 is complete. The system is now significantly more trustworthy and transparent. Ready for Phase 6: Session Analytics & Post-Game Review (if requested) or Phase 4: Table Management UX.

---

## 2026-05-08 — Phase 1: Foundation & Safe Refactor

### Objective
The primary objective of this phase is to establish a stable architectural foundation for the new narrative-driven UX without introducing any breaking changes to the existing API or frontend. This involves evolving the backend's data structures to support a richer, more semantic form of strategic advice.

### Changes Made
- **Initialized Development Log:** Created `docs/ux_development_log.md` to begin tracking all implementation details as required by the execution plan.
- **Defined Structured Response Schema:** Implemented new Pydantic models in `packages/domain/models.py`. The new `AdvisorResponse` model provides a comprehensive, typed structure for all AI advice, while retaining all legacy fields to ensure 100% backward compatibility with the existing frontend.
- **Refactored AI Advisor:** Modified `packages/ai/smart_advisor.py` to replace its dictionary-based output with the new `AdvisorResponse` object. The advisor now populates both the new structured fields (with placeholders for narrative content) and the legacy fields.
- **Verified API Controller:** Confirmed that `apps/api/interfaces/ai_controller.py` correctly handles the new `AdvisorResponse` object, ensuring seamless serialization to JSON without impacting the API's public contract. A minor logging statement was updated to use attribute access instead of dictionary access.

### UX Impact
- **Zero immediate impact.** This was a backend-only change designed to be completely transparent to the current UI.
- It prepares the groundwork for the "Strategic Mode" UI (Phase 2) by making the necessary data available in a structured format.

### Reliability Impact
- **Enhanced Data Integrity:** By creating a strictly-typed, validated schema, we reduce the risk of malformed or inconsistent data being sent to the frontend.
- **Foundation for Trust:** The new `confidence_level` and `key_factors` fields are the first step in building a system that can communicate uncertainty and explain its reasoning, which is critical for the "Reliability & Trust Layer" (Phase 5).

### Technical Notes
- The changes will be additive to the existing `AdvisorResponse` model to ensure 100% backward compatibility. The frontend will continue to function without any modifications.
- All new data structures will be defined using Pydantic for automatic validation.

### Risks / Follow-Ups
- **Risk:** None at this stage, as no logic is being altered.
- **Follow-Up:** The backend is now fully prepared for the Phase 2 UI implementation.

---

## 2026-05-08 — Phase 2: Strategic Mode UI

### Objective
To transform the user experience of the `/play` page from a technical dashboard into a narrative-driven strategic assistant. The primary goal is to prioritize clarity, glanceability, and fast comprehension for live-play usability. This will be achieved by creating a new "Strategic Mode" as the default view.

### Changes Made
- **Pending:** This entry marks the official start of Phase 2. The following frontend changes are now queued for implementation:
    - Create the main `StrategicMode` React component.
    - Implement a UI toggle to switch between `StrategicMode` and the existing `TacticalMode`.
    - Build the `StrategicDirective` card component to serve as the new focal point.
    - Redesign the layout to emphasize whitespace and visual hierarchy, de-emphasizing raw numbers.
    - Create a `SemanticBadge` component for displaying confidence and risk levels.
    - Develop a collapsible `Explanation` component to render the structured explanation data from the API.

### UX Impact
- **High.** This phase will introduce the most significant change to the user-facing application.
- The goal is to reduce cognitive load during a live game, making advice easier to absorb and act upon quickly.
- By hiding raw data behind a "Tactical Mode" toggle, the default experience will feel calmer and more focused.

### Reliability Impact
- **Low direct impact.** This is primarily a frontend presentation change.
- However, by building components that correctly represent confidence and uncertainty (e.g., `ConfidenceBadge`), we begin to build user trust in the system's outputs, which is a core goal of the "Reliability & Trust Layer" (Phase 5).

### Technical Notes
- A new shared type definition file (`apps/web/src/types/advisor.ts`) will be created to mirror the `AdvisorResponse` Pydantic model, ensuring type safety between the frontend and backend.
- State management for the Strategic/Tactical mode toggle will be handled in the main Zustand store (`usePokerStore.ts`).

### Risks / Follow-Ups
- **Risk:** Introducing too much complexity into the UI could harm the goal of "fast comprehension." The design must remain minimal and focused.
- **Follow-Up:** Ensure the new components are fully responsive and tested on various mobile screen sizes.
