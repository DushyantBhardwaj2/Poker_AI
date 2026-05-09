# PokerSense AI — UX Advancement & Intelligence Architecture

**Document Owner:** Senior Product Architect
**Status:** Proposed
**Version:** 1.0
**Date:** May 8, 2026

**Objective:** This document outlines the strategic plan to evolve the PokerSense AI `/play` experience from a technical poker dashboard into a narrative-driven, user-centric AI poker intelligence assistant. This is a product-level redesign of our UX and intelligence architecture, not a UI beautification project. The goal is to reduce cognitive overload during live play while preserving tactical depth for advanced users.

---

## 1. Vision & Product Philosophy

The next generation of PokerSense AI must feel less like a tool and more like a trusted partner. Our product identity will be defined by its role as:

-   **A Strategic Poker Assistant:** It provides clear, high-level strategic direction first.
-   **A Tactical Co-Pilot:** It offers detailed, contextual data when requested, but not before.
-   **An Intelligent Memory System:** It remembers opponents and their tendencies, saving the user mental energy.

It must explicitly **NOT** feel like:

-   A mathematical dashboard cluttered with numbers.
-   A solver console demanding complex interpretation.
-   An analytics cockpit built for data scientists.

The user experience (UX) will be rebuilt around principles of **fast understanding**, **readable strategic insights**, **opponent memory**, **confidence communication**, and **narrative explanations**.

### The User's Core Questions

Through user research and first-principle analysis, we've determined that players under pressure do not want raw poker math first. They are trying to answer fundamental, qualitative questions:

-   Am I likely ahead right now?
-   Is my opponent bluffing?
-   Is this call worth the risk?
-   What kind of player am I up against?

Therefore, our core design mantra will be: **Strategic summary must always precede raw metrics.**

---

## 2. Strategic Narrative System

To align with our philosophy, the backend intelligence layer will be expanded. The current `CALL`/`FOLD`/`RAISE` recommendation is insufficient. We will implement a new narrative-based response schema that provides structured, multi-faceted advice.

This schema separates the high-level story from the low-level data, allowing the UI to present a clear narrative by default while making tactical numbers available on demand.

### New `SmartAdvisor` Response Schema

Below is the proposed JSON structure for all `/advise` endpoint responses.

```json
{
  "advice": {
    "action": "CALL",
    "verdict": "Call the Bluff",
    "summary": "Opponent is applying excessive pressure on a board that does not strongly favor their range. Your hand has significant potential to improve and is likely good enough to win at showdown.",
    "strategic_theme": "Bluff Catching",
    "confidence_label": "High Confidence",
    "risk_level": "Medium Variance",

    "hand_potential": {
      "current_strength": "Medium Pair",
      "draw_strength": "Strong Flush Draw",
      "improvement_chance": "High"
    },

    "bluff_analysis": {
      "likelihood": "Moderate",
      "reason": "Opponent overbets dry boards more frequently than average based on your history with them."
    },

    "board_analysis": {
      "texture": "Dry",
      "range_advantage": "Player",
      "volatility": "Low"
    },

    "factors": [
      {
        "type": "positive",
        "title": "Favorable Pot Odds",
        "detail": "The pot is offering you a good price to call; you only need limited equity to continue profitably.",
        "priority": 1
      },
      {
        "type": "positive",
        "title": "Opponent History",
        "detail": "This player has shown a tendency to bluff in similar spots in past sessions.",
        "priority": 2
      },
      {
        "type": "warning",
        "title": "Large River Bet",
        "detail": "Be aware: the opponent's sizing represents polarized strength (either a monster hand or a complete bluff).",
        "priority": 1
      }
    ],

    "alternative_line": "For a more conservative approach, folding is acceptable, especially if this opponent has been playing unusually tight today."
  },

  "tactical_data": {
    "equity": 61,
    "ev": 2.1,
    "pot_odds": 28,
    "opponent_stats": {
      "vpip": 35,
      "pfr": 28,
      "agg_freq": 6.1
    }
  }
}
```

### Rationale for New Schema

-   **Structured Reasoning:** A structured JSON object is vastly superior to a single block of text. It allows the frontend to create a rich, hierarchical, and interactive UI instead of just displaying a paragraph.
-   **Separation of Concerns:** `advice` (the narrative) is decoupled from `tactical_data` (the numbers). This is the architectural foundation for our dual-mode UX.
-   **Uncertainty Language:** Fields like `confidence_label`, `risk_level`, and probabilistic phrasing in summaries ("likelihood", "potential") build trust. The AI is a co-pilot, not an omniscient god. This manages expectations and encourages critical thinking.
-   **Probabilistic, Not Omniscient:** Explanations will be framed around likelihoods and tendencies, reflecting the true nature of poker. This is more honest and more useful than feigning certainty.

---

## 3. Strategic Mode vs. Tactical Mode

The centerpiece of the new UX is a dual-mode interface, allowing users to switch between a high-level strategic view and a detailed tactical view.

### Strategic Mode (Default View)

This mode is designed for fast, at-a-glance comprehension during a live hand.

-   **Narrative-First:** The `verdict` and `summary` are the most prominent elements.
-   **Semantic Badges:** Information is presented as human-readable labels (e.g., "High Confidence," "Bluff Catching," "Loose Aggressive Opponent").
-   **Minimal Numbers:** Raw percentages and stats are hidden. Equity is shown as a simple bar or label like "Slight Favorite."
-   **Large, Readable Directive:** A clear, unambiguous call to action (e.g., "CALL THE BLUFF," "PROCEED WITH CAUTION").
-   **Opponent Archetype:** Displays the opponent's playstyle, drawn from the Opponent Memory System.
-   **Simplified Insights:** The `factors` are displayed as concise, color-coded bullet points.

### Tactical Mode (Analyst View)

This mode is for users who want to dig into the underlying mathematics and data. It should feel like "unlocking analyst mode."

-   **Advanced Metrics:** Exposes all fields from the `tactical_data` object.
-   **Gauges and Charts:** Visualizes equity, pot odds, and EV with precise gauges.
-   **Detailed Stats:** Shows the opponent's VPIP/PFR/AGG numbers.
-   **Numerical Analysis:** Provides a more detailed breakdown of the hand combinations and ranges being considered.

### Implementation Guidance

-   **Feature Flag:** The entire dual-mode system can be developed behind a feature flag for iterative testing.
-   **React State Toggle:** A simple `useState` hook in the main `AdvisorHUD` component will manage the `'strategic' | 'tactical'` mode.
-   **Animated Transitions:** Use a library like `Framer Motion` to create smooth, animated transitions between modes. The container should elegantly expand to reveal the tactical data.
-   **State Preservation:** Ensure all relevant state (e.g., scroll position in the explanation panel) is preserved when switching between modes.

---

## 4. Human-Friendly Poker Intelligence

We must translate raw poker statistics into human-readable, intuitive language. Users understand behavior and likelihood better than raw numbers. The backend will perform this translation, providing semantic labels directly to the frontend.

### Semantic Translation Tables

| Metric          | Raw Value Range | Semantic Label       |
| --------------- | --------------- | -------------------- |
| **Equity**      | 80-100%         | Overwhelming Favorite|
|                 | 65-79%          | Strong Favorite      |
|                 | 55-64%          | Slight Favorite      |
|                 | 45-54%          | Coinflip             |
|                 | 25-44%          | Underdog             |
|                 | 0-24%           | Longshot             |
| **VPIP**        | 0-15%           | Nit / Rock           |
|                 | 16-24%          | Tight / Selective    |
|                 | 25-35%          | Active               |
|                 | 36%+            | Loose / Maniac       |
| **Aggression**  | 0-1.5           | Passive              |
| (Factor)        | 1.6-3.0         | Solid Aggression     |
|                 | 3.1-5.0         | Aggressive           |
|                 | 5.1+            | Hyper-Aggressive     |
| **Bluff Freq.** | 0-10%           | Rarely Bluffs        |
|                 | 11-25%          | Bluffs Selectively   |
|                 | 26-40%          | Frequent Bluffer     |
|                 | 41%+            | Compulsive Bluffer   |
| **Confidence**  | (Internal Score)| High Confidence      |
|                 |                 | Medium Confidence    |
|                 |                 | Low Confidence       |

This approach is critical because **users emotionally understand poker through likelihood and behavior, not percentages.**

---

## 5. Opponent Memory System

To truly function as an intelligent assistant, the system must have memory. We will build a persistent, user-specific opponent intelligence system.

### Core Requirements

-   **User-Specific Data:** All opponent data is tied to the logged-in `user_id` and must be completely private.
-   **Persistent Storage:** Opponent profiles and historical stats will be stored in our PostgreSQL database.
-   **Automated Tracking:** The system will track every hand played against a named opponent, updating their key statistics:
    -   Bluff Frequency (e.g., `bluff_river_bet_missed_draw`)
    -   Aggression Factor / Frequency
    -   Showdown Tendencies (e.g., `wins_at_showdown`, `folds_to_river_bet`)
    -   Betting Patterns (e.g., `cbet_success_rate`, `3bet_frequency`)

### UX Requirements

-   **Autocomplete Player Names:** When the user starts typing a player's name at the table, suggest names from their history.
-   **Recently Played List:** Provide a quick-add list of opponents from recent sessions.
-   **Automatic Playstyle Badges:** Based on tracked stats, automatically apply semantic badges (e.g., "Loose Aggressive," "Tight Passive") to opponents at the table.
-   **Historical Notes:** Allow users to add free-text notes to an opponent's profile.

**Example Opponent Profile Snippet:**

```text
Aman — Loose Aggressive
VPIP: 42% | PFR: 35% | AGG: 4.8
“Frequently overbets river spots and has been caught bluffing with missed draws twice.”
Last seen: May 7, 2026
```

### Database Architecture Recommendations

-   `opponent_profiles` **Table**:
    -   `profile_id` (PK)
    -   `user_id` (FK to `users`, for data isolation)
    -   `opponent_name` (string)
    -   `notes` (text)
    -   `playstyle_archetype` (string, e.g., 'TAG', 'LAG', 'ROCK')
-   `opponent_historical_stats` **Table**:
    -   `stat_id` (PK)
    -   `profile_id` (FK to `opponent_profiles`)
    -   `stat_name` (e.g., 'vpip', 'pfr', 'agg_factor')
    -   `stat_value` (numeric)
    -   `hands_sampled` (integer)
    -   `last_updated` (timestamp)
-   **Session Linkage:** The existing `game_sessions` table will be linked to `opponent_profiles` to track which opponents participated in each session. Stats will be aggregated and updated post-session.

---

## 6. Table Management UX

Live poker games are dynamic and chaotic. Our interface must prioritize **speed, minimal clicks, and live editing** without relying on disruptive modal dialogs.

### Redesign Requirements

-   **Drag-and-Drop Seating:** Allow users to drag player avatars around the table to change seating positions.
-   **Quick Stack Editing:** Clicking a player's stack size should make the field editable inline.
-   **Fast Rebuy/Add-on:** A simple "+" button next to a stack allows for quick top-ups.
-   **Player Lifecycle:** Simple controls to mark a player as "Sitting Out," or to remove them from/add them to the table.
-   **Position Swapping:** A dedicated, simple UI for rotating positions (e.g., moving the button).

### Implementation Suggestions

-   **Inline Editing:** Use libraries like `react-x-editable` or build custom components for seamless inline text/number editing.
-   **Contextual Actions:** Right-clicking (or long-pressing on mobile) a player avatar should bring up a small contextual menu with actions like "Edit Stack," "Add Note," "Remove Player."
-   **Mobile Responsiveness:** All controls must have large, touch-friendly tap targets.
-   **Fast Chip Controls:** Instead of just a text input for bets/stacks, provide chip denomination buttons (`+10`, `+25`, `+100`) for rapid adjustments.

---

## 7. Explanation Engine UX

Long paragraphs of text are hard to scan under pressure. We will refactor the explanation architecture to be a **prioritized, scannable tactical briefing, not an essay.**

### New Explanation Format

-   **Prioritized Bullets:** Use an ordered list where the most important factor is always first.
-   **Positive/Warning Indicators:** Use icons (e.g., ✅, ⚠️, 📉) and colors to instantly communicate the nature of each factor.
-   **Concise Tactical Language:** Each point should be a sharp, clear statement.

**Example UI Mockup:**

---
**Key Factors for This Decision:**

✅ **Favorable Pot Odds** — The pot is giving you a great price to call; this is mathematically justified.

⚠️ **Opponent's Polarized Sizing** — This large bet typically represents either a monster hand or a total bluff.

📈 **Strong Flush Draw** — You have many outs to make a winning hand on the river.

📉 **Board Doesn't Hit Villain's Range** — The turn card is unlikely to have helped the pre-flop aggressor.
---

This format is scannable, hierarchical, and communicates complex reasoning in seconds.

---

## 8. Product Design Principles

Our visual philosophy must align with our product vision. Complexity should be hidden until requested.

The app should **NOT** feel like:

-   A hacker dashboard (dense, monospaced, cryptic).
-   A trading terminal (overloaded with flashing numbers and charts).
-   A debugging interface (raw, unstyled, utilitarian).

The app **SHOULD** feel like:

-   **An Intelligent Strategic Assistant:** Clean, calm, and confidence-inspiring.
-   **A Premium Tactical Tool:** Polished, responsive, and precise.
-   **A Modern Coaching Interface:** Focused on learning and clarity.

### Guiding Principles

-   **Whitespace:** Generous spacing to reduce cognitive load.
-   **Readability:** Large, high-contrast fonts for easy reading in varied lighting conditions.
-   **Hierarchy:** Clear visual priority. The most important information is the most prominent.
-   **Minimal Clutter:** If it's not essential for the "Strategic Mode," it's hidden.
-   **Progressive Disclosure:** Reveal complexity and detail only when the user explicitly asks for it.

---

## 9. Implementation Roadmap

We will implement this vision in a phased approach to manage risk and gather feedback.

-   **Phase A: Backend & Foundation (Stealth Mode)**
    -   Expand the `SmartAdvisor` backend to generate the new narrative JSON schema.
    -   Deploy this change in shadow mode, logging the new responses without affecting the current UI.
    -   Begin backend work on the Opponent Memory System (database schema, data access layer).

-   **Phase B: The Strategic Leap**
    -   Implement the new "Strategic Mode" UI as the default experience.
    -   Redesign the explanation panel using the new bullet-point format.
    -   Introduce semantic badges for equity, confidence, etc.

-   **Phase C: Deepening the Experience**
    -   Launch the full Opponent Memory System, including historical notes and automatic badging.
    -   Roll out the redesigned Table Management UX.
    -   Implement and release the "Tactical Mode" UI for advanced users.

-   **Phase D: Adaptive Intelligence**
    -   Introduce adaptive intelligence that learns from in-session behavior.
    -   Develop advanced coaching modules that analyze a user's play over multiple sessions and provide strategic feedback.

---

## 10. Critical Product Warnings

To succeed, we must be as disciplined about what we *don't* do as what we do.

-   **Avoid Fake Certainty:** Never present a bluff detection or equity calculation as 100% certain. Always use probabilistic language. User trust is our most valuable asset.
-   **Avoid Overwhelming Users:** The default view must remain simple. Do not let "Tactical Mode" features bleed into "Strategic Mode."
-   **Avoid Exposing Internal Complexity:** The user should never see a raw range matrix or a solver's internal decision tree. Our job is to synthesize, not expose.
-   **Avoid Generic AI Explanations:** All narrative text must be purpose-written by poker experts or generated by highly-tuned, domain-specific models.
-   **Avoid "Feature Overload":** Every new feature must be rigorously evaluated against our core philosophy. If it adds clutter or cognitive load, it's rejected.

**Our guiding principle remains: Trust and clarity are more valuable than raw, uninterpreted complexity.**

---

## 11. Trust & Reliability Architecture

For a poker intelligence system, **trust is the primary product metric**, valued far higher than perceived intelligence or the sheer number of features. A single piece of bad, overconfident advice can permanently erode user trust. Our architecture must be built from the ground up to earn and maintain this trust by transparently communicating uncertainty.

The system must understand and communicate that:
-   **Bluff detection can never be a certainty.** It is a probabilistic assessment based on patterns and deviations.
-   **Opponent reads require a meaningful sample size.** A read based on three hands is a guess; a read based on 300 is a pattern.
-   **Confidence must degrade when data quality is low or signals are conflicting.** The system must know when it doesn't know.

To enforce this, we will introduce a `data_quality` object into our backend response, which will directly inform the UI's presentation of confidence.

### Data Quality & Confidence Schema

This object will be a sibling to the `advice` and `tactical_data` blocks.

```json
{
  "data_quality": {
    "sample_size": 18,
    "reliability": "Low",
    "confidence_decay_active": true,
    "decay_reason": "Low sample size for opponent in this position."
  }
}
```

### Core Reliability Concepts

-   **Sample-Size-Aware Reasoning:** The core logic will be fundamentally different when `sample_size < 50`. Below this threshold, recommendations will be heavily weighted towards game-theory principles and away from opponent-specific tendencies.
-   **Reliability Scoring:** A simple score (`Low`, `Medium`, `High`) will be calculated based on sample size, session recency, and the variance of the opponent's play.
-   **Confidence Degradation:** The `confidence_label` in the `advice` block will be automatically downgraded if `data_quality.reliability` is `Low`. A "High Confidence" read is impossible with low-reliability data.
-   **Uncertainty Escalation:** When conflicting signals are detected (e.g., opponent stats suggest a nit, but the betting line is maniacal), the system will escalate uncertainty, reduce confidence, and highlight the contradiction in the explanation.

### Trust-Centric Language

Our narrative engine will adopt language that reflects this uncertainty.

Instead of:
> “Opponent is bluffing.”

Use:
> “Opponent is showing signs of increased bluff frequency in this session compared to their baseline.”

Or, with low data:
> “This betting line can sometimes indicate a bluff, but we have limited history on this opponent.”

### UI Recommendations for Trust

-   **Low-Confidence Warnings:** A prominent but non-alarming label (e.g., a yellow "Low Read Reliability" badge) when data quality is poor.
-   **"Insufficient Data" States:** For new opponents, the opponent-specific modules of the UI should be explicitly disabled and show "Insufficient Data to Generate Read."
-   **Uncertainty Indicators:** Use visual cues like dashed borders, faded colors, or subtle pulsing animations on elements where confidence is low.
-   **Confidence Transparency:** Allow users to tap a confidence label (e.g., "Medium Confidence") to see a brief explanation from the `decay_reason` field.

**Our mandate is clear: Trust is more important than appearing intelligent.**

---

## 12. Real-Time Performance & Live Play Constraints

This is a **live play assistant**, not a post-game analytics dashboard. Every millisecond of latency degrades the user experience and erodes trust. The system must feel instantaneous to be useful in the high-pressure environment of a live poker hand.

### Hard Performance Requirements

-   **Advice Rendering Target:** The P95 for advice rendering (from user input to UI update) must be **under 500ms**.
-   **Instantaneous UI:** All primary UI interactions (typing bets, moving the button) must update at 60fps with no jank.
-   **Non-Blocking Gameplay:** Narrative generation or heavy computation must **never** block the user from entering the next action in the hand.
-   **Lazy-Loaded Tactical Data:** Tactical Mode calculations (e.g., detailed EV breakdowns) should lazy-load after the primary strategic advice is displayed.
-   **Asynchronous Analysis:** All non-critical computations (e.g., updating historical stats) must be offloaded to background workers.

### Architectural Recommendations

-   **Memoized Calculations:** Use aggressive memoization (e.g., via `React.useMemo` or server-side caching) for pure functions like equity calculation.
-   **Cached Opponent Stats:** Opponent data should be fetched once at the start of a session and held in a hot, in-memory cache on the server.
-   **Optimistic UI Updates:** For simple actions (like inputting a bet), the UI should update immediately, assuming success, while the backend call proceeds in the background.
-   **Background Analysis Workers:** A dedicated queue (e.g., Celery with Redis) for post-hand analysis and updating long-term opponent statistics.
-   **Lightweight Strategic Rendering:** The default "Strategic Mode" must be extremely lightweight, rendering only the pre-computed narrative from the API without performing any client-side calculations.

### Degraded Mode Strategy

The system must be resilient to calculation timeouts or failures. If an advanced analysis (e.g., bluff detection) fails or takes too long:
1.  The API gateway will time out the request to the analysis service.
2.  The backend will return a simplified response containing only game-theory-optimal advice (based on board texture, position, etc.).
3.  The `data_quality` object will indicate a `reliability` of `Degraded`.
4.  The UI will render this simplified advice, clearly indicating that a full read was not possible for this hand.

The UI must **never freeze** or show a loading spinner in the middle of a hand. **Responsiveness is part of perceived intelligence.**

---

## 13. Full Session Flow UX

The product experience is not a collection of individual widgets; it is the **complete, end-to-end gameplay loop.** The UX must be designed to handle the entire lifecycle of a poker session, including its inherent chaos.

### End-to-End Session Flow

1.  **Session Creation:** One-click start, pre-filled with common game types (e.g., "$1/$2 No-Limit Hold'em").
2.  **Player Setup:** Fast player entry with autocomplete from opponent history. Drag-and-drop seating. Quick stack entry.
3.  **Hand Start:** Automatically rotates the button and posts blinds.
4.  **Action Tracking:** Ultra-fast, sequential input of actions (Fold, Check, Call, Bet/Raise amount). The UI should guide the user to the next player to act.
5.  **Live Recommendations:** Advisor HUD updates in real-time as actions are entered.
6.  **Showdown Handling:** Simple interface to enter hole cards for players who reach showdown. The system automatically determines the winner(s) and calculates side pots.
7.  **Post-Hand Analysis:** A brief, skippable summary of the hand's outcome and key strategic takeaways.
8.  **Session Ending:** Manually end the session, which triggers the final stat aggregation.
9.  **Historical Stat Updates:** Background workers process the session data, updating the `opponent_historical_stats` for all players involved.

### Handling Real-World Poker Chaos

The UX must gracefully handle the inevitable interruptions and errors of a live game.
-   **Ultra-Fast Action Entry:** The primary input should be a numeric keypad for bet sizes and large buttons for actions, minimizing typing.
-   **Undo Support:** A crucial feature. A simple "Undo Last Action" button that rewinds the game state.
-   **Correction Workflows:** The ability to pause and edit a past action in the current hand history.
-   **Auto-Save State:** The current session state (players, stacks, current hand) must be saved locally on every action to prevent data loss on browser crash or refresh.
-   **Fast Hand Resets:** A prominent "Next Hand" button that immediately archives the current hand and sets up the next one.
-   **Error Recovery:** If the user inputs an illogical action (e.g., a bet smaller than the minimum raise), the UI should provide clear, constructive feedback instead of just rejecting the input.

The system must anticipate and seamlessly handle:
-   **Misclicks:** Corrected with the Undo feature.
-   **Seat Changes:** Handled by the drag-and-drop table UI between hands.
-   **Players Leaving/Joining:** Players can be added or removed between hands without disrupting the session flow.
-   **Rebuy Interruptions:** The inline stack editor allows for fast updates without a modal.

---

## 14. Opponent Memory Decay & Adaptive Intelligence

Poker players are not static. They tilt, they learn, they adapt. A truly intelligent memory system must account for this behavioral drift. Old reads must become less reliable over time.

### Enhancements to Opponent Memory

-   **Weighted Recent Sessions:** The stat aggregation engine will weigh hands from the current session and the last 3 sessions more heavily than older data.
-   **Stat Decay:** A cron job will periodically apply a decay factor to the `hands_sampled` value for all stats, slowly reducing the weight of very old data.
-   **Behavioral Drift Handling:** The system will track session-by-session stats and compare them to a player's long-term baseline. Significant deviations will be flagged.
-   **Confidence Adjustments Over Time:** The `reliability` score for an opponent will be higher if they were played against yesterday versus six months ago, even with the same total hand sample.

### Adaptive Archetype Recalculation

An opponent's archetype (e.g., "Tight Aggressive") should not be a permanent label. It will be recalculated after each session. The UI will reflect changes in playstyle.

**Example Adaptive Narrative:**

> "Aman — **Shifting to Loose Passive**"
> "Historically an aggressive player, but his pre-flop raise frequency has dropped significantly over the last 50 hands."

This makes the system feel **alive and adaptive, not like a static database.** It demonstrates that the AI is learning alongside the user.

---

## 15. Hybrid AI Reasoning Architecture

A critical architectural decision to ensure reliability and safety is to **avoid purely generative AI for core strategic advice.** LLMs are prone to hallucination, inconsistency, and generating generic "strategic fluff" that is actively harmful in a high-stakes environment like poker.

We will implement a **Hybrid AI Reasoning Architecture** that combines deterministic logic with controlled narrative generation.

### The Three Layers of Reasoning

**Layer 1: Deterministic Poker Logic (The Ground Truth)**
This layer is pure, hard-coded poker mathematics and heuristics. It is not an LLM.
-   **Inputs:** Hand state, board texture, opponent stats (from our DB).
-   **Processes:**
    -   Equity calculation (vs. an assumed range).
    -   Pot odds calculation.
    -   Behavioral heuristic checks (e.g., `if opponent_cbet_flop < 40% and opponent_bets_turn, increase strength_assumption`).
-   **Output:** A structured object of raw tactical data and logical flags. `{"equity": 0.61, "pot_odds": 0.33, "flags": ["OPPONENT_DEVIATES_FROM_BASELINE"]}`.

**Layer 2: Structured Semantic Interpretation (The Translator)**
This layer takes the deterministic output from Layer 1 and translates it into the structured semantic concepts defined in our `advice` schema. This is also rule-based, not generative.
-   **Inputs:** The raw object from Layer 1.
-   **Processes:** A series of mapping functions.
    -   `mapEquityToLabel(0.61)` -> `"Strong Favorite"`
    -   `mapFlagsToFactors(["OPPONENT_DEVIATES_FROM_BASELINE"])` -> `{ "type": "warning", "title": "Unusual Line", ... }`
-   **Output:** The complete, structured `advice` object (minus the final summary).

**Layer 3: Controlled Narrative Rendering (The Storyteller)**
This is the *only* layer where a generative model (or template engine) is used. It operates under strict constraints.
-   **Inputs:** The fully populated structured `advice` object from Layer 2.
-   **Process:** The LLM or template engine is given a highly-constrained prompt: *"Based ONLY on the following JSON object, assemble a human-readable summary. Do not invent any new reasoning. Do not use overly confident language."*
-   **Output:** The final `summary` and `verdict` strings.

This architecture ensures the **narrative layer summarizes reasoning, it does NOT invent reasoning.** It grounds our AI in mathematical reality and prevents the generation of dangerous, hallucinated advice. We must be allergic to **"GPT-style strategic fluff."**

---

## 16. Failure State UX & Uncertainty Handling

A trustworthy system is defined by how it behaves when it's not confident. The UI must be designed to gracefully handle and clearly communicate states of uncertainty. Acting confident when the data is weak is a cardinal sin.

### Key Scenarios for Uncertainty

-   **Insufficient Opponent History:** The primary source of uncertainty.
-   **Chaotic Multiway Pots:** The complexity of range calculations increases exponentially, reducing model confidence.
-   **Conflicting Signals:** When opponent stats contradict their current betting line.
-   **High-Variance Situations:** Spots where the range of outcomes is extremely wide (e.g., set-over-set coolers).
-   **Unusual Betting Lines:** Unfamiliar or bizarre lines that don't fit known patterns.

### UX for Communicating Failure & Uncertainty

When the backend returns a response with low `reliability` or specific uncertainty flags, the UI must adapt.

**Example Narrative Snippets:**

> **"Insufficient Read on Opponent"** - The most common and important state.
> **"This spot is highly volatile with a wide range of outcomes."**
> **"Recommendation confidence reduced due to conflicting signals."**
> **"Limited historical data available; advice is based on general principles."**

### UI Guidance for Uncertainty

-   **Neutral Colors:** In high-confidence spots, our "CALL" button might be a vibrant green. In a low-confidence spot, it should be a neutral grey or white.
-   **Softer Language:** The `verdict` should change from "Call the Bluff" to "Consider Calling."
-   **Expanded Explanations:** The system can default to showing more of the `factors` to help the user understand *why* the spot is uncertain.
-   **Fallback Summaries:** The narrative engine will have pre-canned summaries for common failure states, like "This is a complex multi-way pot where precise advice is difficult. Focus on pot odds and your hand's raw potential."

Good AI systems don't pretend to be omniscient. **They communicate uncertainty clearly and hand control back to the user.**

---

## 17. Mobile-First Live Poker UX

The primary use case for this product is not at a desktop. It is at a live poker table, held in one hand, often under a dim restaurant light, while the user is simultaneously handling chips and cards under the pressure of a 30-second decision clock. The mobile experience is the *only* experience that matters.

### Core Mobile Constraints & Requirements

-   **One-Handed Operation:** All primary controls must be reachable with a single thumb.
-   **Glanceability:** Information must be digestible in a 1-2 second glance.
-   **Large Touch Targets:** Reduce misclicks under pressure.
-   **Low-Light Readability:** High-contrast color schemes (like our dark theme) are essential.
-   **Minimal Typing:** Leverage buttons, steppers, and sliders over free-text input wherever possible.
-   **Fast Interaction Loops:** Getting from action input to advice should require the fewest possible taps.

### Mobile-Specific UI/UX Recommendations

-   **Bottom-Sheet Interactions:** Instead of modals that cover the screen, use non-invasive bottom sheets for secondary actions (e.g., editing a player).
-   **Swipe-Based Quick Actions:** Consider swipe gestures on player avatars for common actions like "Remove Player."
-   **Compact Strategic Cards:** The main `AdvisorHUD` should be a compact, self-contained card that doesn't occupy the entire screen.
-   **Large Semantic Indicators:** The `verdict` and `confidence_label` must be the largest, most prominent elements on the screen.
-   **Haptic Feedback:** Use subtle haptic feedback on actions like confirming a bet or receiving new advice to provide tactile confirmation without needing to look.

The mobile experience cannot be a down-sized version of a desktop web app. It must be designed from the ground up to be a frictionless, glanceable tool for a player in the heat of the moment.

---

## 18. Product Scope Boundaries & Non-Goals

Product discipline is as important as technical architecture. To prevent feature bloat and maintain focus, we must be explicit about what PokerSense AI is **not**.

### Explicit Non-Goals

-   **Not a GTO Solver Replacement:** We provide strategic advice rooted in GTO principles, but we do not expose complex solver outputs or claim to be a perfect GTO engine. Our goal is exploitability and clarity, not theoretical perfection.
-   **Not an Autonomous Poker AI:** The tool is an advisor, not a player. It will never make decisions or take actions on behalf of the user.
-   **Not OCR Automation:** We will not pursue reading physical cards or chips via a camera. All input is manual to ensure accuracy and avoid legal/ethical gray areas.
-   **Not a Real-Money Bot:** The product is strictly forbidden from integrating with any real-money online poker client. It is a decision-support tool for live or personal play only.
-   **Not Guaranteed Winning Intelligence:** The product is an informational tool designed to assist a player's decision-making process. It does not guarantee profit or success.

### The Guiding Principle of Scope

**Every proposed feature must answer "Yes" to one of these two questions:**
1.  Does it significantly **reduce the user's cognitive load** during a live hand?
2.  Does it meaningfully **improve the clarity and trustworthiness** of the strategic advice?

If the answer is no, the feature is rejected. We will actively fight against:
-   **Unnecessary Analytics:** No vanity charts or data dumps that don't lead to a direct, actionable decision.
-   **Metric Overload:** The "Tactical Mode" will be curated and will not become a dumping ground for every possible poker statistic.
-   **Complexity for its Own Sake:** We will never expose an internal system's complexity just to make the product seem more "advanced."

---

## 19. Strategic Product Philosophy

In summary, after this architectural evolution, PokerSense AI's identity will be clear, focused, and trustworthy.

It should ultimately feel like:
-   **A Calm, Strategic Advisor:** It provides clarity in moments of high-pressure confusion.
-   **A Trusted Tactical Memory System:** It reliably remembers details so the user can focus on the present moment.
-   **A Readable Poker Intelligence Layer:** It translates complex data into simple, actionable narratives.

It must never feel like:
-   **An Intimidating Analytics Terminal:** It should empower, not overwhelm.
-   **An AI Gimmick:** Its intelligence must be grounded, reliable, and in all cases, genuinely useful.
-   **A Solver Dump:** It synthesizes, explains, and advises; it does not simply output raw data.

Our final measure of success is not the number of calculations we can perform or the complexity of our models. **The product succeeds when users stop thinking about the software itself and simply feel more strategically informed, confident, and in control of their game.**
---

# 20. Deterministic Decision Pipeline

To ensure maximum reliability and prevent generative hallucination, the PokerSense intelligence engine must operate as a deterministic, multi-stage pipeline. Every piece of advice is the result of a verifiable, sequential process. Narrative generation is the final, highly-constrained step, not the primary function. It summarizes the output of the preceding deterministic stages.

The core architectural principle is: **Narrative summarizes evidence; it does not create it.**

### High-Level Pipeline Architecture

The flow from raw input to user-facing advice follows a strict, non-negotiable sequence. Each stage's output serves as the validated input for the next.

```text
[Raw Hand State] → Validation Layer → Range Engine → Tactical Engine → Confidence Engine → Semantic Mapping → Narrative Renderer → Response Validator → [UI Delivery]
```

### Stage-by-Stage Breakdown

1.  **Raw Hand State Input:**
    -   **Input:** JSON object from the frontend representing the current table state (stacks, positions, pot size, action history).
    -   **Function:** Ingestion.

2.  **Validation Layer:**
    -   **Input:** Raw Hand State.
    -   **Function:** Ensures game state integrity. Checks for illegal actions, inconsistent stack sizes, or out-of-order moves.
    -   **Output:** A validated, sanitized `game_state` object. If validation fails, the pipeline halts and returns a `STATE_INVALID` error.
    -   **Constraint:** No advice can be generated from an invalid state.

3.  **Range Engine:**
    -   **Input:** Validated `game_state`.
    -   **Function:** Assigns probable hand ranges to each opponent based on position, pre-flop action, and historical VPIP/PFR data from the Opponent Memory System.
    -   **Output:** Structured `opponent_ranges` object.
    -   **Constraint:** Ranges are based on statistical archetypes and tracked history, not real-time "reads." The engine's limitations (e.g., no perfect range modeling) are codified here.

4.  **Tactical Engine:**
    -   **Input:** `game_state`, `opponent_ranges`.
    -   **Function:** Purely mathematical computation. Calculates pot odds, equity (our hand vs. `opponent_ranges`), expected value, and identifies key tactical factors (e.g., "Player has position," "Board is draw-heavy").
    -   **Output:** A structured `tactical_analysis` object containing only numerical data and boolean flags. Example: `{"equity": 0.67, "pot_odds": 0.33, "flags": ["HAS_POSITIONAL_ADVANTAGE"]}`.

5.  **Confidence Engine:**
    -   **Input:** `tactical_analysis`, `data_quality` object (from Opponent Memory).
    -   **Function:** Assesses the reliability of the tactical analysis. It cross-references `data_quality.sample_size` and `data_quality.reliability` with the strength of the tactical signals.
    -   **Output:** A `confidence_score` (0.0 to 1.0) and a list of `uncertainty_factors`.
    -   **Constraint:** A high-equity hand against an opponent with `sample_size: 10` will have its confidence score programmatically degraded.

6.  **Semantic Mapping:**
    -   **Input:** `tactical_analysis`, `confidence_score`.
    -   **Function:** Translates raw numbers and flags into the structured, human-readable labels defined in this document (e.g., 67% equity becomes "Strong Favorite"). This is a rule-based mapping, not a generative process.
    -   **Output:** The pre-narrative `advice` object, fully populated with all structured data points except for the final text summary.

7.  **Narrative Renderer:**
    -   **Input:** The fully populated `advice` object.
    -   **Function:** The *only* step where controlled text generation occurs. It uses a template-based system or a heavily constrained LLM prompt to assemble the `summary` and `verdict` strings from the structured semantic data.
    -   **Anti-Hallucination Rule:** **No explanation may contain reasoning absent from the structured tactical analysis provided to it.** The renderer's job is to synthesize, not invent.

8.  **Response Validator:**
    -   **Input:** The final, complete response JSON.
    -   **Function:** A final schema validation and sanity check. Ensures the generated narrative doesn't contradict the tactical data (e.g., says "High Confidence" when the confidence score was low).
    -   **Output:** Validated JSON for the frontend.

9.  **UI Delivery:**
    -   **Function:** The frontend receives the validated JSON and renders the UI components. It does not perform its own reasoning.

This pipeline ensures that every piece of advice is traceable, verifiable, and grounded in deterministic calculations, drastically reducing the risk of unsafe, hallucinated outputs.

---

# 21. AI Safety Constraints for Narrative Generation

To prevent the generation of misleading, overconfident, or outright hallucinated poker reasoning, the Narrative Renderer (Stage 7) must operate under a strict set of safety constraints. The system's primary directive is to maintain user trust, which is immediately destroyed by fabricated advice.

Our philosophy: **The system must sound probabilistic and evidence-based, not omniscient.**

### Prohibited Narrative Generation Actions

The AI system, particularly the Narrative Renderer, **MUST NOT**:
-   Invent or speculate on specific opponent holdings (e.g., "He probably has Ace-King").
-   Invent or overstate blocker effects without explicit calculation from the Tactical Engine.
-   Invent range assumptions not provided by the Range Engine.
-   Invent or reference GTO solver outputs that were not part of the input.
-   Invent bluff reads or "soul reads" not backed by statistical deviation flags from the Tactical Engine.
-   Invent or inflate confidence levels beyond what the Confidence Engine has determined.
-   Reference player psychology, mood, or physical tells.

### Mandatory Origin of Information

Every narrative statement must originate **exclusively** from one of the following validated sources provided in its input object:
-   **Tracked Statistics:** From the `opponent_stats` object.
-   **Deterministic Calculations:** Equity, EV, and pot odds from the `tactical_data` object.
-   **Explicit Heuristics:** Boolean flags set by the Tactical Engine (e.g., `FLAG_OPPONENT_AGGRESSION_SPIKE`).
-   **Validated Assumptions:** The range models provided by the Range Engine.

### Architectural Safety Constraints

To enforce these rules, the following architecture is mandated:
1.  **Template-Backed Generation:** The primary method for narrative generation should be a sophisticated template engine. The structured `advice` object populates predefined sentence structures.
2.  **Schema-Constrained Outputs:** The final JSON response must be validated against a strict schema. Any deviation results in an error, not a malformed response.
3.  **Limited Vocabulary Layers:** The system should use a curated dictionary of poker terms. This prevents an LLM from using ambiguous or overly confident language.
4.  **Semantic Mapping Dictionaries:** Use explicit key-value mappings to translate tactical flags into sentence fragments, ensuring consistency.
5.  **Prohibited Language Patterns:** Implement a post-generation filter to scan for and reject outputs containing "tells," certainty claims, or other forbidden phrases (e.g., "I know," "he definitely has," "for sure").

### Examples of Safe vs. Unsafe Narrative

**UNSAFE (Hallucinated, Omniscient):**
> "Your opponent almost certainly missed his flush draw on the river and is now bluffing. He looks frustrated. Your pair of tens is good here, so you should call."

**SAFE (Probabilistic, Evidence-Based):**
> "The opponent's betting line is consistent with some missed draws given the board runout. While your hand has showdown value, the large bet size indicates a polarized range. The decision has medium variance, but pot odds are favorable for a call."

The latter is more trustworthy because it's transparent about the reasoning process and acknowledges uncertainty. It provides the user with the factors for a decision, rather than making an unverifiable claim.

---

# 22. Poker Intelligence Engine Specification

The Poker Intelligence Engine is the analytical core of the system. It is crucial to define its capabilities and, more importantly, its limitations. The engine is an **inferential tool**, not a predictive one. It analyzes available data to produce the most probable assessment; it does not "know" the future or an opponent's hidden state.

### Core Principles

-   **Explainable, Not Magical:** Every inference must be traceable to a specific model or heuristic.
-   **Conservative by Default:** When data is sparse or signals are conflicting, the engine must default to game-theory-optimal (GTO) baseline advice rather than attempting a high-variance exploit.
-   **Not a Perfect Solver:** The engine uses simplified models and heuristics to achieve real-time performance. It is not a replacement for offline GTO solvers.

### Engine Components & Limitations

1.  **Range Estimation:**
    -   **Methodology:** Uses a library of pre-calculated opening ranges based on position. These base ranges are then weighted and filtered based on the opponent's historical VPIP/PFR from the Opponent Memory System.
    -   **Limitations:**
        -   The model does not dynamically construct ranges street-by-street in real-time. It filters a master range.
        -   It cannot account for sophisticated opponent strategies like mixing frequencies or balancing ranges perfectly.
        -   **No perfect range reading is possible.** The output is always a probability distribution of likely holdings.

2.  **Bluff Detection Methodology:**
    -   **Methodology:** This is a pattern-recognition system, not a mind-reader. It works by flagging statistical deviations from a player's baseline behavior, correlated with board texture.
    -   **Inputs:** Opponent's historical Aggression Factor (AF), C-Bet frequency, WTSD% (Went to Showdown), and the current betting line.
    -   **Example Heuristic:** `IF opponent_cbet_freq < 40% AND current_action == "bets turn" AND board_is_dry THEN raise FLAG_POTENTIAL_BLUFF`.
    -   **Limitations:**
        -   Highly dependent on sample size. A "bluff read" with fewer than 100 hands on an opponent is low-confidence by definition.
        -   **It cannot guarantee exploit detection.** It can only identify lines that are *consistent* with a bluff based on past actions.

3.  **Aggression Modeling:**
    -   **Methodology:** Tracks a rolling Aggression Factor/Frequency over the last N hands (e.g., 200) and a separate session-only AF. A spike in the session AF compared to the long-term baseline is a significant flag.
    -   **Limitations:** Does not understand the *reason* for aggression (e.g., tilt, table dynamics, genuine good hands). It only quantifies the behavior.

4.  **Showdown Learning:**
    -   **Methodology:** When a hand goes to showdown, the engine logs the opponent's actions on each street along with their specific holding. This data is used to refine the Range Engine's filters over time.
    -   **Limitations:** This is a slow learning process that requires thousands of hands to become highly accurate.

5.  **Behavioral Confidence Weighting:**
    -   **Methodology:** The Confidence Engine (Stage 5) uses a Bayesian approach. It starts with the confidence from the pure tactical model and then updates it based on the `data_quality` from the Opponent Memory.
    -   **Example:** A strong tactical signal (`equity: 85%`) might start with 0.9 confidence. If the opponent `sample_size` is low, the final confidence is programmatically reduced: `0.9 * 0.5 (low_data_penalty) = 0.45`.
    -   **Recommendations:** Implement explicit confidence penalties for small sample sizes, long periods since the last session, and high-variance opponents.

The engine's intelligence comes from the disciplined synthesis of these limited, imperfect components. Its value is in providing a consistently rational, evidence-based perspective, not in making perfect predictions.

---

# 23. Data Integrity & Session Consistency

Live poker sessions are fluid, chaotic, and highly error-prone from a data-entry perspective. A corrupted or inconsistent game state renders all subsequent strategic advice worthless, and potentially harmful. The system's architecture must be fundamentally resilient to data integrity failures.

**Core Principle:** No strategic advice should *ever* be rendered against an invalid game state.

### Common Real-World Data Corruptions

The architecture must anticipate and handle:
-   **Duplicate Actions:** User accidentally double-clicks the "Call" button.
-   **Invalid Bet Sizing:** Inputting a raise amount that is below the legal minimum.
-   **Out-of-Order Turns:** Trying to log an action for a player who is not next to act.
-   **Inconsistent Stack Sizes:** A player's stack after a bet does not match `previous_stack - bet_size`.
-   **Player Removal Mid-Hand:** A player leaves the table during a hand.
-   **Undo Conflicts:** Attempting to undo an action that has subsequent actions depending on it.
-   **Desynchronized Session State:** Frontend and backend states diverge due to a network error.

### Architectural Recommendations for Robustness

1.  **Event-Sourced Hand History:**
    -   Do not model the game state as a single, mutable object. Instead, model it as an ordered log of immutable `action` events.
    -   The current `game_state` is a projection, rebuilt by replaying the event log from the start of the hand.
    -   **Benefit:** This creates an auditable, replayable history of the hand, making debugging and state correction trivial.

2.  **Immutable Action Logs:**
    -   Once an action is accepted by the backend, it cannot be edited. To correct a mistake, a new `CORRECTION` or `UNDO` event is appended to the log.
    -   **Benefit:** Prevents complex and error-prone mutations of historical state.

3.  **State Checksum / Hashing:**
    -   The backend can send a hash of the current game state along with its advice. The frontend can verify that its local state hash matches before rendering the advice, preventing desynchronization issues.

4.  **Action Validation Engine:**
    -   This is the core function of the Validation Layer (Stage 2). It is a pure function: `validateAction(currentState, proposedAction) -> [isValid, errorReason]`.
    -   This engine contains all the rules of No-Limit Hold'em (bet sizing, turn order, etc.) and is the single source of truth for action legality.

5.  **Session Snapshots:**
    -   Periodically, or between hands, the entire session state (all players, stacks, and settings) should be snapshotted and persisted. This allows for full session recovery.

6.  **Rollback & Correction Support:**
    -   The "Undo" feature should not simply pop an item from an array. It should append an `UNDO_ACTION` event to the log. The state projection logic then knows how to correctly rebuild the previous state.

By treating the game state as a derivative of an immutable log of events, the system gains immense resilience and auditability. This architecture is more complex initially but is far safer and more maintainable for a real-world, error-prone application.

---

# 24. Developer Execution Constraints

This section provides explicit, non-negotiable constraints for any developer—human or AI—working on the PokerSense system. These rules are designed to enforce architectural integrity, prevent common implementation pitfalls, and reduce the likelihood of hallucinated or tightly-coupled code.

**The Prime Directive:** The frontend renders intelligence; the backend generates intelligence. There are no exceptions.

### Prohibited Implementation Patterns

**DO NOT:**
-   **Tightly couple UI components to poker logic.** A React component should not know how to calculate pot odds.
-   **Generate narrative text directly from raw user prompts or unvalidated state.** All narrative generation must flow through the deterministic pipeline.
-   **Place poker reasoning or strategic heuristics in frontend components.** All `if/else` logic related to poker strategy belongs in the backend intelligence engine.
-   **Duplicate tactical calculations across services.** Equity, EV, and other math must be computed in exactly one place: the Tactical Engine.
-   **Expose raw internal engine state directly to the UI.** The UI should consume the clean, validated, and structured JSON response, not internal flags or intermediate values.
-   **Bypass the Confidence Engine or its validation checks.** The UI must respect and visibly render the confidence level provided by the backend.
-   **Hardcode strategic labels in the frontend.** A string like "Bluff Catching" must originate from the `strategic_theme` field in the backend response, not from an `if` statement in a UI component.
-   **Implement optimistic UI updates for strategic advice.** While fine for simple inputs, the advice itself must only be rendered *after* receiving a validated response from the backend.

### Mandated Architectural Patterns

1.  **Shared Typed Schemas:**
    -   Use a shared library (e.g., a private `npm` package or monorepo workspace) to define TypeScript types/interfaces for all API requests and responses.
    -   This ensures that the frontend and backend agree on the shape of data, catching errors at compile time.

2.  **Centralized Intelligence Engine:**
    -   All poker intelligence—from range calculation to semantic mapping—must reside within a dedicated, isolated backend service or module group.

3.  **Backend-Owned Reasoning:**
    -   The final JSON response from the backend is the **single source of truth**. The frontend's job is to render this object faithfully.
    -   The frontend should be "dumb" concerning poker strategy. It knows how to display a "High Confidence" badge, but it doesn't know what "High Confidence" means or how it was calculated.

4.  **Frontend as Presentation Layer Only:**
    -   Frontend code should be exclusively concerned with state management (e.g., toggling Tactical Mode), user input, and rendering the components described by the backend's response object.

Adherence to these constraints will produce a decoupled, scalable, and reliable system. Violation of these constraints will lead to a brittle, unmaintainable monolith where logic is smeared across the stack, making it impossible to validate or improve.

---

# 25. Incremental Build Strategy

The vision outlined in this document is ambitious. Attempting to build the entire system in one monolithic effort would be a critical mistake, likely resulting in over-engineering and delays. A phased, incremental approach is mandatory to manage risk and deliver value quickly.

**Core Principle:** A stable, fast, and trusted system is more valuable than a theoretically advanced but unreliable one. Prioritize the user's core loop.

### Phase 1: Core Stability & Foundational Advice
*Goal: A rock-solid, fast hand tracker with basic, reliable advice.*
-   **Features:**
    -   Stable, fast, and reliable hand tracking for a full game flow.
    -   Action validation engine (enforcing poker rules).
    -   Basic `SmartAdvisor` backend that provides only GTO-based advice (equity, pot odds) without opponent modeling.
    -   Simple Opponent Memory: Store opponent names and basic notes, but no automated stats yet.
    -   A single, static "Strategic Mode" UI that displays the basic advice.
-   **Warnings:**
    -   **DO NOT** build adaptive AI or complex bluff detection.
    -   **DO NOT** over-engineer the UI. Focus on speed and stability.

### Phase 2: Confidence & Semantic Context
*Goal: Make the advice smarter and more trustworthy by layering on context and uncertainty.*
-   **Features:**
    -   Implement the full Opponent Memory System for tracking core stats (VPIP, PFR, Aggression).
    -   Launch the Confidence Engine. Advice is now weighted by sample size.
    -   Launch the Semantic Mapping layer. The UI can now display "Strong Favorite" instead of "67%."
    -   Introduce the "Strategic Mode" vs. "Tactical Mode" toggle. Tactical mode shows the underlying numbers.
-   **Warnings:**
    -   Narrative generation should still be template-based and simple. Avoid complex LLM integration.

### Phase 3: Adaptive Modeling & Deeper Tactics
*Goal: The AI starts to feel alive and adapts to specific opponents.*
-   **Features:**
    -   Implement the advanced bluff detection and behavioral modeling heuristics.
    -   Introduce session-vs-baseline analysis and adaptive archetypes ("Player is shifting to passive").
    -   Roll out the full "Explanation Engine" with prioritized, scannable factors.
    -   Launch advanced session analytics for post-game review.
-   **Warnings:**
    -   Latency is a major risk here. Ensure new models are fast and have hard timeouts.

### Phase 4: Narrative Refinement & Trust Optimization
*Goal: Polish the human-AI interaction to perfection.*
-   **Features:**
    -   Integrate a more sophisticated (but still constrained) Narrative Renderer to create more fluid summaries.
    -   A/B test different narrative styles to see what builds the most user trust.
    -   Refine the UI for communicating uncertainty (e.g., animations, subtle color shifts).
    -   Improve probabilistic reasoning models.
-   **Warnings:**
    -   This phase is pure refinement. Do not add major new features. Focus on making the existing system feel more intelligent and trustworthy.

This phased approach ensures that a usable, valuable product exists at every stage, while de-risking the more complex and speculative AI features until the core foundation is proven.

---

# 26. Hallucination Risk Audit

This section serves as a formal, internal audit of the areas within the PokerSense AI system most vulnerable to AI hallucination, unreliable execution, and catastrophic failures of user trust. For each area, we identify the risk, the potential failure mode, and the mandatory mitigation strategy.

**Final Principle:** Every intelligent claim made by the system must be traceable to deterministic evidence in its input data.

### 1. Bluff Detection

-   **Risk:** The highest risk of catastrophic failure. A wrongly-asserted "bluff" call that loses a large pot will instantly and permanently destroy user trust.
-   **Hallucination Mode:** The AI invents a "read" based on insufficient data or presents a low-probability statistical anomaly as a certainty. It says "He is bluffing" instead of "His line is consistent with bluffs."
-   **Mitigation Strategy:**
    1.  **No Direct Claims:** The system is forbidden from ever stating "the opponent is bluffing." It can only state that the opponent's actions are statistically consistent with patterns previously associated with bluffs.
    2.  **Hard Sample Size Gate:** The bluff detection module is completely disabled for any opponent with `< 100` hands in the database. Below this, only GTO advice is given.
    3.  **Mandatory Confidence Degradation:** Any bluff-related flag raised by the Tactical Engine must trigger a significant confidence penalty in the Confidence Engine if the sample size is below a higher threshold (e.g., 500 hands).
    4.  **UI Transparency:** The UI must display the sample size alongside any bluff-related analysis.

### 2. Range Assumptions

-   **Risk:** The engine assumes an incorrect or overly narrow range for an opponent, leading to drastically incorrect equity calculations.
-   **Hallucination Mode:** The AI acts as if it "knows" the opponent's range is exactly `[AA, KK, AK]`, when in reality it could be much wider.
-   **Mitigation Strategy:**
    1.  **Probabilistic Ranges:** The Range Engine must always work with a probability distribution over a wide range of hands, never a small, discrete set.
    2.  **Conservative Defaults:** For unknown opponents, the engine must use wide, GTO-based default ranges, not a narrow "average player" range.
    3.  **Explicit Uncertainty in UI:** The Tactical Mode can include a visualization showing the assumed range, making it transparent to the user.

### 3. Player Classification (Archetypes)

-   **Risk:** The system mislabels a player (e.g., calls a "Nit" a "Maniac"), leading the user to make profoundly incorrect strategic adjustments.
-   **Hallucination Mode:** The AI labels a player based on a few dozen hands, treating a short-term statistical variance as a permanent personality trait.
-   **Mitigation Strategy:**
    1.  **High Sample Size Threshold:** Archetype labels are only applied after a significant hand count (e.g., `> 300 hands`).
    2.  **Use of "Shifting" Language:** The system should describe behavior rather than applying permanent labels. E.g., "Playing more aggressively this session" is safer than "Is an aggressive player."
    3.  **Show the Numbers:** The UI should always show the underlying VPIP/PFR stats next to the archetype label, allowing the user to sanity-check the classification.

### 4. Narrative Confidence

-   **Risk:** The generated text sounds more confident than the underlying mathematical analysis warrants.
-   **Hallucination Mode:** A constrained LLM, in its attempt to be helpful and fluent, uses confident-sounding filler language (e.g., "Clearly, the best move is...") that wasn't present in its structured input.
-   **Mitigation Strategy:**
    1.  **Strict Prompt Engineering:** The prompt for the Narrative Renderer must explicitly forbid words of certainty and instruct the model to adopt a probabilistic, advisory tone.
    2.  **Post-Generation Filtering:** A validation layer must scan the generated text for a blacklist of "certainty words" ("obviously," "definitely," "for sure," "no doubt") and trigger a regeneration or error if they are found.
    3.  **Direct Confidence Mapping:** The narrative must explicitly state the confidence level provided by the Confidence Engine.

By rigorously auditing and mitigating these risk areas, we build a system that is not only intelligent but, more importantly, safe, reliable, and worthy of our users' trust in high-stakes situations.
