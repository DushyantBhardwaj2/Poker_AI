# 🃏 PokerSense AI: "God-Mode Operator" UX Plan (Discord Poker Night Inspired)

## 1. The Core Concept: Tactical Omniscience
Discord's *Poker Night* works brilliantly because it maps complex state (pots, turns, bets) into intuitive, spatial visuals. 
For **PokerSense AI**, we are adapting this into a **"God-Mode Operator"** interface. You (the user) are tracking a live game. You input every bet, raise, refill, and player exit. 

**The Goal:** We want the frictionless, spatial, and visual clarity of *Poker Night*, but skinned in our elite, dark-mode tactical aesthetic, keeping input speeds under 1 second per action.

---

## 2. Visual & UX Enhancements (Without Breaking Current UI)

### A. Spatial Player Layout (The "Virtual Felt")
Currently, players are listed in a vertical column (`PlayerList.tsx` / `ActionTracker.tsx`).
*   **The Upgrade:** Transform the left/center of the screen into an elliptical or semi-circular arrangement of player pods.
*   **Why?** It visually establishes **Position** (UTG, Cutoff, Button). Position is a critical feature for our ML model. Seeing who acts first visually is much faster than reading a list.
*   **UI Implementation:** Keep the dark glass-morphism cards, but arrange them around a central `Board` component.

### B. Action & Turn Indicators (The "Clock Ring")
*   **The Upgrade:** Instead of just highlighting the active player's box, implement a glowing, pulsing "Active Ring" (like Discord's timer ring) around their avatar/name.
*   **Visual Detail:** Use our tactical Gold/Emerald colors. When it's a player's turn, the ring pulses.

### C. Visual Chip Movement & Pot Accumulation
*   **The Upgrade:** When you input a `Call` or `Raise`, do not just instantly change the text numbers. Add a micro-animation (0.3s) of a chip stack sliding from the player pod into the central pot.
*   **Side Pots:** Visually split the main pot text into physical-looking distinct "zones" on the board when an All-in occurs, just like Poker Night makes side-pots extremely obvious.

### D. The Dealer & Blind Pucks
*   **The Upgrade:** Prominent, draggable/rotating tokens for `[ D ]` (Dealer), `[ SB ]` (Small Blind), and `[ BB ]` (Big Blind). 
*   **Operator Logic:** At the start of a hand, the tokens automatically rotate. If the physical game skipped a blind, you can drag the `[ D ]` token to correct the state instantly.

---

## 3. Business Logic & Operator Workflows

Since *you* are inputting everything, the system needs to handle the messy reality of live poker.

### A. Mid-Session Player Lifecycle
In live games, people go to the bathroom, bust out, or join late.
*   **Sit Out / Sit In:** Add a `[Pause]` button on a player's pod. This greys them out and skips them for the current hand without losing their stack or stats.
*   **Player Left Table:** A `[Leave]` action that removes them from the active ring but finalizes their database session stats.
*   **Add Player Mid-Game:** A `[+]` empty seat pod that allows you to instantly insert a new player, assign their stack, and seed them with "Table Average" ML stats (solving the Cold Start problem).

### B. "Frictionless" Operator Inputs
*   **Smart Numpad:** When you click "Raise", instead of just a text box, show a tactical Numpad overlaid on the screen with physical chip denominations (e.g., +$5, +$25, +$100) alongside the Pot-math buttons (1/2 Pot, Full Pot).
*   **Blind Adjustments:** A quick-access menu in the top header to increase the blinds (e.g., moving from 10/20 to 25/50) without restarting the session.

### C. The "Undo" Safety Net
*   **The Upgrade:** In Discord, if you misclick, you're stuck. Since you are operating for the whole table, a misclick ruins the ML data. 
*   **Logic:** Implement a global `[ Undo Last Action ]` button (Ctrl+Z shortcut) that rolls back the Zustand state and the Backend Action log by exactly one step.

---

## 4. ML Integration Strategy

How these UX changes improve the AI:
1.  **Positional Tracking:** By forcing a spatial layout and tracking the Dealer button accurately, the `LiveGameState` can easily calculate `is_in_position_relative_to_aggressor`.
2.  **Accurate VPIP:** The "Sit Out" functionality ensures we don't penalize a player's VPIP (making them look like a tight Nit) just because they went to grab a drink.
3.  **Visual Confidence:** We will place the AI's "Bluff Probability" gauge directly underneath the central pot. When a player makes a massive overbet, a radar-like scan animation sweeps the board before flashing the Prediction.

---

## 5. Execution Phasing

*   **Phase 1:** **State Engine Updates:** Add "Sit Out" and "Leave Table" states to the backend `GameState` and `process_action` logic.
*   **Phase 2:** **Spatial Redesign:** Refactor `ActionTracker.tsx` into a `VirtualTable.tsx` with elliptical layout and rotating Dealer pucks.
*   **Phase 3:** **Micro-Animations:** Add Framer Motion (or pure CSS) for chip sliding and active-turn pulsing rings.
*   **Phase 4:** **Operator Tools:** Implement the Undo stack and the physical-chip smart Numpad.