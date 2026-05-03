# Texas Hold’em Table Workflow Specification (Dealer-Assisted Tracker)

This document defines the complete, real-world, rule-accurate workflow for a Texas Hold’em poker table tracking system. The system acts as a dealer-assisted tracking tool, meaning it strictly enforces rules, flow, and state transitions, while relying on manual inputs for card reveals and winner declarations.

---

## SECTION 1: TABLE STRUCTURE

### Number of Players
* The table accommodates **2 to 10 players**.

### Positional Roles
* **Dealer Button (The Button):** A marker indicating the theoretical dealer. The button moves clockwise one position after each hand.
* **Small Blind (SB):** The player immediately clockwise from the Dealer Button. Forced to post a predetermined small bet before cards are dealt.
* **Big Blind (BB):** The player immediately clockwise from the Small Blind. Forced to post a predetermined large bet (usually twice the SB) before cards are dealt.

*(Note: In a heads-up game (2 players), the Dealer Button posts the Small Blind and acts first pre-flop, while the other player posts the Big Blind).*

### Turn Order
* Action always proceeds **clockwise** around the table.

### Player States
* **Active:** The player is currently involved in the hand and is eligible to win the pot.
* **Folded:** The player has surrendered their cards and any claim to the pot. They take no further part in the current hand.
* **All-In:** The player has committed all their remaining chips to the pot. They remain eligible to win the pot (or a portion of it) but cannot take any further betting actions.
* **Sitting Out:** The player is temporarily away from the table, receives no cards, and posts no blinds.

---

## SECTION 2: GAME FLOW (STRICT STATE MACHINE)

The system must strictly enforce the following sequence for every hand:

### 1. Hand Start
* The Dealer Button moves to the next active player.
* Player states are reset (folded and all-in flags cleared).

### 2. Blinds Posting
* The SB and BB amounts are automatically deducted from the respective players' stacks and added to the pot.

### 3. Hole Cards Distribution
* The dealer manually deals 2 private cards to each active player.
* *System interaction:* The system records that cards have been dealt (specific cards may be inputted now or later, depending on visibility).

### 4. Pre-Flop Betting Round
* **First to act:** The player immediately clockwise from the Big Blind (Under the Gun).
* **Allowed actions:** Fold, Call (match the BB), Raise, All-In.
* **Ends when:** All active players have acted AND all bets are equalized (or all but one player has folded).

### 5. Flop Reveal
* **Rules:** Exactly 3 community cards are revealed simultaneously.
* *System interaction:* Dealer manually inputs the 3 Flop cards.

### 6. Flop Betting Round
* **First to act:** The first active player clockwise from the Dealer Button.
* **Allowed actions:** Check (if no bet is faced), Bet, Fold, Call, Raise, All-In.
* **Ends when:** All active players have acted AND bets are equalized.

### 7. Turn Reveal
* **Rules:** Exactly 1 community card is revealed.
* *System interaction:* Dealer manually inputs the Turn card.

### 8. Turn Betting Round
* **First to act:** The first active player clockwise from the Dealer Button.
* Same action and completion rules as the Flop.

### 9. River Reveal
* **Rules:** Exactly 1 community card is revealed.
* *System interaction:* Dealer manually inputs the River card.

### 10. River Betting Round
* **First to act:** The first active player clockwise from the Dealer Button.
* Same action and completion rules as the Flop/Turn.

### 11. Showdown
* Occurs after the River betting round is complete and at least 2 players remain active (or if all remaining players are all-in prior to the River).
* Players reveal their hole cards to determine the winner.

### 12. Pot Distribution
* The pot (and any side pots) is awarded to the winning player(s).
* *System interaction:* Dealer inputs the winner(s).

### 13. Hand End → Next Hand
* Stacks are finalized.
* The system transitions back to Step 1.

---

## SECTION 3: BETTING RULES

### Valid Actions
* **Fold:** Discard hand. The player is marked as *folded*. Allowed when facing a bet/raise.
* **Check:** Pass the action without betting. Allowed only if no previous player has bet in the current round (except for the BB pre-flop if there are no raises).
* **Call:** Match the current highest outstanding bet. Allowed when facing a bet/raise.
* **Bet:** Place the first wager of the current betting round (post-flop).
* **Raise:** Increase the size of the current outstanding bet. Allowed when facing a bet.
* **All-In:** Bet all remaining chips in the player's stack. Allowed at any time the player can act.

### Round Completion Criteria
A betting round strictly ends when:
1. All active, non-all-in players have acted at least once in the round.
2. All active, non-all-in players have contributed an equal amount of chips to the pot for that round.
3. *Alternative:* If all but one player folds, the hand ends immediately, and the pot is awarded to the remaining player.

### Constraints
* A *folded* player cannot act again in the current hand.
* An *all-in* player cannot take further actions in the current hand.
* **Minimum Raise Rule (No-Limit):** A raise must be at least the size of the previous bet or raise in the same round. (e.g., If Player A bets 10, Player B must raise to at least 20. The raise amount is 10). If a player goes all-in for less than a legal raise, it does not reopen the betting for players who have already acted, unless a full raise is completed.

---

## SECTION 4: ALL-IN BEHAVIOR (CRITICAL)

### Player Status
* When a player goes all-in, they remain eligible for the main pot (and any side pots they contributed to) up to the amount of their total wager.
* They are bypassed for all subsequent action requests.

### Global All-In Scenario
* If, at any point, all remaining active players are all-in (or if one player is all-in and the only other active player calls), **no further betting rounds occur.**
* The system must bypass any remaining betting phases and proceed directly toward the Showdown sequence.

### Community Card Reveal in Global All-In
* Even with no betting, the remaining community cards must still be dealt.
* *System interaction:* The system prompts the dealer to manually input the remaining community cards sequentially (e.g., if all-in on the flop, system prompts for Turn card, then River card). The dealer may also choose to input them all at once if the physical deal has already concluded.

---

## SECTION 5: COMMUNITY CARDS (MANUAL INPUT MODEL)

### Input Rules
* Cards must be inputted strictly according to the phase sequence:
  * **Flop:** Exactly 3 cards together.
  * **Turn:** Exactly 1 card.
  * **River:** Exactly 1 card.

### Card Constraints
* **No Duplicates:** A card cannot be inputted if it has already been recorded as a hole card or a previous community card in the current hand.
* **Order Enforcement:** The system must not allow the Turn card to be inputted before the Flop, nor the River before the Turn.

### System Responsibilities
* The system must strictly validate card uniqueness upon every entry.
* The system must permanently store the revealed community cards as part of the hand's historical record.

---

## SECTION 6: SHOWDOWN LOGIC (CUSTOM FOR THIS SYSTEM)

Because this system relies on dealer input rather than auto-evaluating a digital deck, the Showdown phase follows a specific manual workflow:

### 1. Active Player Query
* The system identifies all players who reached the showdown (active, non-folded).
* The system prompts the dealer:
  * Which player(s) choose to **SHOW** their cards?
  * Which player(s) choose to **MUCK** (concede without showing)?

### 2. Card Recording
* For every player marked as "SHOW," the system prompts the dealer to input their exactly 2 hole cards.
* Validation applies (no duplicates with community cards or other shown hole cards).

### 3. Winner Declaration
* The system does *not* automatically calculate the best 5-card hand.
* The system prompts the dealer: **"Who is the winner?"**
* The dealer manually selects the winning player(s) from the list of active showdown players.

### 4. Pot Distribution
* The system must allow the dealer to select **multiple winners** to accommodate split pots.
* If side pots exist, the system should prompt for the winner of each specific pot.

---

## SECTION 7: DATA CAPTURE FOR ANALYTICS (VERY IMPORTANT)

To support future analysis and machine learning, the system must exhaustively log the following data points for every hand:

### Pre-Hand Data
* List of players and their seat positions.
* Dealer button position.
* Starting stack sizes for all players.

### Action Log (Per Round)
* Chronological list of every action taken.
* For each action:
  * Player name/ID.
  * Action type (Fold, Check, Call, Bet, Raise, All-In).
  * Amount of the action.
  * Pot size at the exact moment of the action.
  * The amount the player needed to call at the exact moment of the action.

### Card Data
* All revealed community cards (Flop, Turn, River) with timestamps of when they were revealed relative to the betting rounds.

### Showdown & Resolution Data
* List of players who reached showdown.
* Which players showed cards.
* The exact hole cards shown by those players.
* Which players mucked.
* The declared Winner(s).
* The final amount won by the winner(s).
* Ending stack sizes for all players.

### All-In Events
* Exact record of who went all-in.
* The specific betting round and sequence step where the all-in occurred.

---

## SECTION 8: BLUFF ANALYSIS SUPPORT

The data capture defined above is specifically structured to support advanced bluff detection and behavioral modeling. The system must ensure the data can answer the following queries for future ML pipelines:

### Key Tracked Behaviors
* **Aggressive Non-Showdown Winners:** Track players who frequently bet or raise heavily and win the pot because all opponents fold (winning without showing cards).
* **Weak Showdowns:** Track players who exhibit strong betting patterns (raising pre-flop, betting flop/turn) but are forced to show weak hole cards at showdown.
* **Bluff Frequencies:** By comparing aggressive betting lines against the actual cards shown at showdown, the system builds a profile of how often a player's bets correlate with mathematical hand strength versus "air."

### Stored Metadata
* Historical betting patterns categorized by player.
* Ratios of hands won at showdown vs. hands won via opponent folds.
* Correlation between bet sizing and revealed hand strength.

---

## SECTION 9: VALIDATION RULES

The system acts as a rigid referee. It must block any input that violates the following constraints:
* **No Skipping Phases:** A betting round cannot be skipped unless a global all-in triggers a phase bypass.
* **No Early Reveals:** Community cards cannot be inputted while a betting round is still active and awaiting player actions.
* **Strict Turn Order:** Action inputs must be attributed to the correct player whose turn it currently is.
* **Dead Action Blocks:** The system must reject any attempt to input a bet or raise if all remaining players are all-in.
* **Deck Integrity:** The system must reject the entry of any card (hole or community) that has already been registered in the current hand.

---

## SECTION 10: REALISM REQUIREMENTS

The system must mimic the exact flow of a casino-level Texas Hold'em table:
* **Dealer Control:** The dealer (user of the software) acts as the physical dealer, controlling the flow of cards and resolving the pot.
* **Player Autonomy:** The players dictate the betting action. The system merely records and validates it.
* **Rule Enforcement:** The system prevents dealer errors (e.g., dealing the turn before flop betting is done, miscalculating pot sizes, or allowing an out-of-turn action).
* **Frictionless Tracking:** The UI for inputting actions and cards must be streamlined to keep pace with a live game without slowing down the physical action at the table.
