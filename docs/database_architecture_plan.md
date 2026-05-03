# 🚀 PokerSense AI: Database Architecture & Setup Plan

## 1. Objective
To establish a multi-tenant, ML-ready database architecture using PostgreSQL. This plan addresses three critical requirements:
1.  **Production Flow:** A fast, robust backend (FastAPI) interacting with a cloud database (Supabase/Neon).
2.  **ML Flexibility:** Using Postgres `JSONB` columns to solve the "Cold Start" problem and allow dynamic feature injection for the XGBoost pipeline without rigid schema migrations.
3.  **Developer Experience (AI-Assisted):** Integrating a PostgreSQL Model Context Protocol (MCP) server so AI coding assistants (like Gemini/Claude) can directly query and manage the database schema during development.

---

## 2. Infrastructure & Technology Choices

### A. The Production Database: PostgreSQL (Supabase/Neon)
*   **Why:** Free tier available, highly robust, and natively supports `JSONB` which gives us the schema-less flexibility of NoSQL (MongoDB) while maintaining the relational security needed for user authentication.

### B. The AI Developer Tool: Postgres MCP Server
*   **Why:** You mentioned wanting an MCP server for easy version edits. By configuring the standard [PostgreSQL MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres), your AI assistants will gain direct, real-time read/write access to your database schema.
*   **How it works:** The AI can run SQL commands (e.g., `SELECT * FROM opponents`, `ALTER TABLE`) directly from the chat interface, drastically speeding up future ML feature additions. The FastAPI app remains the primary access point for the actual application.

---

## 3. High-Level Schema Design

### Table 1: `users` (Authentication & Security)
Handles logging into the system.
*   `user_id` (UUID, Primary Key)
*   `email` (String)

### Table 2: `opponents` (Multi-Tenant Isolation)
Ensures your recorded data for a player named "John" does not collide with your friend's data for a player named "John".
*   `opponent_id` (UUID, Primary Key)
*   `user_id` (UUID, Foreign Key -> `users.user_id`)
*   `player_name` (String)

### Table 3: `opponent_stats` (The ML Feeder & NoSQL Hybrid)
This is where the ML data lives. The rigid columns track necessary SQL relations, while the `JSONB` column handles the evolving ML parameters.
*   `opponent_id` (UUID, Foreign Key -> `opponents.opponent_id`)
*   `hands_played` (Int)
*   **`dynamic_features` (JSONB):** This payload acts like a NoSQL document.
    *   *Initial Keys:* `vpip_count`, `pfr_count`, `aggression_ip`, `aggression_oop`, `strict_bluff_showdowns`.
    *   *Future-Proofing:* As your ML pipeline in `PLAN.md` evolves, you can instantly add keys like `river_overbet_freq` to this JSON without writing any database migration scripts.

---

## 4. Behavioral & Logic Workflows

### A. The "Cold Start" Resolution (Table-Averaged Baseline)
When the AI encounters a new player (`hands_played = 0`):
1.  **Query:** The backend fetches the `dynamic_features` of all *known* players currently sitting at the active table.
2.  **Average:** It calculates the average for critical stats (e.g., table's average `aggression_ip`).
3.  **Initialize:** It inserts a new row for the new player, seeding their `dynamic_features` JSON with this table average.
4.  **Result:** The XGBoost model has immediate, logical baseline features to predict bluffs on Hand #1.

### B. Showdown Truth (Strict Hand Strength)
1.  **Definition:** At showdown, the backend checks the absolute mathematical strength of a player's hand. If it is below a strict threshold (e.g., High Card or weak pair) BUT the player took aggressive action.
2.  **Action:** The system increments the `strict_bluff_showdowns` counter inside their `dynamic_features` JSON document.

---

## 5. Hybrid DB Strategy

### Development vs Production
To ensure seamless development without network latency or DNS issues, the system employs a hybrid database strategy:
- **Development** → SQLite (fast, local, no network issues).
- **Production** → PostgreSQL (Supabase).

### Architecture Compatibility
- **JSON over JSONB:** We use SQLAlchemy's generic `JSON` type instead of Postgres-specific `JSONB`. In SQLite, this is stored seamlessly as text, while PostgreSQL automatically leverages it as JSON/JSONB.
- **Migration:** Transitioning from development to production requires zero schema changes. The environment dictates the engine.

### Tradeoffs
- **SQLite:** Lacks native indexing for JSON fields.
- **PostgreSQL:** Provides full performance, including JSONB indexing and concurrency.

**Migration Note:** "Once development stabilizes, switching to Supabase requires only updating the DATABASE_URL. No schema changes are required due to SQLAlchemy abstraction."

---

## 6. Game Intelligence Layer

The Game Intelligence Layer bridges the gap between raw poker gameplay and the Machine Learning data pipeline. It orchestrates the flow of game events into actionable statistics without burdening the core API routing.

### A. How Gameplay Actions Update Stats
During an active game session (`GameSession`), each player action (e.g., `FOLD`, `CALL`, `RAISE`, `ALL_IN`) is recorded.
*   **VPIP & PFR:** If a player calls or raises pre-flop, the system flags their `vpip_this_hand` as `True`. If they raise pre-flop, `pfr_this_hand` is flagged `True`.
*   **Aggression:** Raises and all-ins increment aggression counters (`aggression_ip` / `aggression_oop`) based on the player's position.
*   **Live Injection:** These metrics immediately update the `dynamic_features` JSON document via the repository layer (`StatsRepository`), ensuring the opponent's behavior profile is continuously evolving in real-time.

### B. How Showdown Contributes to Bluff Detection
Showdowns provide objective ground-truth regarding a player's behavior versus their actual mathematical strength.
1.  **Hand Evaluation:** When hole cards are revealed, the system evaluates the best 5-card combination using `HandEvaluator.evaluate_7_cards`.
2.  **Detection Trigger:** If the computed `HandRank` is exceptionally weak (e.g., High Card or weak Pair), the system checks the player's most recent actions.
3.  **Bluff Affirmation:** If the weak hand is paired with aggressive action (`RAISE` or `ALL_IN`) on the final street, the system definitively identifies this as a bluff and increments the `strict_bluff_showdowns` counter in the database.

### C. Deriving ML Features from Gameplay Data
The computed metrics surfaced by the API are mathematical derivatives of the `dynamic_features` JSON:
*   `vpip_percentage` = `vpip_count` / `hands_played`
*   `pfr_percentage` = `pfr_count` / `hands_played`
*   `aggression_score` = (`aggression_ip` + `aggression_oop`) / `hands_played`
*   `bluff_frequency` = `strict_bluff_showdowns` / `hands_played`
This clean derivation keeps the raw event data flexible for the XGBoost models while ensuring the user interface receives easily digestible percentages.

---

## 7. Next Steps for Implementation
1.  **Provision Database:** Create a free Supabase or Neon PostgreSQL instance.
2.  **Configure MCP:** Install the Postgres MCP Server locally and provide it with the database connection URI so the AI assistant can connect to it.
3.  **Schema Creation:** Ask the AI (via MCP) to execute the SQL `CREATE TABLE` scripts to build the schema above.
4.  **FastAPI Integration:** Update `packages/domain/stats_repository.py` to connect to PostgreSQL and begin writing/reading the JSONB data.